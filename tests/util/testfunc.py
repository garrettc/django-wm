"""
Utility functions used in multiple test files.
"""
import random
import uuid
from typing import Optional, Tuple

from django.db import models
from django.urls import reverse
from django.utils.text import slugify

from mentions import options
from mentions.models import Webmention
from mentions.models.mixins import IncomingMentionType
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


def create_webmention(
    source_url: Optional[str] = None,
    target_url: Optional[str] = None,
    post_type: Optional[IncomingMentionType] = None,
    sent_by: Optional[str] = None,
    approved: bool = True,
    validated: bool = True,
    quote: Optional[str] = None,
) -> Webmention:
    return Webmention.objects.create(
        source_url=source_url or random_url(),
        target_url=target_url or random_url(),
        post_type=post_type.name.lower() if post_type else None,
        sent_by=sent_by or random_url(),
        approved=approved,
        validated=validated,
        quote=quote,
    )


def get_absolute_url_for_object(obj: models.Model = None):
    if obj is None:
        obj = create_mentionable_object(content=random_str())

    return _absolute_url(obj.get_absolute_url())


def get_simple_url(absolute: bool = False):
    """Return relative URL for a simple page with no associated models."""
    path = reverse(viewname.no_object_view)
    if absolute:
        return _absolute_url(path)
    else:
        return path


def _absolute_url(path):
    return f"{options.base_url()}{path}"


def endpoint_submit_webmention() -> str:
    """Return relative URL for our root webmention endpoint."""
    return reverse(view_names.webmention_api_incoming)


def endpoint_get_webmentions() -> str:
    """Return relative URL for our webmention /get endpoint."""
    return reverse(view_names.webmention_api_get_for_object)


def endpoint_submit_webmention_absolute() -> str:
    """Return absolute URL for our root webmention endpoint on our domain."""
    return f"{options.base_url()}{endpoint_submit_webmention()}"


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
