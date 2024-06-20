from typing import Type

import cattrs

from ..config import Config
from .launcher import JobLauncher, LauncherConfig


def get_launcher(config: Config) -> JobLauncher:
    launcher = config.launcher
    type: Type[LauncherConfig]
    if launcher == "local":
        from ..launchers.local import LocalLauncherConfig

        type = LocalLauncherConfig
    elif launcher == "slurm":
        from ..launchers.slurm import SlurmLauncherConfig

        type = SlurmLauncherConfig
    else:
        raise ValueError(f"Unknown launcher: {type}")

    return cattrs.structure(config.launchers.get(launcher, {}), type).instantiate()
