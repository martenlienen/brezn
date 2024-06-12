# brezn :pretzel:

`brezn` runs your experiments regardless of which configuration or logging framework you
use. It takes an arbitrary command and runs it in an isolated environment on your own
computer or a cluster such as slurm.

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
dir = ".brezn"
# Rules in the .gitignore format about which files should be included in the saved environments
files = [
  "brezn/**/*.py",
  "config/**/*.yaml",
]
# Rules to select files that should be symlinked into the saved environment. These files are not
# considered in checking if a change occurred and a new environment has to be created.
symlinks = [
  "data/",
]
```

### Run a command

`brezn run` creates a new copy of your code and then runs the command you provide from
there. Note that the working directory will be the directory where brezn copied the
environment to.

```sh
brezn run ./train.py overrides=True
```
