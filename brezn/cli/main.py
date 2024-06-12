import logging

import click

from ..config import Config, find_pyproject_toml

# Since this module controls the application, we get the root logger here instead of the
# one specified by __name__
log = logging.getLogger("brezn")


@click.group(context_settings={"help_option_names": ["-h", "--help"]})
@click.option(
    "-v",
    "--verbose",
    count=True,
    help="Increase verbosity level. Can be passed multiple times.",
)
@click.pass_context
def main(ctx, verbose):
    """brezn launches experiments."""

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
@click.option("-l", "--launcher", default="local", type=click.Choice(["local"]))
@click.argument("command", nargs=-1)
@click.pass_context
def run(ctx, command, launcher):
    """Run COMMAND in batch-mode (in the background)."""

    from .run import run_cli

    run_cli(ctx.obj, command, launcher)


@main.command(context_settings={"ignore_unknown_options": True})
@click.option("-l", "--launcher", default="local", type=click.Choice(["local"]))
@click.argument("command", nargs=-1)
@click.pass_context
def rin(ctx, command, launcher):
    """Run COMMAND interactively."""

    from .run import rin_cli

    rin_cli(ctx.obj, command, launcher)
