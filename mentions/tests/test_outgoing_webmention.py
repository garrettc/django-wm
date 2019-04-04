"""
Tests for webmentions that originate on our server, usually pointing somewhere else.
"""
import logging
from dataclasses import dataclass, field

from django.test import TestCase
from django.urls import reverse

import mentions.tests.util.snippets
from mentions.tasks import outgoing_webmentions
from mentions.tests import util
from mentions.tests.models import MentionableTestModel
from mentions.tests.util import constants

log = logging.getLogger(__name__)


@dataclass
class MockResponse:
    url: str
    text: str = None
    headers: dict = field(default_factory=dict)


class OutgoingWebmentionsTests(TestCase):

    def setUp(self):
        self.target_stub_id, self.target_slug = util.get_id_and_slug()

        target = MentionableTestModel.objects.create(
            stub_id=self.target_stub_id,
            slug=self.target_slug,
            allow_incoming_webmentions=True)
        target.save()

    def _get_target_url(self, viewname):
        return reverse(viewname, args=[self.target_slug])

    def _get_absolute_target_url(self, viewname):
        return f'{constants.domain}{self._get_target_url(viewname)}'

    def test_find_links_in_text(self):
        """Ensure that outgoing links are found correctly."""

        outgoing_content = util.get_mentioning_content(
            reverse(constants.view_all_endpoints, args=[self.target_slug]))

        outgoing_links = outgoing_webmentions._find_links_in_text(outgoing_content)
        self.assertEqual(
            outgoing_links,
            [util.url(constants.correct_config,
                      self.target_slug)])

    def test_get_absolute_endpoint_from_response(self):
        """Ensure that any exposed endpoints are found and returned as an absolute url."""
        mock_response = MockResponse(
            url=self._get_absolute_target_url(constants.view_all_endpoints),
            headers={'Link': mentions.tests.util.snippets.HTTP_LINK_ENDPOINT})
        absolute_endpoint_from_http_headers = outgoing_webmentions._get_absolute_endpoint_from_response(
            mock_response)
        self.assertEqual(constants.webmention_api_absolute_url, absolute_endpoint_from_http_headers)

        mock_response.headers = {}
        mock_response.text = mentions.tests.util.snippets.HTML_HEAD_ENDPOINT
        absolute_endpoint_from_html_head = outgoing_webmentions._get_absolute_endpoint_from_response(
            mock_response)
        self.assertEqual(constants.webmention_api_absolute_url, absolute_endpoint_from_html_head)

        mock_response.headers = {}
        mock_response.text = mentions.tests.util.snippets.HTML_BODY_ENDPOINT
        absolute_endpoint_from_html_body = outgoing_webmentions._get_absolute_endpoint_from_response(
            mock_response)
        self.assertEqual(constants.webmention_api_absolute_url, absolute_endpoint_from_html_body)

    def test_get_endpoint_in_http_headers(self):
        """Ensure that endpoints exposed in http header are found correctly."""

        mock_response = MockResponse(
            url=self._get_absolute_target_url(constants.view_all_endpoints),
            headers={'Link': mentions.tests.util.snippets.HTTP_LINK_ENDPOINT})
        endpoint_from_http_headers = outgoing_webmentions._get_endpoint_in_http_headers(
            mock_response)
        self.assertEqual(constants.webmention_api_relative_url, endpoint_from_http_headers)

    def test_get_endpoint_in_html_head(self):
        """Ensure that endpoints exposed in html <head> are found correctly."""

        mock_response = MockResponse(
            url=self._get_absolute_target_url(constants.view_all_endpoints),
            text=mentions.tests.util.snippets.HTML_HEAD_ENDPOINT)
        endpoint_from_html_head = outgoing_webmentions._get_endpoint_in_html(mock_response)
        self.assertEqual(constants.webmention_api_relative_url, endpoint_from_html_head)

    def test_get_endpoint_in_html_body(self):
        """Ensure that endpoints exposed in html <body> are found correctly."""

        mock_response = MockResponse(
            url=self._get_absolute_target_url(constants.view_all_endpoints),
            text=mentions.tests.util.snippets.HTML_BODY_ENDPOINT)
        endpoint_from_html_body = outgoing_webmentions._get_endpoint_in_html(mock_response)
        self.assertEqual(constants.webmention_api_relative_url, endpoint_from_html_body)

    def test_relative_to_absolute_url(self):
        """Ensure that relative urls are correctly converted to absolute"""

        domain = constants.domain
        page_url = f'{domain}/some-url-path'
        response = MockResponse(url=page_url)

        absolute_url_from_root = outgoing_webmentions._relative_to_absolute_url(
            response, '/webmention')
        self.assertEqual(f'{domain}/webmention', absolute_url_from_root)

        absolute_url_from_relative = outgoing_webmentions._relative_to_absolute_url(
            response, 'webmention')
        self.assertEqual(f'{domain}/webmention', absolute_url_from_relative)

        already_absolute_url = outgoing_webmentions._relative_to_absolute_url(
            response, f'{domain}/already_absolute_path')
        self.assertEqual(f'{domain}/already_absolute_path',
                         already_absolute_url)

    # def test_send_webmention(self):
    #     outgoing_stub_id, outgoing_slug = _get_id_and_slug()
    #
    #     outgoing = MentionableTestModel.objects.create(
    #         stub_id=outgoing_stub_id,
    #         slug=outgoing_slug,
    #         enable_outgoing_webmentions=True)
    #     outgoing.save()
    #
    #     source_url = reverse(view_names.all_endpoints, args=[outgoing_slug])
    #     endpoint = endpoints.webmention_api_absolute_url
    #     target_url = self._get_absolute_target_url(view_names.all_endpoints)
    #
    #     success = outgoing_webmentions._send_webmention(
    #         source_url=source_url, endpoint=endpoint, target=target_url)
    #     self.assertTrue(success)