import logging
from typing import Literal

from ..config import Config
from ..environment import Environment
from ..job import Job
from ..launchers.local import LocalLauncher

log = logging.getLogger(__name__)


def run_cli(config: Config, command: tuple[str], launcher_type: Literal["local"]):
    """Implementation of the run CLI command."""

    if launcher_type == "local":
        launcher = LocalLauncher()
    else:
        raise ValueError(f"Unknown launcher: {launcher_type}")

    log.info("Preparing environment")
    env = Environment.prepare(config)

    log.info("Preparing job")
    job = Job(env, command)
    prepared_job = launcher.prepare_job(config, job)

    log.info("Launching job")
    launcher.launch_job(prepared_job)


def rin_cli(config: Config, command: tuple[str], launcher_type: Literal["local"]):
    """Implementation of the rin CLI command."""

    if launcher_type == "local":
        launcher = LocalLauncher()
    else:
        raise ValueError(f"Unknown launcher: {launcher_type}")

    log.info("Preparing environment")
    env = Environment.prepare(config)

    log.info("Preparing job")
    job = Job(env, command)
    prepared_job = launcher.prepare_interactive_job(config, job)

    log.info("Running job")
    launcher.run_job(prepared_job)
