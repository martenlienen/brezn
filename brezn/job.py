import attrs

from .environment import Environment


@attrs.frozen
class Job:
    """A job is a command to be run in a specific environment."""

    env: Environment
    command: tuple[str]
