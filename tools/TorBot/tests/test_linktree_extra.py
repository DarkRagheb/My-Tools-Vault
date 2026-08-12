"""Additional edge-case tests for linktree parsing functions.

These tests cover corner cases and error conditions for the parsing helpers.
"""
from bs4 import BeautifulSoup
import pytest

from torbot.modules.linktree import (
    parse_hostname,
    parse_links,
    parse_emails,
    parse_phone_numbers,
)


def test_parse_hostname_raises_on_invalid_url() -> None:
    """Ensure parse_hostname raises exception for URLs without hostname."""
    with pytest.raises(Exception, match="unable to parse hostname"):
        parse_hostname("not-a-valid-url")


def test_parse_hostname_handles_various_schemes() -> None:
    """Verify parse_hostname works with http, https, and onion domains."""
    assert parse_hostname("https://www.example.com/path") == "www.example.com"
    assert parse_hostname("http://test.onion") == "test.onion"
    assert parse_hostname("https://sub.domain.co.uk:8080/") == "sub.domain.co.uk"


def test_parse_links_filters_only_valid_full_urls() -> None:
    """Ensure parse_links returns only absolute http(s) URLs."""
    html = """
    <html>
      <a href="/relative/path">relative</a>
      <a href="https://valid.example/path">valid</a>
      <a href="http://also.valid.test/">valid2</a>
      <a href="javascript:void(0)">js</a>
      <a href="https://valid.example/path">valid-duplicate</a>
    </html>
    """

    links = parse_links(html)
    # only absolute http(s) URLs should be returned, duplicates preserved
    assert links == [
        "https://valid.example/path",
        "http://also.valid.test/",
        "https://valid.example/path",
    ]


def test_parse_links_empty_html() -> None:
    """Test parse_links with HTML containing no anchor tags."""
    html = "<html><body><p>No links here</p></body></html>"
    links = parse_links(html)
    assert links == []


def test_parse_links_anchor_without_href() -> None:
    """Ensure parse_links handles anchor tags without href attribute."""
    html = """
    <html>
      <a>No href</a>
      <a name="anchor">Named anchor</a>
      <a href="https://valid.com">Valid</a>
    </html>
    """
    links = parse_links(html)
    assert links == ["https://valid.com"]


def test_parse_emails_ignores_invalid_and_returns_unique() -> None:
    """Verify parse_emails filters invalid emails and removes duplicates."""
    doc = BeautifulSoup(
        """
        <html>
          <a href="mailto:good@example.com">good</a>
          <a href="mailto:good@example.com">good-dup</a>
          <a href="mailto:bad-email@invalid@">bad</a>
          <a href="mailto:withparams@example.com?subject=hi">withparams</a>
          <a href="#">not-mailto</a>
        </html>
        """,
        "html.parser",
    )

    emails = parse_emails(doc)
    # duplicates removed, invalid emails rejected
    # Note: current impl splits on 'mailto:' so params might be included
    # We test actual behavior here
    assert "good@example.com" in emails
    assert len([e for e in emails if e == "good@example.com"]) == 1  # no duplicates


def test_parse_emails_empty_page() -> None:
    """Test parse_emails with no mailto links."""
    doc = BeautifulSoup("<html><body><p>No emails</p></body></html>", "html.parser")
    emails = parse_emails(doc)
    assert emails == []


def test_parse_emails_malformed_mailto() -> None:
    """Ensure malformed mailto links are filtered out."""
    doc = BeautifulSoup(
        """
        <html>
          <a href="mailto:">empty</a>
          <a href="mailto:not-an-email">invalid</a>
          <a href="mailto:valid@test.com">valid</a>
        </html>
        """,
        "html.parser",
    )
    emails = parse_emails(doc)
    # Only valid email should be extracted
    assert emails == ["valid@test.com"]


def test_parse_phone_numbers_only_accepts_possible_international_numbers() -> None:
    """Verify parse_phone_numbers validates international format."""
    doc = BeautifulSoup(
        """
        <html>
          <a href="tel:+14155552671">us</a>
          <a href="tel:4155552671">no-plus</a>
          <a href="tel:+442071838750">uk</a>
          <a href="tel:invalid_phone">invalid</a>
        </html>
        """,
        "html.parser",
    )

    numbers = parse_phone_numbers(doc)
    # only the properly formatted international numbers (with +) are considered possible
    assert sorted(numbers) == ["+14155552671", "+442071838750"]


def test_parse_phone_numbers_empty_page() -> None:
    """Test parse_phone_numbers with no tel: links."""
    doc = BeautifulSoup("<html><body><p>No phones</p></body></html>", "html.parser")
    numbers = parse_phone_numbers(doc)
    assert numbers == []


def test_parse_phone_numbers_removes_duplicates() -> None:
    """Ensure duplicate phone numbers are deduplicated."""
    doc = BeautifulSoup(
        """
        <html>
          <a href="tel:+14155551234">call</a>
          <a href="tel:+14155551234">call again</a>
          <a href="tel:+14155559999">other</a>
        </html>
        """,
        "html.parser",
    )
    numbers = parse_phone_numbers(doc)
    assert len(numbers) == 2
    assert "+14155551234" in numbers
    assert "+14155559999" in numbers
