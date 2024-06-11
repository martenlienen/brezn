import logging
import shlex
from datetime import datetime
from pathlib import Path
from typing import Iterable

import attrs
import cattrs
import toml

from .config import Config
from .environment import Environment
from .files import write_script

log = logging.getLogger(__name__)


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


@attrs.frozen
class JobDir:
    # Path of the job directory
    path: Path

    # Path of the command script relative to the job directory
    command_script: Path


@attrs.frozen
class Job:
    """A job is a command to be run in a specific environment."""

    env: Environment
    command: tuple[str]

    @property
    def shell_command(self):
        """A formatted shell command to be run in the environment directory."""
        return shlex.join(self.command)

    def create_basic_job_dir(self, config: Config) -> JobDir:
        now = datetime.now()
        command_hash = hash_messages(self.command, hash_length=6)
        job_name = now.strftime("%Y%m%d-%H%M%S") + "-" + command_hash
        job_dir = config.jobs_dir / job_name
        log.debug("Job directory: %s", job_dir)
        job_dir.mkdir(exist_ok=True, parents=True)

        # Symlink the environment into the job directory
        (job_dir / "env").symlink_to(self.env.path.relative_to(job_dir, walk_up=True))

        config_path = job_dir / "brezn.toml"
        with config_path.open("w") as f:
            toml.dump(cattrs.unstructure(config), f)

        script_name = "command.sh"
        self.write_job_script(job_dir, script_name=script_name)

        return JobDir(job_dir, Path(script_name))

    def write_job_script(self, job_dir: Path, *, script_name: str):
        """Write a script that executes the command in the environment."""

        script = f"""#!/bin/bash

# Move into the environment
script_dir="$(cd "$(dirname "${{BASH_SOURCE[0]}}")" > /dev/null && pwd)"
cd "${{script_dir}}/env"

# Run the user-specified command
{self.shell_command}
"""
        write_script(job_dir / script_name, script)
