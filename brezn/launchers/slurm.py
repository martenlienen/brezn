import logging
import subprocess

import attrs

from ..config import Config
from ..files import write_script
from ..job import Job, JobDir
from ..templates import render_template
from .launcher import JobLauncher, LauncherConfig

log = logging.getLogger(__name__)


@attrs.frozen
class SlurmJob:
    dir: JobDir


@attrs.frozen
class SlurmLauncherConfig(LauncherConfig):
    sbatch: dict[str, str]

    def instantiate(self):
        return SlurmLauncher(sbatch_options=self.sbatch)


class SlurmLauncher(JobLauncher[SlurmJob]):
    """Launch jobs on a Slurm cluster."""

    def __init__(self, *, sbatch_options: dict[str, str]):
        super().__init__()

        self.sbatch_options = sbatch_options

    def prepare_interactive_job(self, config: Config, job: Job) -> SlurmJob:
        job_dir = job.create_basic_job_dir(config)

        srun_script = render_template(
            "slurm/srun.j2.sh",
            srun_options=self.sbatch_options,
            command_script=job_dir.command_script,
        )
        write_script(job_dir.path / "srun.sh", srun_script)

        return SlurmJob(job_dir)

    def run_job(self, job: SlurmJob):
        """Launch a job with interactive srun."""
        subprocess.run(job.dir.path / "srun.sh")

    def prepare_job(self, config: Config, job: Job) -> SlurmJob:
        job_dir = job.create_basic_job_dir(config)

        sbatch_script = render_template(
            "slurm/sbatch.j2.sh",
            sbatch_options=self.sbatch_options,
            command_script=job_dir.command_script,
        )
        write_script(job_dir.path / "sbatch.sh", sbatch_script)

        return SlurmJob(job_dir)

    def launch_job(self, job: SlurmJob):
        """Submit a job with sbatch."""
        subprocess.run(("sbatch", job.dir.path / "sbatch.sh"))
