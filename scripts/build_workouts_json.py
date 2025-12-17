import json, re, time
import requests

BASE = "https://darebee.com/workout.html"
OUT  = "workouts.json"
STEP = 15  # matches the site paging  [oai_citation:2‡Darebee](https://darebee.com/workout.html)

WORKOUT_RE = re.compile(r'href="(/workouts/[^"]+\.html)"')

def fetch(url: str) -> str:
    r = requests.get(url, timeout=30, headers={"User-Agent": "github-pages-random-darebee/1.0"})
    r.raise_for_status()
    return r.text

def main():
    html0 = fetch(BASE)

    # The page shows "Results 1 - 15 of 2629"  [oai_citation:3‡Darebee](https://darebee.com/workout.html)
    m = re.search(r"Results\s+\d+\s*-\s*\d+\s+of\s+(\d+)", html0)
    total = int(m.group(1)) if m else 3000  # fallback

    starts = list(range(0, total, STEP))

    urls = []
    seen = set()

    def add_from_html(html: str):
        for href in WORKOUT_RE.findall(html):
            full = "https://darebee.com" + href
            if full not in seen:
                seen.add(full)
                urls.append(full)

    add_from_html(html0)

    for s in starts[1:]:
        page = f"{BASE}?start={s}"
        html = fetch(page)
        add_from_html(html)
        time.sleep(0.2)  # be polite

    with open(OUT, "w", encoding="utf-8") as f:
        json.dump({"count": len(urls), "urls": urls}, f, indent=2)

    print(f"Wrote {len(urls)} workouts to {OUT}")

if __name__ == "__main__":
    main()
