from dataclasses import dataclass
from pathlib import Path

import toml


@dataclass
class Config:
    @staticmethod
    def from_pyproject_toml(file: Path):
        pyproject = toml.load(file)
        brezn_table = pyproject.get("tool", {}).get("brezn", {})

        return Config(
            project_root=file.parent,
            env_dir=Path(brezn_table.get("env_dir", ".brezn")),
            files=brezn_table.get("files", []),
            symlinks=brezn_table.get("symlinks", []),
        )

    project_root: Path
    env_dir: Path
    files: list[str]
    symlinks: list[str]


def find_pyproject_toml():
    dir = Path.cwd().resolve()

    for root in [dir] + list(dir.parents):
        pp_toml = root / "pyproject.toml"
        if pp_toml.is_file():
            return pp_toml
