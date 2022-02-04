"""
Utility functions used in multiple test files.
"""
import random
import uuid
from typing import Tuple

from django.conf import settings
from django.urls import reverse
from django.utils.text import slugify

from mentions.views import view_names
from tests.models import MentionableTestModel
from tests.util import viewname


def get_id_and_slug() -> Tuple[int, str]:
    """Create a random id and slug."""
    _id = random.randint(1, 1_000_000)
    slug = slugify(random_str())
    return _id, slug


def create_mentionable_object(content: str = ""):
    """Create and return an instance of MentionableTestModel."""
    pk, slug = get_id_and_slug()
    return MentionableTestModel.objects.create(pk=pk, slug=slug, content=content)


def get_url_for_slug(slug):
    """Return the absolute URL for the target slug on our domain."""
    return f"https://{settings.DOMAIN_NAME}{_get_urlpath_for_slug(slug)}"


def _get_urlpath_for_slug(slug: str) -> str:
    """Return the relative URL for the target slug."""
    return reverse(viewname.with_target_object_view, args=[slug])


def get_simple_urlpath():
    """Return relative URL for a simple page with no associated models."""
    return reverse(viewname.with_no_mentionable_object)


def endpoint_submit_webmention() -> str:  #
    """Return relative URL for our root webmention endpoint."""
    return reverse(view_names.webmention_api_incoming)


def endpoint_get_webmentions() -> str:
    """Return relative URL for our webmention /get endpoint."""
    return reverse(view_names.webmention_api_get_for_object)


def endpoint_submit_webmention_absolute() -> str:
    """Return absolute URL for our root webmention endpoint on our domain."""
    return f"https://{settings.DOMAIN_NAME}{endpoint_submit_webmention()}"


def random_domain() -> str:
    """Return a randomised domain name."""
    return f"example-url-{random_str()}.org"


def random_url() -> str:
    """Generate a random URL."""
    scheme = random.choice(["http", "https"])
    subdomain = random.choice(["", "", f"{random_str()}."])
    domain = random_domain()
    port = random.choice(([""] * 5) + [":8000"])
    path = "/".join([random_str() for _ in range(random.randint(0, 2))])
    path = (f"/{path}" if path else "") + random.choice(["", "/"])

    return f"{scheme}://{subdomain}{domain}{port}{path}"


def random_str(length: int = 5) -> str:
    """Generate a short string of random characters."""
    return uuid.uuid4().hex[:length]
