import os
from jinja2 import Environment, FileSystemLoader

# Shared Jinja2 environment – single instance used by all generators.
# auto_reload=False prevents filesystem checks on every get_template() call,
# which gives a significant speedup when templates are stable at runtime.
# BytecodeCache is not used here because Jinja2's internal LRU cache (
# cache_size=400 by default) is sufficient for the handful of templates
# in this project.
_template_dir = os.path.join(os.path.dirname(__file__), "templates")

env = Environment(
    loader=FileSystemLoader(_template_dir),
    trim_blocks=True,
    lstrip_blocks=True,
    auto_reload=False,   # Hot spot 1 fix: skip mtime checks on every render
    cache_size=400,      # explicit, same as default – document the intent
)


def render_template_to_lines(template_name: str, context: dict) -> list[str]:
    """Render a Jinja2 template and return non-empty lines.

    Single shared entry-point used by both generate.py and protocols.py
    to avoid creating duplicate Environment objects.
    """
    template = env.get_template(template_name)
    rendered = template.render(**context)
    return [line for line in rendered.splitlines() if line.strip()]
