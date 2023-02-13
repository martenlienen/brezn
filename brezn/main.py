import click


@click.group(context_settings={"help_option_names": ["-h", "--help"]})
def main():
    """Something layered on top of hydra."""
    pass
