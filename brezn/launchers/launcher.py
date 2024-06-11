from abc import abstractmethod

from ..config import Config
from ..job import Job


class JobLauncher[T]:
    """A job launcher launches jobs, e.g. locally or on a cluster."""

    @abstractmethod
    def prepare_interactive_job(self, config: Config, job: Job) -> T:
        """Prepare an interactive job."""
        pass

    @abstractmethod
    def run_job(self, job: T):
        """Run an interactive job."""
        pass

    @abstractmethod
    def prepare_job(self, config: Config, job: Job) -> T:
        """Prepare a batch-mode job."""
        pass

    @abstractmethod
    def launch_job(self, job: T):
        """Launch a batch-mode job."""
        pass
