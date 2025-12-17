import json, re, time
import requests
from collections import defaultdict

BASE = "https://darebee.com"
STEP = 15

WORKOUT_RE = re.compile(r'href="(/workouts/[^"]+\.html)"')
RESULTS_RE = re.compile(r"Results\s+\d+\s*-\s*\d+\s+of\s+(\d+)", re.I)

# Keep expanding this list as you discover more options on Darebee.
FACETS = {
  "type": {
    "strength":  f"{BASE}/workout/types/strength.html",
    "cardio":    f"{BASE}/workout/types/cardio.html",
    "metcon":    f"{BASE}/workout/types/metcon.html",
    "hiit":      f"{BASE}/workout/types/hiit.html",
    "combat":    f"{BASE}/workout/types/combat.html",
    "stretching":f"{BASE}/workout/types/stretching.html",
    "yoga":      f"{BASE}/workout/types/yoga.html",
    "wellness":  f"{BASE}/workout/types/wellness.html",
  },
  "focus": {
    "full-body": f"{BASE}/workout/focus/full-body.html",
    "upper-body":f"{BASE}/workout/focus/upper-body.html",
    "lower-body":f"{BASE}/workout/focus/lower-body.html",
    "abs":       f"{BASE}/workout/focus/abs.html",
  },
  "difficulty": {
    "light":     f"{BASE}/workout/difficulty/light.html",
    "easy":      f"{BASE}/workout/difficulty/easy.html",
    "normal":    f"{BASE}/workout/difficulty/normal.html",
    "hard":      f"{BASE}/workout/difficulty/hard.html",
    "advanced":  f"{BASE}/workout/difficulty/advanced.html",
  },
  "tools": {
    "dumbbells": f"{BASE}/workout/tools/dumbbells.html",
    "pull-up-bar": f"{BASE}/workout/tools/pull-up-bar.html",
    "kettlebells": f"{BASE}/workout/tools/kettlebells.html",
    "barbell":   f"{BASE}/workout/tools/barbell.html",
    "swiss-ball":f"{BASE}/workout/tools/swiss-ball.html",
    "weapons":   f"{BASE}/workout/tools/weapons.html",
    "other":     f"{BASE}/workout/tools/other.html",
  },
  "specialty": {
    "seated":    f"{BASE}/workout/specialty/seated.html",
    "office-friendly": f"{BASE}/workout/specialty/office-friendly.html",
  },
  "equipment": {
    "no":        f"{BASE}/workout/equipment/no.html",
    "yes":       f"{BASE}/workout/equipment/yes.html",
  }
}

def fetch(url: str) -> str:
    r = requests.get(url, timeout=40, headers={"User-Agent":"gh-pages-darebee-filter/1.0"})
    r.raise_for_status()
    return r.text

def extract_workouts(html: str):
    return [BASE + href for href in WORKOUT_RE.findall(html)]

def total_results(html: str):
    m = RESULTS_RE.search(html)
    return int(m.group(1)) if m else None

def scrape_listing(list_url: str):
    html0 = fetch(list_url)
    total = total_results(html0)
    urls = extract_workouts(html0)
    seen = set(urls)

    # paginate
    if total:
        for start in range(STEP, total, STEP):
            html = fetch(f"{list_url}?start={start}")
            for u in extract_workouts(html):
                if u not in seen:
                    seen.add(u); urls.append(u)
            time.sleep(0.15)
    else:
        # fallback: stop when no new URLs appear
        for i in range(1, 400):
            html = fetch(f"{list_url}?start={i*STEP}")
            before = len(seen)
            for u in extract_workouts(html):
                if u not in seen:
                    seen.add(u); urls.append(u)
            if len(seen) == before:
                break
            time.sleep(0.15)

    return urls

def main():
    # load your existing all-urls list
    with open("workouts.json","r",encoding="utf-8") as f:
        data = json.load(f)
    all_urls = data if isinstance(data, list) else data["urls"]
    all_set = set(all_urls)

    meta = {u: {"type":[], "focus":[], "difficulty":[], "tools":[], "specialty":[], "equipment":[]} for u in all_urls}

    for facet, options in FACETS.items():
        for key, list_url in options.items():
            print("Scraping", facet, key, list_url)
            urls = scrape_listing(list_url)
            for u in urls:
                if u in all_set:
                    meta[u][facet].append(key)

    with open("meta.json","w",encoding="utf-8") as f:
        json.dump(meta, f, indent=2)

    with open("facets.json","w",encoding="utf-8") as f:
        json.dump(FACETS, f, indent=2)

if __name__ == "__main__":
    main()