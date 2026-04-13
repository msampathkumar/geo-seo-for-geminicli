#!/usr/bin/env python3

import requests
from requests.adapters import HTTPAdapter
from urllib3.util import Retry
from urllib.parse import quote_plus
import sys
import os
import re
import json
import time
import hashlib

# Common AI crawler user agents for testing
AI_CRAWLERS = {
    "GPTBot": "Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; GPTBot/1.2; +https://openai.com/gptbot)",
    "GeminiBot": "GEO-Audit/1.0 (Gemini CLI)",
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

def fetch_page(url, crawler_name=None, cache_dir=None, force_fresh=False, verify_ssl=True):
    """
    Fetches the content of a given URL with retries for transient errors.
    Supports caching based on URL and time threshold.

    Args:
        url (str): The URL to fetch.
        crawler_name (str, optional): If specified, uses the User-Agent of this crawler.
        cache_dir (str, optional): Directory to store cached pages.
        force_fresh (bool): If True, bypasses cache and fetches fresh content.

    Returns:
        tuple: (status_code, content, headers) or (None, None, None) on error.
    """
    # Check cache first if enabled
    use_cache = False
    cache_file = None
    
    if cache_dir and not force_fresh:
        # Check if it's a local file or Google doc (always fetch fresh)
        is_local = url.startswith("file://") or "localhost" in url or url.startswith("/")
        is_gdoc = "docs.google.com" in url
        
        if not (is_local or is_gdoc):
            use_cache = True
            os.makedirs(cache_dir, exist_ok=True)
            # Create a safe filename from URL
            url_hash = hashlib.md5(url.encode('utf-8')).hexdigest()
            cache_file = os.path.join(cache_dir, f"{url_hash}.json")
            
            if os.path.exists(cache_file):
                file_stat = os.stat(cache_file)
                time_diff = time.time() - file_stat.st_mtime
                if time_diff < 300: # 5 minutes
                    try:
                        with open(cache_file, 'r', encoding='utf-8') as f:
                            cached_data = json.load(f)
                            print(f"Using cached content for {url}", file=sys.stderr)
                            return cached_data.get("status_code"), cached_data.get("content"), cached_data.get("headers")
                    except Exception as e:
                        print(f"Error reading cache: {e}", file=sys.stderr)

    headers = DEFAULT_HEADERS.copy()
    if crawler_name and crawler_name in AI_CRAWLERS:
        headers["User-Agent"] = AI_CRAWLERS[crawler_name]

    # Setup session with retries
    session = requests.Session()
    retry = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[500, 502, 503, 504],
        raise_on_status=False
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)

    try:
        response = session.get(url, headers=headers, timeout=15, allow_redirects=True, verify=verify_ssl)
        response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)

        content = response.text
        response_headers = response.headers

        # Try to decode content if it's not text/html, e.g., JSON
        if 'charset' not in response_headers.get('Content-Type', '').lower():
            try:
                content = response.content.decode('utf-8')
            except UnicodeDecodeError:
                pass # Keep as bytes if decode fails

        # Save to cache if enabled
        if use_cache and cache_file:
            try:
                with open(cache_file, 'w', encoding='utf-8') as f:
                    json.dump({
                        "status_code": response.status_code,
                        "content": content,
                        "headers": dict(response_headers)
                    }, f, indent=2)
            except Exception as e:
                print(f"Error writing cache: {e}", file=sys.stderr)

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

def analyze_page(url, crawler_name=None, cache_dir=None, force_fresh=False, verify_ssl=True):
    """Fetches and analyzes a page, returning key metadata."""
    status_code, content, headers = fetch_page(url, crawler_name, cache_dir, force_fresh, verify_ssl)

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
    import argparse
    
    parser = argparse.ArgumentParser(description="Fetch and analyze a webpage.")
    parser.add_argument("url", help="The URL to fetch.")
    parser.add_argument("crawler", nargs="?", default=None, help="The crawler user-agent to simulate.")
    parser.add_argument("--cache-dir", default=None, help="Directory to store cached pages.")
    parser.add_argument("--fresh", action="store_true", help="Force fresh fetch, bypass cache.")
    parser.add_argument("--no-verify", action="store_true", help="Disable SSL certificate verification.")
    
    args = parser.parse_args()

    page_data = analyze_page(args.url, args.crawler, args.cache_dir, args.fresh, not args.no_verify)

    if page_data:
        print(json.dumps(page_data, indent=2))
    else:
        sys.exit(1)
