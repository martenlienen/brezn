import logging
import shlex
import shutil
import tempfile
from datetime import datetime
from pathlib import Path

import cattrs
import gitignorant as gi
import toml

from ..config import Config
from ..files import copy_files, enumerate_files, hash_files, symlink_files

log = logging.getLogger(__name__)


def collect_files(config: Config) -> list[Path]:
    """Collect all files that should be copied into the environment."""

    project_root = config.project_root
    brezn_dir = config.brezn_dir

    # Parse the rules for which files to copy
    rules = [rule for r in config.files if (rule := gi.try_parse_rule(r)) is not None]
    if (project_root / ".gitignore").is_file():
        gitignore = [
            rule
            for line in (project_root / ".gitignore").read_text().splitlines()
            if (rule := gi.try_parse_rule(line)) is not None
        ]
        # Negate the gitignore rules
        for rule in gitignore:
            rule.negative = not rule.negative
        rules += gitignore
    # Ignore anything in the brezn directory
    brezn_project_dir = None
    if not brezn_dir.is_absolute():
        brezn_project_dir = brezn_dir
    elif brezn_dir.is_relative_to(project_root):
        brezn_project_dir = brezn_dir.relative_to(project_root)
    if brezn_project_dir is not None:
        rules += [gi.Rule(negative=True, content="/" + str(brezn_project_dir))]
    log.debug("File adding rules: %s", rules)
    return enumerate_files(project_root, rules)


def create_environment(config: Config, files: list[Path], symlinks: list[Path]) -> Path:
    """Create a frozen environment with the given files and symlinks."""

    envs_dir = config.envs_dir
    envs_dir.mkdir(exist_ok=True, parents=True)

    files_hash = hash_files(files)
    env_dir = envs_dir / files_hash
    if not env_dir.is_dir():
        # Copy the source code into a temporary directory first, so that another
        # concurrently running instance of brezn cannot observe a partially created
        # environment.
        #
        # We create the temporary directory in the same directory, so that it is on the
        # same filesystem and renaming in the end won't have a hidden copy operation.
        tmp_root = Path(tempfile.mkdtemp(dir=envs_dir, prefix="tmp-"))
        try:
            copy_files(config.project_root, tmp_root, files)
            symlink_files(config.project_root, tmp_root, symlinks)

            try:
                tmp_root.rename(env_dir)
            except OSError:
                # A concurrent brezn instance created the environment faster than us.
                # Just delete our environment and pretend nothing happened.
                shutil.rmtree(tmp_root)
        except:
            # If anything went wrong during copying, delete the broken directory
            shutil.rmtree(tmp_root)
            raise
    return env_dir


def prepare_environment(config: Config) -> Path:
    """Prepare a frozen environment."""

    files = collect_files(config)
    log.debug("Files to copy: %s", files)

    # Construct the files to symlink into the environment directory
    symlinks = [Path(s) for s in config.symlinks]
    log.debug("Files to symlink: %s", symlinks)

    # Copy the project files into the environment directory
    env_dir = create_environment(config, files, symlinks)
    log.debug("Environment directory: %s", env_dir)

    return env_dir


def hash_messages(messages: list[str], *, hash_length: int = 12) -> str:
    """Compute a hex-encoded hash string for messages."""

    assert hash_length % 2 == 0
    import hashlib

    # Use half the requested hash length as number of bytes for the digest size, because
    # the digest is in raw bytes and will be twice as long when hex-encoded.
    m = hashlib.blake2b(digest_size=hash_length // 2)
    for message in messages:
        m.update(message.encode("utf-8"))
    return m.hexdigest()


def prepare_job(config: Config, env_dir: Path, command: tuple[str]) -> Path:
    """Prepare a job directory with all related information."""

    now = datetime.now()
    command_hash = hash_messages(command, hash_length=6)
    job_name = now.strftime("%Y%m%d-%H%M%S") + "-" + command_hash
    job_dir = config.jobs_dir / job_name
    log.debug("Job directory: %s", job_dir)
    job_dir.mkdir(exist_ok=True, parents=True)

    # Symlink the environment into the job directory
    (job_dir / "env").symlink_to(env_dir.relative_to(job_dir, walk_up=True))

    config_path = job_dir / "brezn.toml"
    with config_path.open("w") as f:
        toml.dump(cattrs.unstructure(config), f)

    # Store the command to run as a script
    script = f"""#!/bin/bash

# Move into the environment
script_dir="$(cd "$(dirname "${{BASH_SOURCE[0]}}")" > /dev/null && pwd)"
cd "${{script_dir}}/env"

# Run the user-specified command
{shlex.join(command)}
"""
    script_path = job_dir / "script"
    script_path.write_text(script)
    script_path.chmod(0o755)

    return job_dir


def run_job(job_dir: Path):
    """Run the job prepared in the given directory."""

    import subprocess

    subprocess.run(job_dir / "script")


def run_cli(config: Config, command: tuple[str]):
    """Implementation of the run CLI command."""

    log.info("Preparing environment")
    env_dir = prepare_environment(config)

    log.info("Preparing job")
    job_dir = prepare_job(config, env_dir, command)

    log.info("Running job")
    run_job(job_dir)
