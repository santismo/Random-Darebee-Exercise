import json, re, time
import requests

BASE = "https://darebee.com"
OUT = "categories.json"

# Add/adjust these however you want.
CATEGORIES = {
  "Strength – Upper Body": "https://darebee.com/workout/types/strength/focus/upper-body.html",
  "Strength – Lower Body": "https://darebee.com/workout/types/strength/focus/lower-body.html",
  "Strength – Abs":       "https://darebee.com/workout/types/strength/focus/abs.html",
  "Strength – Full Body": "https://darebee.com/workout/types/strength/focus/full-body.html",

  "Combat – Upper Body":  "https://darebee.com/workout/types/combat/focus/upper-body.html",
  "Combat – Full Body":   "https://darebee.com/workout/types/combat/focus/full-body.html",
}

WORKOUT_RE = re.compile(r'href="(/workouts/[^"]+\.html)"')
RESULTS_RE = re.compile(r"Results\s+\d+\s*-\s*\d+\s+of\s+(\d+)", re.I)

STEP = 15  # DAREBEE listing pages paginate in 15s (start=15,30,45,...)  [oai_citation:1‡Darebee](https://darebee.com/workout/types/strength/focus/upper-body.html?start=45&utm_source=chatgpt.com)

def fetch(url: str) -> str:
    r = requests.get(url, timeout=30, headers={"User-Agent":"gh-pages-random-darebee/1.0"})
    r.raise_for_status()
    return r.text

def extract_urls(html: str):
    urls = []
    seen = set()
    for href in WORKOUT_RE.findall(html):
        full = BASE + href
        if full not in seen:
            seen.add(full)
            urls.append(full)
    return urls

def get_total(html: str):
    m = RESULTS_RE.search(html)
    return int(m.group(1)) if m else None

def scrape_category(url: str):
    html0 = fetch(url)
    total = get_total(html0)
    urls = extract_urls(html0)

    # paginate if total is known; otherwise, just try a bunch until nothing new appears
    if total is None:
        # fallback: try up to 500 pages
        max_pages = 500
        for i in range(1, max_pages):
            html = fetch(f"{url}?start={i*STEP}")
            got = extract_urls(html)
            before = len(urls)
            for u in got:
                if u not in urls:
                    urls.append(u)
            if len(urls) == before:
                break
            time.sleep(0.2)
    else:
        for start in range(STEP, total, STEP):
            html = fetch(f"{url}?start={start}")
            got = extract_urls(html)
            for u in got:
                if u not in urls:
                    urls.append(u)
            time.sleep(0.2)

    return urls

def main():
    out = {"generated_from": CATEGORIES, "categories": {}}

    for name, url in CATEGORIES.items():
        urls = scrape_category(url)
        out["categories"][name] = {"count": len(urls), "urls": urls}
        print(name, len(urls))

    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)

if __name__ == "__main__":
    main()