#!/usr/bin/env python3

import requests
from urllib.parse import quote_plus
import sys
import os
import re

# Common AI crawler user agents for testing
AI_CRAWLERS = {
    "GPTBot": "Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; GPTBot/1.2; +https://openai.com/gptbot)",
    "GeminiBot": "Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; GeminiBot/1.0; +https://www.anthropic.com/claude-bot)",
    "PerplexityBot": "Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; PerplexityBot/1.0; +https://perplexity.ai/perplexitybot)",
    "GoogleBot": "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)",
    "BingBot": "Mozilla/5.0 (compatible; bingbot/2.0; +http://www.bing.com/bingbot.htm)",
}

DEFAULT_HEADERS = {
    "User-Agent": "GEO-Audit/1.0 (Gemini CLI)",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-User": "?1",
    "Sec-Fetch-Dest": "document",
}

def fetch_page(url, crawler_name=None):
    """
    Fetches the content of a given URL.

    Args:
        url (str): The URL to fetch.
        crawler_name (str, optional): If specified, uses the User-Agent of this crawler.
                                      Defaults to None (uses default headers).

    Returns:
        tuple: (status_code, content, headers) or (None, None, None) on error.
    """
    headers = DEFAULT_HEADERS.copy()
    if crawler_name and crawler_name in AI_CRAWLERS:
        headers["User-Agent"] = AI_CRAWLERS[crawler_name]

    try:
        response = requests.get(url, headers=headers, timeout=15, allow_redirects=True)
        response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)

        content = response.text
        response_headers = response.headers

        # Try to decode content if it's not text/html, e.g., JSON
        if 'charset' not in response_headers.get('Content-Type', '').lower():
            try:
                content = response.content.decode('utf-8')
            except UnicodeDecodeError:
                pass # Keep as bytes if decode fails

        return response.status_code, content, response_headers

    except requests.exceptions.RequestException as e:
        print(f"Error fetching {url}: {e}", file=sys.stderr)
        return None, None, None

def extract_title(html_content):
    """Extracts the title from HTML content."""
    match = re.search(r"<title>(.*?)</title>", html_content, re.IGNORECASE | re.DOTALL)
    if match:
        return match.group(1).strip()
    return None

def extract_meta_description(html_content):
    """Extracts the meta description from HTML content."""
    match = re.search(r'<meta name="description"\s+content="(.*?)">', html_content, re.IGNORECASE | re.DOTALL)
    if match:
        return match.group(1).strip()
    return None

def extract_h1(html_content):
    """Extracts the first H1 tag content from HTML."""
    match = re.search(r'<h1>(.*?)</h1>', html_content, re.IGNORECASE | re.DOTALL)
    if match:
        return match.group(1).strip()
    return None

def analyze_page(url, crawler_name=None):
    """Fetches and analyzes a page, returning key metadata."""
    status_code, content, headers = fetch_page(url, crawler_name)

    if status_code is None:
        return None

    analysis = {
        "url": url,
        "status_code": status_code,
        "title": extract_title(content),
        "h1": extract_h1(content),
        "meta_description": extract_meta_description(content),
        "content_length": len(content) if content else 0,
        "headers": dict(headers),
    }
    return analysis

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python fetch_page.py <url> [crawler_name]")
        sys.exit(1)

    target_url = sys.argv[1]
    crawler = sys.argv[2] if len(sys.argv) > 2 else None

    page_data = analyze_page(target_url, crawler)

    if page_data:
        print(json.dumps(page_data, indent=2))
    else:
        sys.exit(1)
