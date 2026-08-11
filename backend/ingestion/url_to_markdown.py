import ipaddress
import os
import socket
from urllib.parse import urlparse

import httpx
import trafilatura

MAX_REDIRECTS = 3
MAX_BYTES = 10 * 1024 * 1024  # 10 MB
TIMEOUT_SECONDS = 15
ALLOWED_SCHEMES = {"http", "https"}


class UnsafeUrlError(ValueError):
    """Raised when a URL fails SSRF-safety validation."""


def _assert_public_host(hostname: str) -> None:
    """Resolve a hostname and reject it if any address is private/loopback/reserved.

    This is the core SSRF guard: without it, a pasted URL could point at
    localhost, a cloud metadata endpoint (169.254.169.254), or an internal
    service, and the server would happily fetch it.
    """
    try:
        addr_infos = socket.getaddrinfo(hostname, None)
    except socket.gaierror as exc:
        raise UnsafeUrlError(f"Could not resolve host: {hostname}") from exc

    for family, _, _, _, sockaddr in addr_infos:
        ip_str = sockaddr[0]
        ip = ipaddress.ip_address(ip_str)

        if (
            ip.is_private
            or ip.is_loopback
            or ip.is_link_local
            or ip.is_reserved
            or ip.is_multicast
            or ip.is_unspecified
        ):
            raise UnsafeUrlError(f"Refusing to fetch non-public address: {ip_str}")


def _assert_safe_url(url: str) -> str:
    parsed = urlparse(url)

    if parsed.scheme not in ALLOWED_SCHEMES:
        raise UnsafeUrlError(f"Unsupported URL scheme: {parsed.scheme!r}")

    if not parsed.hostname:
        raise UnsafeUrlError("URL has no hostname")

    _assert_public_host(parsed.hostname)

    return url


def fetch_url_safely(url: str) -> str:
    """Fetch a URL's HTML, validating it (and any redirect targets) are public
    web addresses. Returns raw HTML.
    """
    current_url = _assert_safe_url(url)

    with httpx.Client(follow_redirects=False, timeout=TIMEOUT_SECONDS) as client:
        for _ in range(MAX_REDIRECTS + 1):
            response = client.get(current_url, headers={"User-Agent": "LoktBot/1.0"})

            if response.is_redirect:
                next_url = str(response.next_request.url)
                current_url = _assert_safe_url(next_url)
                continue

            response.raise_for_status()

            content_length = len(response.content)
            if content_length > MAX_BYTES:
                raise UnsafeUrlError(f"Response too large: {content_length} bytes")

            return response.text

    raise UnsafeUrlError("Too many redirects")


def render_with_headless_browser(url: str) -> str:
    """Fully render a JS-driven page (e.g. a React/Next.js site) and return
    the resulting HTML.

    Only called as a fallback when a plain HTTP fetch yields no extractable
    content — booting a browser is much slower than a raw GET, so most
    (server-rendered) pages never pay this cost.
    """
    from playwright.sync_api import sync_playwright

    render_timeout_ms = 30_000

    with sync_playwright() as p:
        browser = p.chromium.launch()
        try:
            page = browser.new_page(user_agent="LoktBot/1.0")
            # "networkidle" is unreliable on sites with continuous background
            # traffic (analytics beacons, etc.) — it can hang until timeout
            # even once the actual content has long since rendered. Instead,
            # wait for the initial load then give client-side rendering a
            # fixed window to finish painting.
            page.goto(url, wait_until="load", timeout=render_timeout_ms)
            page.wait_for_timeout(8000)
            return page.content()
        finally:
            browser.close()


def _extract_markdown(html: str) -> str | None:
    return trafilatura.extract(
        html,
        output_format="markdown",
        include_links=False,
        include_images=False,
        favor_recall=True,  # prefer keeping real content over trimming noise
    )


def _fetch_with_scraperapi(url: str) -> str:
    """Fetch a URL through ScraperAPI with JS rendering, bypassing bot detection."""
    with httpx.Client(timeout=60) as client:
        response = client.get(
            "http://api.scraperapi.com",
            params={"api_key": os.getenv("SCRAPERAPI_KEY"), "url": url},
        )
        response.raise_for_status()
        return response.text


def convert_url(url: str, output_dir: str) -> str:
    """Fetch a privacy-policy page and extract its main content as Markdown.

    Uses a readability-style extractor (trafilatura) to strip navigation,
    footers, and cookie banners, keeping heading structure intact. When
    SCRAPERAPI_KEY is set, routes through ScraperAPI (residential IPs + JS
    rendering) to bypass bot detection on sites like Facebook. Falls back to
    a direct httpx fetch + headless browser otherwise.
    """
    from pathlib import Path

    _assert_safe_url(url)

    if os.getenv("SCRAPERAPI_KEY"):
        html = _fetch_with_scraperapi(url)
        markdown_content = _extract_markdown(html)
    else:
        html = fetch_url_safely(url)
        markdown_content = _extract_markdown(html)

        if not markdown_content or not markdown_content.strip():
            _assert_safe_url(url)
            rendered_html = render_with_headless_browser(url)
            markdown_content = _extract_markdown(rendered_html)

    if not markdown_content or not markdown_content.strip():
        raise ValueError(f"Could not extract readable content from {url}")

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    slug = urlparse(url).netloc.replace(".", "_") or "page"
    markdown_file = output_path / f"{slug}.md"
    markdown_file.write_text(markdown_content, encoding="utf-8")

    return str(markdown_file)
