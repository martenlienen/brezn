import hashlib
import os
import shutil
import subprocess
from pathlib import Path

import gitignorant as gi


def enumerate_files(root: Path, rules: list[gi.Rule]):
    """Enumerate all files under `root` according to (inverse) gitignore rules."""

    assert root.is_dir()
    dirs: list[tuple[Path, bool | None]] = [(root, None)]
    files = []
    i = 0
    while i < len(dirs):
        dir, parent_match = dirs[i]
        for name in dir.iterdir():
            f = dir / name
            relpath = f.relative_to(root)
            is_dir = f.is_dir()
            match = gi._find_match(rules, str(relpath), is_dir=is_dir)
            if match is False:
                # Explicitly rejected
                continue
            elif is_dir:
                # If a parent got explicitly added, bequeath it to the children
                dirs.append((f, match or parent_match))
            elif match is True or parent_match is True:
                # If the file or any of its parents got explicitly added
                files.append(f)
        i += 1
    return files


def hash_files(files: list[Path]) -> str:
    """Compute a single hash for a bunch of files."""

    m = hashlib.blake2b(digest_size=12)
    if len(files) > 0:
        cmd = ["sha256sum"] + (sorted(files))
        proc = subprocess.run(cmd, stdout=subprocess.PIPE, check=True)
        if proc.returncode != 0:
            raise RuntimeError("Could not hash files")
        m.update(proc.stdout)
    return m.hexdigest()


def copy_files(from_: Path, to: Path, files: list[Path]):
    """Copy `files` and their parent directories from `from_` to `to`."""

    dirs = set([p for f in files for p in f.parents])
    to_copy = set(files) | dirs

    def ignore(path, contents):
        p = Path(path)
        return [f for f in contents if p / f not in to_copy]

    shutil.copytree(from_, to, ignore=ignore, dirs_exist_ok=True)


def symlink_files(from_: Path, to: Path, files: list[Path]):
    """Symlink `files` from `from`_ to `to`."""

    for f in files:
        link = to / f
        target = (from_ / f).resolve()

        if not target.exists():
            # If a symlink target does not exist, just create it as a directory. I think
            # this will be less confusing and frustrating than creating symlinks to
            # non-existent targets and in my experience symlink targets have always been
            # directories anyway.
            target.mkdir(parents=True, exist_ok=True)

        link.symlink_to(target)


def write_script(path: Path, script: str):
    """Write a script to a path and make it executable."""

    path.write_text(script)
    mode = os.stat(path).st_mode
    # Set all executable bits
    path.chmod(mode | 0o111)
