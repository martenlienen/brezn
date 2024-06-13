from pathlib import Path

import attrs
import toml


@attrs.frozen
class Config:
    """Global brezn configuration."""

    project_root: Path
    brezn_dir: Path = Path(".brezn")
    files: list[str] = []
    symlinks: list[str] = []
    launcher: str = "local"

    launcher_configs: dict[str, dict] = {}

    @staticmethod
    def from_pyproject_toml(file: Path, launcher: str):
        pyproject = toml.load(file)
        brezn_table = pyproject.get("tool", {}).get("brezn", {})

        return Config(
            project_root=file.parent,
            brezn_dir=Path(brezn_table.get("dir", ".brezn")),
            files=brezn_table.get("files", []),
            symlinks=brezn_table.get("symlinks", []),
            launcher=launcher or brezn_table.get("launcher", "local"),
            launcher_configs=brezn_table.get("launchers", {}),
        )

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
