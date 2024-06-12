import shlex

import jinja2

ENV = None


def jinja_env() -> jinja2.Environment:
    global ENV
    if ENV is None:
        ENV = jinja2.Environment(loader=jinja2.PackageLoader("brezn", "templates"))
        ENV.filters["quote"] = shlex.quote
    return ENV


def render_template(path: str, *args, **kwargs):
    """Render a jinja2 template from the templates folder."""
    return jinja_env().get_template(path).render(*args, **kwargs)
