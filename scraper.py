import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import os
import time
import re
import json

start_urls = [
    "https://en.wikipedia.org/wiki/Python_(programming_language)",
    "https://en.wikipedia.org/wiki/Artificial_intelligence",
    "https://en.wikipedia.org/wiki/Machine_learning",
    "https://en.wikipedia.org/wiki/Computer_science",
    "https://en.wikipedia.org/wiki/Data_science",
    "https://www.bbc.com/news",
    "https://www.youm7.com/",
    "https://www.reuters.com",
    "https://stackoverflow.com/questions",
    "https://www.nytimes.com/",
]

max_pages = 1000
max_per_site = 100
folder_name = "pages"
os.makedirs(folder_name, exist_ok=True)

headers = {"User-Agent": "Khaled/5.0"}

used = {}


def make_name(url):
    p = urlparse(url)
    name = p.netloc + p.path
    name = re.sub(r"[^a-zA-Z0-9]", "_", name).strip("_")[:100]

    if name in used:
        used[name] += 1
        name = f"{name}_{used[name]}"
    else:
        used[name] = 0

    return name + ".txt"


def clean_text(soup):
    for t in soup(["script", "style", "img", "video", "nav", "footer"]):
        t.decompose()
    txt = soup.get_text(" ", strip=True)
    txt = re.sub(r"\s+", " ", txt)
    return txt


def get_all_links(soup, base):
    links = set()
    for a in soup.find_all("a", href=True):
        full = urljoin(base, a["href"])
        p = urlparse(full)
        if p.scheme in ("http", "https"):
            link = p._replace(fragment="").geturl()
            links.add(link)
    return links


def run():
    visited = set()
    queue = list(start_urls)
    files_map = {}
    count = 0
    site_count = {}

    print(f"Start {max_pages}")

    while queue and count < max_pages:
        url = queue.pop(0)

        if url in visited:
            continue
        visited.add(url)

        domain = urlparse(url).netloc
        if site_count.get(domain, 0) >= max_per_site:
            continue

        res = requests.get(url, headers=headers, timeout=10)

        if "text/html" not in res.headers.get("Content-Type", ""):
            continue

        soup = BeautifulSoup(res.text, "lxml")
        text = clean_text(soup)

        if len(text) < 100:
            continue

        name = make_name(url)
        path = os.path.join(folder_name, name)

        with open(path, "w", encoding="utf-8") as f:
            f.write(f"URL: {url}\n\n")
            f.write(text)

        files_map[name] = url
        count += 1
        site_count[domain] = site_count.get(domain, 0) + 1

        print(f"{count}/{max_pages} - {url[:60]}")

        links = get_all_links(soup, url)
        for l in links:
            if l not in visited:
                queue.append(l)

        time.sleep(0.5)

    with open("map.json", "w", encoding="utf-8") as f:
        json.dump(files_map, f, ensure_ascii=False, indent=2)

    print("Done")


if __name__ == "__main__":
    run()
