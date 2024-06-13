import logging

from ..config import Config
from ..environment import Environment
from ..job import Job
from ..launchers import get_launcher

log = logging.getLogger(__name__)


def run_cli(config: Config, command: tuple[str]):
    """Implementation of the run CLI command."""

    log.info("Instantiating launcher")
    launcher = get_launcher(config)

    log.info("Preparing environment")
    env = Environment.prepare(config)

    log.info("Preparing job")
    job = Job(env, command)
    prepared_job = launcher.prepare_job(config, job)

    log.info("Launching job")
    launcher.launch_job(prepared_job)


def rin_cli(config: Config, command: tuple[str]):
    """Implementation of the rin CLI command."""

    log.info("Instantiating launcher")
    launcher = get_launcher(config)

    log.info("Preparing environment")
    env = Environment.prepare(config)

    log.info("Preparing job")
    job = Job(env, command)
    prepared_job = launcher.prepare_interactive_job(config, job)

    log.info("Running job")
    launcher.run_job(prepared_job)
