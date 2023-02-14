import hashlib
import shutil
import subprocess
from pathlib import Path

import gitignorant as gi


def enumerate_files(root: Path, rules: list[gi.Rule]):
    """Enumerate all files under `root` according to (inverse) gitignore rules."""

    assert root.is_dir()
    dirs = [root]
    files = []
    i = 0
    while i < len(dirs):
        dir = dirs[i]
        for name in dir.iterdir():
            f = dir / name
            relpath = f.relative_to(root)
            match = gi._find_match(rules, str(relpath), is_dir=True)
            if f.is_dir():
                if match is not False:
                    dirs.append(f)
            elif match is True:
                files.append(f)
        i += 1
    return files


def hash_files(files: list[Path]) -> str:
    """Compute a single hash for a bunch of files."""

    cmd = ["sha256sum"] + (sorted(files))
    proc = subprocess.run(cmd, stdout=subprocess.PIPE, check=True)
    if proc.returncode != 0:
        raise RuntimeError("Could not hash files")
    m = hashlib.blake2b(digest_size=12)
    m.update(proc.stdout)
    return m.hexdigest()


def copy_files(from_: Path, to: Path, files: list[Path]):
    """Copy `files` and their parent directories from `from_` to `to`."""

    dirs = set()
    for f in files:
        dirs.update(f.parents)
    ignores = set(files) | dirs

    def ignore(path, contents):
        p = Path(path)
        return [f for f in contents if p / f not in ignores]

    shutil.copytree(from_, to, ignore=ignore)
