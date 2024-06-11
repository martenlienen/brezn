from abc import abstractmethod

from ..config import Config
from ..job import Job


class JobLauncher[T]:
    """A job launcher launches jobs, e.g. locally or on a cluster."""

    @abstractmethod
    def prepare_job(self, config: Config, job: Job) -> T:
        """Prepare a job for launching."""
        pass

    @abstractmethod
    def run_job(self, job: T):
        """Run the job interactively."""
        pass

    @abstractmethod
    def launch_job(self, job: T):
        """Launch the job in batch-mode."""
        pass
