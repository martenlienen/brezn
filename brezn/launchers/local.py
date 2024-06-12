import logging
import subprocess

from ..config import Config
from ..files import write_script
from ..job import Job, JobDir
from ..templates import render_template
from .launcher import JobLauncher

log = logging.getLogger(__name__)


class LocalLauncher(JobLauncher[JobDir]):
    def prepare_interactive_job(self, config: Config, job: Job) -> JobDir:
        return job.create_basic_job_dir(config)

    def run_job(self, job: JobDir):
        # Some commands like htop break if their streams are redirected, so we don't
        # record streams in interactive mode
        subprocess.run(job.path / job.command_script)

    def prepare_job(self, config: Config, job: Job) -> JobDir:
        job_dir = job.create_basic_job_dir(config)

        script = render_template(
            "local/batch.j2.sh", command_script=job_dir.command_script
        )
        write_script(job_dir.path / "batch.sh", script)

        return job_dir

    def launch_job(self, job: JobDir):
        # Just run the job and terminate
        proc = subprocess.Popen(
            job.path / "batch.sh",
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

        # Wait for just 100ms to see if the command fails immediately and print its
        # stdout and stderr for easier debugging
        try:
            returncode = proc.wait(0.1)
            if returncode is not None and returncode > 0:
                log.info("Job failed immediately")
                print((job.path / "stdout.log").read_text())
                print((job.path / "stderr.log").read_text())
        except subprocess.TimeoutExpired:
            pass
