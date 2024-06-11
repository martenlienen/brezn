import logging

from ..config import Config
from ..environment import Environment
from ..job import Job
from ..launchers.local import LocalLauncher

log = logging.getLogger(__name__)


def run_cli(config: Config, command: tuple[str]):
    """Implementation of the run CLI command."""

    launcher = LocalLauncher()

    log.info("Preparing environment")
    env = Environment.prepare(config)

    log.info("Preparing job")
    job = Job(env, command)
    prepared_job = launcher.prepare_job(config, job)

    log.info("Running job")
    launcher.launch_job(prepared_job)
