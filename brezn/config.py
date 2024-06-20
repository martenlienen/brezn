from pathlib import Path
from typing import Any

import attrs
import cattrs
import toml


@attrs.frozen
class Config:
    """Global brezn configuration."""

    project_root: Path
    brezn_dir: Path = Path(".brezn")
    files: list[str] = []
    symlinks: list[str] = []

    launcher: str = "local"
    launchers: dict[str, Any] = {}

    @staticmethod
    def from_pyproject_toml(file: Path, launcher: str | None):
        pyproject = toml.load(file)
        brezn_table = pyproject.get("tool", {}).get("brezn", {})
        brezn_table.setdefault("project_root", file.parent)
        if launcher is not None:
            brezn_table["launcher"] = launcher

        return cattrs.structure(brezn_table, Config)

    @property
    def envs_dir(self) -> Path:
        return self.brezn_dir / "envs"

    @property
    def jobs_dir(self) -> Path:
        return self.brezn_dir / "jobs"


def find_pyproject_toml():
    dir = Path.cwd().resolve()

    for root in [dir] + list(dir.parents):
        pp_toml = root / "pyproject.toml"
        if pp_toml.is_file():
            return pp_toml
