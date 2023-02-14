import logging
import click

# Since this module controls the application, we get the root logger here instead of the
# one specified by __name__
log = logging.getLogger("brezn")


@click.group(context_settings={"help_option_names": ["-h", "--help"]})
@click.option("-v", "--verbose", count=True)
def main(verbose):
    """Something layered on top of hydra."""

    if verbose >= 1:
        logging.basicConfig()
        log.setLevel(logging.INFO)
        if verbose >= 2:
            log.setLevel(logging.DEBUG)
