import logging
import shlex
import subprocess
from pathlib import Path

import attrs

from ..config import Config
from ..job import Job
from .launcher import JobLauncher

log = logging.getLogger(__name__)


@attrs.frozen
class LocalJob:
    path: Path


def write_job_script(job_dir: Path, command: str):
    # Store the command to run as a script
    script = f"""#!/bin/bash

# Move into the environment
script_dir="$(cd "$(dirname "${{BASH_SOURCE[0]}}")" > /dev/null && pwd)"
cd "${{script_dir}}/env"

# Run the user-specified command
{command}
"""
    script_path = job_dir / "script"
    script_path.write_text(script)
    script_path.chmod(0o755)


class LocalLauncher(JobLauncher[LocalJob]):
    def prepare_interactive_job(self, config: Config, job: Job) -> LocalJob:
        job_dir = job.create_basic_job_dir(config)
        # Some commands like htop break if their streams are redirected, so we don't
        # record streams in interactive mode
        write_job_script(job_dir, f"({shlex.join(job.command)})")

        return LocalJob(job_dir)

    def run_job(self, job: LocalJob):
        # Run the job and wait for it
        subprocess.run(job.path / "script")

    def prepare_job(self, config: Config, job: Job) -> LocalJob:
        job_dir = job.create_basic_job_dir(config)
        # Run the command and record both stdout and stderr transparently
        command = (
            f"({shlex.join(job.command)})"
            ' > >(tee "${script_dir}/stdout.log")'
            ' 2> >(tee "${script_dir}/stderr.log" >&2)'
        )
        write_job_script(job_dir, command)

        return LocalJob(job_dir)

    def launch_job(self, job: LocalJob):
        # Just run the job and terminate
        subprocess.Popen(
            job.path / "script",
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
