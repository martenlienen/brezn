import tomllib
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Config:
    @staticmethod
    def from_pyproject_toml(file: Path):
        with file.open("rb") as f:
            pyproject = tomllib.load(f)
        brezn_table = pyproject.get("tool", {}).get("brezn", {})

        return Config(
            project_root=file.parent,
            env_dir=Path(brezn_table.get("env_dir", ".brezn")),
            files=brezn_table.get("files", []),
        )

    project_root: Path
    env_dir: Path
    files: list[str]


def find_pyproject_toml():
    dir = Path.cwd().resolve()

    for root in [dir] + list(dir.parents):
        pp_toml = root / "pyproject.toml"
        if pp_toml.is_file():
            return pp_toml
