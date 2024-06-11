import logging
import shlex
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Iterable

import attrs
import cattrs
import toml

from ..config import Config
from ..job import Job
from .launcher import JobLauncher

log = logging.getLogger(__name__)


@attrs.frozen
class LocalJob:
    path: Path


def hash_messages(messages: Iterable[str], *, hash_length: int = 12) -> str:
    """Compute a hex-encoded hash string for messages."""

    assert hash_length % 2 == 0
    import hashlib

    # Use half the requested hash length as number of bytes for the digest size, because
    # the digest is in raw bytes and will be twice as long when hex-encoded.
    m = hashlib.blake2b(digest_size=hash_length // 2)
    for message in messages:
        m.update(message.encode("utf-8"))
    return m.hexdigest()


class LocalLauncher(JobLauncher[LocalJob]):
    def prepare_job(self, config: Config, job: Job) -> LocalJob:
        """Prepare a job directory with all related information."""

        now = datetime.now()
        command_hash = hash_messages(job.command, hash_length=6)
        job_name = now.strftime("%Y%m%d-%H%M%S") + "-" + command_hash
        job_dir = config.jobs_dir / job_name
        log.debug("Job directory: %s", job_dir)
        job_dir.mkdir(exist_ok=True, parents=True)

        # Symlink the environment into the job directory
        (job_dir / "env").symlink_to(job.env.path.relative_to(job_dir, walk_up=True))

        config_path = job_dir / "brezn.toml"
        with config_path.open("w") as f:
            toml.dump(cattrs.unstructure(config), f)

        # Store the command to run as a script
        script = f"""#!/bin/bash

# Move into the environment
script_dir="$(cd "$(dirname "${{BASH_SOURCE[0]}}")" > /dev/null && pwd)"
cd "${{script_dir}}/env"

# Run the user-specified command
if [[ $1 == "--interactive" ]]; then
  # Some commands like htop break if their streams are redirected, so we don't
  # record streams in interactive mode
  ({shlex.join(job.command)})
else
  ({shlex.join(job.command)}) > >(tee "${{script_dir}}/stdout.log") 2> >(tee "${{script_dir}}/stderr.log" >&2)
fi
"""
        script_path = job_dir / "script"
        script_path.write_text(script)
        script_path.chmod(0o755)

        return LocalJob(job_dir)

    def run_job(self, job: LocalJob):
        # Run the job and wait for it
        subprocess.run((job.path / "script", "--interactive"))

    def launch_job(self, job: LocalJob):
        # Just run the job and terminate
        subprocess.Popen(
            job.path / "script",
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
