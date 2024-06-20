import logging

import click

from .config import Config, find_pyproject_toml
from .environment import Environment
from .job import Job
from .launchers import get_launcher

# Since this module controls the application, we get the root logger here instead of the
# one specified by __name__
log = logging.getLogger("brezn")


@click.group(context_settings={"help_option_names": ["-h", "--help"]})
@click.option(
    "-l",
    "--launcher",
    default=None,
    type=click.Choice(["local", "slurm"]),
    help="Launcher to use.",
)
@click.option(
    "-v",
    "--verbose",
    count=True,
    help="Increase verbosity level. Can be passed multiple times.",
)
@click.pass_context
def main(ctx, launcher, verbose):
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
    ctx.obj = Config.from_pyproject_toml(pyproject_toml, launcher)
    log.info(f"Configuration {ctx.obj}")


@main.command(context_settings={"ignore_unknown_options": True})
@click.argument("command", nargs=-1)
@click.pass_context
def run(ctx, command) -> None:
    """Run COMMAND in batch-mode (in the background)."""

    config: Config = ctx.obj

    log.info("Instantiating launcher")
    launcher = get_launcher(config)

    log.info("Preparing environment")
    env = Environment.prepare(config)

    log.info("Preparing job")
    job = Job(env, command)
    prepared_job = launcher.prepare_job(config, job)

    log.info("Launching job")
    launcher.launch_job(prepared_job)


@main.command(context_settings={"ignore_unknown_options": True})
@click.argument("command", nargs=-1)
@click.pass_context
def rin(ctx, command) -> None:
    """Run COMMAND interactively."""

    config: Config = ctx.obj

    log.info("Instantiating launcher")
    launcher = get_launcher(config)

    log.info("Preparing environment")
    env = Environment.prepare(config)

    log.info("Preparing job")
    job = Job(env, command)
    prepared_job = launcher.prepare_interactive_job(config, job)

    log.info("Running job")
    launcher.run_job(prepared_job)


@main.command(context_settings={"ignore_unknown_options": True})
@click.argument("config", type=click.Path(readable=True, dir_okay=False))
@click.pass_context
def sweep(ctx, config):
    """Sweep over all commands in the sweep configuration."""

    from .sweep import sweep_cli

    sweep_cli(ctx.obj, config)
