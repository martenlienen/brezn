import logging
import os
import shutil
import tempfile
from pathlib import Path

import click
import gitignorant as gi

from .config import Config, find_pyproject_toml
from .files import copy_files, enumerate_files, hash_files, symlink_files

# Since this module controls the application, we get the root logger here instead of the
# one specified by __name__
log = logging.getLogger("brezn")


@click.group(context_settings={"help_option_names": ["-h", "--help"]})
@click.option("-v", "--verbose", count=True)
@click.option("-c", "--config")
@click.pass_context
def main(ctx, verbose, config):
    """Something layered on top of hydra."""

    if verbose >= 1:
        logging.basicConfig()
        log.setLevel(logging.INFO)
        if verbose >= 2:
            log.setLevel(logging.DEBUG)

    pyproject_toml = find_pyproject_toml()
    if pyproject_toml is None:
        raise click.ClickException("Could not find a pyproject.toml")

    log.info(f"Load configuration from {pyproject_toml}")
    ctx.obj = Config.from_pyproject_toml(pyproject_toml)
    log.info(f"Configuration {ctx.obj}")


@main.command(context_settings={"ignore_unknown_options": True})
@click.argument("file", type=click.Path(exists=True, executable=True, dir_okay=False))
@click.argument("options", nargs=-1)
@click.pass_context
def run(ctx, file, options):
    """Run the provided command after copying the environment."""

    config: Config = ctx.obj
    file = Path(file)

    project_root = config.project_root
    env_dir = config.env_dir
    if not env_dir.is_absolute():
        env_dir = (project_root / config.env_dir).resolve()

    # Parse the rules for which files to copy
    rules = [rule for r in config.files if (rule := gi.try_parse_rule(r)) is not None]
    if (project_root / ".gitignore").is_file():
        gitignore = [
            rule
            for line in (project_root / ".gitignore").read_text().splitlines()
            if (rule := gi.try_parse_rule(line)) is not None
        ]
        # Negate the gitignore rules to make the "add" rules
        for rule in gitignore:
            rule.negative = not rule.negative
        rules += gitignore
    # Ignore anything in the environment directory
    if env_dir.is_relative_to(project_root):
        rules += [
            gi.Rule(negative=True, content="/" + str(env_dir.relative_to(project_root)))
        ]
    files = enumerate_files(project_root, rules)

    # Construct the files to symlink into the environment directory
    symlinks = [Path(s) for s in config.symlinks]

    # Copy the project files into the environment directory
    env_dir.mkdir(exist_ok=True, parents=True)
    files_hash = hash_files(files)
    copy_root = env_dir / files_hash
    if not copy_root.is_dir():
        # Copy the source code into a temporary directory first, so that another
        # concurrently running instance of brezn cannot observe a partially created
        # environment.
        #
        # We create the temporary directory in the same directory, so that it is on the
        # same filesystem and renaming in the end won't have a hidden copy operation.
        tmp_root = Path(tempfile.mkdtemp(dir=env_dir))
        try:
            copy_files(project_root, tmp_root, files)
            symlink_files(project_root, tmp_root, symlinks)

            try:
                tmp_root.rename(copy_root)
            except OSError:
                # A concurrent brezn instance created the environment faster than us.
                # Just delete our environment and pretend nothing happened.
                shutil.rmtree(tmp_root)
        except:
            # If anything went wrong during copying, delete the broken directory
            shutil.rmtree(tmp_root)
            raise

    # Replace the current process to forward stdout, stderr, exit code and anything else
    # to and from the program as best as possible.
    if file.is_relative_to(project_root):
        file = file.relative_to(project_root)

    # Change directory to run the command in the copied directory
    os.chdir(copy_root)

    os.execvp((copy_root / file).absolute(), [file] + list(options))
