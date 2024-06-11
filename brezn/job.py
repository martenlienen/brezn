import logging
from datetime import datetime
from pathlib import Path
from typing import Iterable

import attrs
import cattrs
import toml

from .config import Config
from .environment import Environment

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
class Job:
    """A job is a command to be run in a specific environment."""

    env: Environment
    command: tuple[str]

    def create_basic_job_dir(self, config: Config) -> Path:
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

        return job_dir
