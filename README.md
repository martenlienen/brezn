# brezn :pretzel:

This is my attempt at figuring out what I would like a
[seml](https://github.com/TUM-DAML/seml) equivalent built on top of
[hydra](https://hydra.cc) to look like. In particular, I want to have code isolation, i.e.
making a copy of the code when you run a job, so that you can continue working on your
code while your jobs wait in a SLURM queue.

`brezn` comes with *absolutely no guarantees* regarding stability or backwards
compatibility. You have been warned.

## Installation

You can install `brezn` from pypi (`pip install brezn`) though if you want the latest
version, you better install it straight from the repo.

```sh
pip install git+https://github.com/martenlienen/brezn
```

## Usage

### Configuration

You can configure `brezn` in a separate section of your `pyproject.toml`.

```toml
[tool.brezn]
# Directory that brezn should put its internal files and saved environments into
env_dir = ".brezn"
# Rules in the .gitignore format about which files should be included in the saved environments
files = [
  "brezn/**/*.py",
  "config/**/*.yaml",
]
```

### Run a command

`brezn run` creates a new copy of your code and then runs the command you provide from
there. Note that the working directory will be the directory where you issue `brezn run`.

```sh
brezn run ./train.py overrides=True
```
