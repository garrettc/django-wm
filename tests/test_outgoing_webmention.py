"""
Tests for webmentions that originate on our server, usually pointing somewhere else.
"""
import logging
from unittest.mock import Mock, patch

import requests
from django.conf import settings

from mentions.models import OutgoingWebmentionStatus
from mentions.tasks import handle_pending_webmentions
from mentions.tasks.outgoing import process_outgoing_webmentions, remote
from tests import MockResponse, OptionsTestCase
from tests.util import testfunc

log = logging.getLogger(__name__)


TARGET_DOMAIN = testfunc.random_domain()

OUTGOING_WEBMENTION_HTML = f"""<html>
<head><link rel="webmention" href="/webmention/" /></head>
<body>blah blah 
<a href="https://{TARGET_DOMAIN}/">This is a mentionable link</a> 
blah blah</body></html>
"""

OUTGOING_WEBMENTION_HTML_MULTIPLE_LINKS = f"""<html>
<head><link rel="webmention" href="/webmention/" /></head>
<body>blah blah 
<a href="https://{TARGET_DOMAIN}/">This is a mentionable link</a> 
<a href="https://{TARGET_DOMAIN}/some-article/">This is another mentionable link</a> 
blah blah</body></html>
"""

OUTGOING_WEBMENTION_HTML_NO_LINKS = """<html>
<head><link rel="webmention" href="/webmention/" /></head>
<body>blah blah no links here blah blah</body></html>
"""


def _mock_get_ok(url, headers=None, **kwargs):
    return {
        f"https://{TARGET_DOMAIN}/": MockResponse(
            url,
            text=OUTGOING_WEBMENTION_HTML,
            headers=headers or {},
            status_code=200,
        ),
        f"https://{TARGET_DOMAIN}/some-article/": MockResponse(
            url,
            text=OUTGOING_WEBMENTION_HTML_MULTIPLE_LINKS,
            headers=headers or {},
            status_code=200,
        ),
    }.get(url)


def _mock_post_ok(url, headers=None, **kwargs):
    return {
        f"https://{TARGET_DOMAIN}/webmention/": MockResponse(
            url,
            headers=headers or {},
            status_code=200,
        ),
    }.get(url)


def _mock_post_error(url, headers=None, **kwargs):
    return {
        f"https://{TARGET_DOMAIN}/webmention/": MockResponse(
            url,
            text=OUTGOING_WEBMENTION_HTML,
            headers=headers or {},
            status_code=400,
        ),
    }.get(url)


def _patch_get(ok: bool):
    return patch.object(requests, "get", Mock(side_effect=_mock_get_ok if ok else None))


def _patch_post(ok: bool):
    return patch.object(
        requests, "post", Mock(side_effect=_mock_post_ok if ok else _mock_post_error)
    )


class OutgoingWebmentionsTests(OptionsTestCase):
    """OUTOOING: tests for task `process_outgoing_webmentions`."""

    source_url = f"https://{settings.DOMAIN_NAME}/some-url-path/"

    @_patch_post(ok=True)
    def test_send_webmention(self):
        """_send_webmention should return True with status code when webmention is accepted by server."""

        success, status_code = remote._send_webmention(
            source_urlpath=self.source_url,
            endpoint=f"https://{TARGET_DOMAIN}/webmention/",
            target=f"https://{TARGET_DOMAIN}/",
        )

        self.assertTrue(success)
        self.assertEqual(200, status_code)

    @_patch_post(ok=False)
    def test_send_webmention__with_endpoint_error(self):
        """_send_webmention should return False with status code when webmention is not accepted by server."""

        success, status_code = remote._send_webmention(
            source_urlpath=self.source_url,
            endpoint=f"https://{TARGET_DOMAIN}/webmention/",
            target=f"https://{TARGET_DOMAIN}/",
        )

        self.assertFalse(success)
        self.assertEqual(400, status_code)

    @_patch_post(ok=True)
    @_patch_get(ok=True)
    def test_process_outgoing_webmentions(self):
        """Test the entire process_outgoing_webmentions task with no errors."""
        self.assertEqual(0, OutgoingWebmentionStatus.objects.count())

        successful_submissions = process_outgoing_webmentions(
            self.source_url, OUTGOING_WEBMENTION_HTML
        )

        self.assertEqual(1, successful_submissions)
        self.assertEqual(1, OutgoingWebmentionStatus.objects.count())

        successful_submissions = process_outgoing_webmentions(
            self.source_url, OUTGOING_WEBMENTION_HTML_MULTIPLE_LINKS
        )

        self.assertEqual(2, successful_submissions)
        self.assertEqual(2, OutgoingWebmentionStatus.objects.count())

    # No network requests should be made if links not found in text
    @patch.object(requests, "get", None)
    @patch.object(requests, "post", None)
    def test_process_outgoing_webmentions__with_no_links_found(self):
        """Test the entire process_outgoing_webmentions task with no links in provided text."""
        self.assertEqual(0, OutgoingWebmentionStatus.objects.count())

        successful_webmention_submissions = process_outgoing_webmentions(
            self.source_url, OUTGOING_WEBMENTION_HTML_NO_LINKS
        )

        self.assertEqual(0, successful_webmention_submissions)
        self.assertEqual(0, OutgoingWebmentionStatus.objects.count())

    @_patch_get(ok=True)
    @_patch_post(ok=False)
    def test_process_outgoing_webmentions__with_endpoint_error(self):
        """Test the entire process_outgoing_webmentions task with endpoint error."""

        successful_webmention_submissions = process_outgoing_webmentions(
            self.source_url, OUTGOING_WEBMENTION_HTML
        )

        self.assertEqual(0, successful_webmention_submissions)
        self.assertEqual(1, OutgoingWebmentionStatus.objects.count())

    @_patch_get(ok=True)
    @_patch_post(ok=False)
    def test_process_outgoing_webmentions__recycles_status(self):
        self.enable_celery(False)
        self.set_retry_interval(0)

        # Process links from text to target url.
        process_outgoing_webmentions(self.source_url, OUTGOING_WEBMENTION_HTML)
        status: OutgoingWebmentionStatus = OutgoingWebmentionStatus.objects.first()
        self.assertEqual(status.retry_attempt_count, 1)

        # After failure, retrying process increments retry_attempt_count.
        handle_pending_webmentions()
        status.refresh_from_db()
        self.assertEqual(status.retry_attempt_count, 2)

        # Reprocessing raw text reuses same status instance, resetting its retry tracking.
        process_outgoing_webmentions(self.source_url, OUTGOING_WEBMENTION_HTML)

        self.assertEqual(OutgoingWebmentionStatus.objects.count(), 1)
        self.assertEqual(
            OutgoingWebmentionStatus.objects.first().retry_attempt_count, 1
        )
