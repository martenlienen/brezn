from ..config import Config
from .launcher import JobLauncher


def get_launcher(config: Config) -> JobLauncher:
    type = config.launcher
    if type == "local":
        from ..launchers.local import LocalLauncher

        return LocalLauncher()
    elif type == "slurm":
        from ..launchers.slurm import SlurmLauncher

        return SlurmLauncher(
            sbatch_options=config.launcher_configs.get("slurm", {}).get("sbatch", {})
        )
    else:
        raise ValueError(f"Unknown launcher: {type}")
