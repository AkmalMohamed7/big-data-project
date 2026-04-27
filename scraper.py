import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import os
import time
import re
import hashlib
import json

# ========== Settings ==========
SEED_URLS = [
    "https://en.wikipedia.org/wiki/Python_(programming_language)",
    "https://en.wikipedia.org/wiki/Artificial_intelligence",
    "https://en.wikipedia.org/wiki/Machine_learning",
    "https://en.wikipedia.org/wiki/Computer_science",
    "https://en.wikipedia.org/wiki/Data_science",
    "https://www.bbc.com/news",
    "https://techcrunch.com",
    "https://www.reuters.com",
    "https://stackoverflow.com/questions",
    "https://www.britannica.com",
]

MAX_URLS = 1000
MAX_PER_DOMAIN = 100
OUTPUT_DIR = "crawled_pages"
os.makedirs(OUTPUT_DIR, exist_ok=True)

HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; MyCrawler/1.0)"}

# ========== URL → Filename ==========
used_names = {}


def url_to_filename(url):
    parsed = urlparse(url)
    name = parsed.netloc + parsed.path
    name = re.sub(r"[^a-zA-Z0-9]", "_", name).strip("_")[:100]

    if name in used_names:
        used_names[name] += 1
        name = f"{name}_{used_names[name]}"
    else:
        used_names[name] = 0

    return name + ".txt"


# ========== Get Text Only ==========
def get_text(soup):
    for tag in soup(["script", "style", "img", "video", "nav", "footer"]):
        tag.decompose()
    text = soup.get_text(separator=" ", strip=True)
    text = re.sub(r"\s+", " ", text)
    return text


# ========== Get Links ==========
def get_links(soup, base_url):
    links = set()
    for a_tag in soup.find_all("a", href=True):
        full_url = urljoin(base_url, a_tag["href"])
        parsed = urlparse(full_url)
        if parsed.scheme in ("http", "https"):
            clean = parsed._replace(fragment="").geturl()
            links.add(clean)
    return links


# ========== Main Crawler ==========
def crawl():
    visited = set()
    to_visit = list(SEED_URLS)
    mapping = {}
    saved = 0
    domain_count = {}

    print(f"Start Crawling {MAX_URLS} pages...")

    while to_visit and saved < MAX_URLS:
        url = to_visit.pop(0)

        if url in visited:
            continue
        visited.add(url)

        domain = urlparse(url).netloc
        if domain_count.get(domain, 0) >= MAX_PER_DOMAIN:
            continue

        try:
            response = requests.get(url, headers=HEADERS, timeout=10)

            if "text/html" not in response.headers.get("Content-Type", ""):
                continue

            soup = BeautifulSoup(response.text, "lxml")
            text = get_text(soup)

            if len(text) < 100:
                continue

            filename = url_to_filename(url)
            filepath = os.path.join(OUTPUT_DIR, filename)

            with open(filepath, "w", encoding="utf-8") as f:
                f.write(f"URL: {url}\n\n")
                f.write(text)

            mapping[filename] = url
            saved += 1
            domain_count[domain] = domain_count.get(domain, 0) + 1
            print(
                f"[{saved}/{MAX_URLS}] ({domain_count[domain]}/{MAX_PER_DOMAIN}) {url[:70]}"
            )

            new_links = get_links(soup, url)
            for link in new_links:
                if link not in visited:
                    to_visit.append(link)

            time.sleep(0.5)

        except Exception as e:
            print(f"Error {url[:50]}: {e}")
            continue

    with open("mapping.json", "w", encoding="utf-8") as f:
        json.dump(mapping, f, ensure_ascii=False, indent=2)

    print(f"\nDone! {saved} pages saved in '{OUTPUT_DIR}'")
    print(f"Mapping saved in 'mapping.json'")


# ========== Run ==========
if __name__ == "__main__":
    crawl()
