"""Stage 1: download and parse level-0/1 basketball schedules.

Usage:  python -I scrape.py <cache_dir>      (writes <cache_dir>/games.json)

Season strings and site configs live in config.py.  Downloaded HTML is cached
in <cache_dir>/http (delete it to force a refresh).  Requests are throttled.
"""
import hashlib, html, json, os, re, subprocess, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from config import SEASONS, LEVEL1, UNION  # noqa: E402

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/120.0 Safari/537.36")
_last = [0.0]


def fetch(url, cache, delay=0.5, retries=2):
    """curl-based GET with on-disk cache. Returns (status, text)."""
    os.makedirs(os.path.join(cache, "http"), exist_ok=True)
    key = hashlib.sha1(url.encode()).hexdigest()[:16]
    path = os.path.join(cache, "http", key)
    if os.path.exists(path + ".ok"):
        with open(path, encoding="utf-8", errors="replace") as f:
            return 200, f.read()
    status, text = 0, ""
    for attempt in range(retries + 1):
        wait = delay - (time.time() - _last[0])
        if wait > 0:
            time.sleep(wait)
        r = subprocess.run(["curl", "-sL", "-m", "30", "-A", UA,
                            "-H", "Accept: text/html,application/xhtml+xml,*/*",
                            "-H", "Accept-Language: en-US,en;q=0.9",
                            "-o", path, "-w", "%{http_code}", url],
                           capture_output=True, text=True)
        _last[0] = time.time()
        try:
            status = int(r.stdout.strip() or 0)
        except ValueError:
            status = 0
        text = open(path, encoding="utf-8", errors="replace").read() if os.path.exists(path) else ""
        if status == 200 and text:
            open(path + ".ok", "w").close()
            return status, text
        time.sleep(4 * (attempt + 1))  # 202 = AWS WAF challenge; back off, never solve it
    return status, text


def clean(t):
    t = re.sub(r"<[^>]+>", " ", t)
    return re.sub(r"\s+", " ", html.unescape(t)).strip()


def hrefs(block):
    return [html.unescape(h) for h in re.findall(r'href="([^"#][^"]*)"', block)]


# ---------------- parsers: each yields dicts ----------------

def parse_sidearm(s):
    out = []
    blocks = re.split(r'<li[^>]*class="sidearm-schedule-game ', s)[1:]
    for b in blocks:
        b = b.split('class="sidearm-schedule-game-toggle')[0]
        m = re.search(r'sidearm-schedule-game-opponent-name">(.*?)</div>', b, re.S)
        if not m:
            continue
        inner = m.group(1)
        inner_nr = re.sub(r"<span>\s*(#|No\.)\s*\d+\s*</span>", " ", inner)
        name = clean(inner_nr)
        a = re.search(r'<a[^>]*href="(https?://[^"]+)"', inner)
        vs = re.search(r'sidearm-schedule-game-conference-vs[^>]*>(.*?)</span>', b, re.S)
        loc = re.search(r'sidearm-schedule-game-location">\s*<span>(.*?)</span>', b, re.S)
        conf = "sidearm-schedule-game-conference-conference" in b and re.search(
            r'sidearm-schedule-game-conference-conference[^>]*>\s*<span', b) is not None
        ha = "home" if "sidearm-schedule-home-game" in b[:300] else (
            "away" if "sidearm-schedule-away-game" in b[:300] else (
                "neutral" if "neutral-game" in b[:300] else ""))
        out.append({"raw": name, "oppUrl": a.group(1) if a else "",
                    "site": clean(vs.group(1)) if vs else "", "ha": ha,
                    "location": clean(loc.group(1)) if loc else "",
                    "exhibition": "exhibition" in b[:400].lower() or "(exh" in name.lower(),
                    "conference": conf, "links": hrefs(b)})
    return out


def parse_presto(s):
    """PrestoSports: handles the card, table and 'inner-wrap' schedule templates."""
    out = []
    s = re.sub(r"<(script|style|svg)[^>]*>.*?</\1>", "", s, flags=re.S)
    parts = re.split(r'<(?:div|tr)[^>]*class="([^"]*\bevent-row\b[^"]*)"', s)
    for i in range(1, len(parts), 2):
        cls, r = " " + parts[i] + " ", parts[i + 1]
        r = re.split(r'class="(?:game-leaders|month-title|event-date )', r)[0][:8000]
        m = (re.search(r'class="team-name">(.*?)</span>', r, re.S)
             or re.search(r'event-opponent-name[^"]*">(.*?)</span>\s*</div>', r, re.S)
             or re.search(r'class="team opponent">(.*?)</td>', r, re.S)
             or re.search(r'class="opponent">(.*?)</div>', r, re.S))
        if not m:
            continue
        name = clean(re.sub(r'<span class="event-location-badge[^>]*>.*?</span>', "", m.group(1), flags=re.S))
        badge = re.search(r'event-location-badge[^>]*>(.*?)</span>', r, re.S) or re.search(r'<div class="va">(.*?)</div>', r, re.S)
        locs = [clean(x) for x in re.findall(
            r'class="(?:event-neutralsite[^"]*|event-notes[^"]*|notes|venue[^"]*)"[^>]*>(.*?)</(?:div|td|a)>', r, re.S)]
        ha = "home" if " home " in cls else "away" if " away " in cls else "neutral" if " neutral " in cls else ""
        out.append({"raw": name, "oppUrl": "", "site": clean(badge.group(1)) if badge else "", "ha": ha,
                    "location": " | ".join(x for x in locs if x and x not in ("A", "H", "N")),
                    "exhibition": " exhibition " in cls, "conference": " conf " in cls,
                    "links": hrefs(r)})
    return out


def parse_drupal(s):
    """Union-style Drupal athletics sites (uauwarriors, mccthunder, cbusaints, occambassadors ...)."""
    out = []
    for trc, r in re.findall(r'<tr([^>]*)>(.*?)</tr>', s, re.S):
        r = re.sub(r'<div class="tourn">.*?</div>', "", r, flags=re.S)
        m = re.search(r'<div class="opponent-group">(.*?)(?:<span class="location">|</div>)', r, re.S)
        if not m:
            continue
        opp = clean(m.group(1))
        sm = re.search(r'<span class="site">(.*?)</span>', r, re.S)
        site = clean(sm.group(1)).lower() if sm else ""
        lm = re.search(r'<span class="location">(.*?)</span>', r, re.S) or re.search(r'views-field-field-city[^>]*>(.*?)</td>', r, re.S)
        trc = trc.lower()
        ha = ("home" if site == "vs" or 'class="home' in trc else "away" if site == "at" or 'class="away' in trc
              else "neutral" if "neutral" in trc else "")
        out.append({"raw": opp, "oppUrl": "", "site": site, "ha": ha,
                    "location": clean(lm.group(1)) if lm else "",
                    "exhibition": "exhib" in opp.lower(), "conference": False, "links": hrefs(r)})
    return out


def parse_barclay(s):
    out = []
    i = s.find('id="schedule"')
    seg = s[i:i + 80000] if i >= 0 else ""
    seg = seg.split("Roster")[0]
    for r in re.findall(r"<tr[^>]*>.*?</tr>", seg, re.S):
        tds = re.findall(r"<td[^>]*>(.*?)</td>", r, re.S)
        if len(tds) < 3:
            continue
        loc = clean(tds[2])
        out.append({"raw": clean(tds[1]), "oppUrl": "", "site": "",
                    "ha": "away" if loc.lower().startswith("away") else "home" if "haviland" in loc.lower() else "",
                    "location": loc, "exhibition": "exhib" in clean(tds[3]).lower() if len(tds) > 3 else False,
                    "conference": False, "links": hrefs(r)})
    return out


PARSERS = {"sidearm": parse_sidearm, "presto": parse_presto, "drupal": parse_drupal, "barclay": parse_barclay}


def schedule_urls(sch):
    """Yield (sport, season, url) for a school's configured schedules."""
    base = sch["site"].rstrip("/")
    p = sch["platform"]
    for sport in ("m", "w"):
        if sport in sch.get("noSport", ""):
            continue
        for season in SEASONS:
            if p == "sidearm":
                slug = {"m": "mens-basketball", "w": "womens-basketball"}[sport]
                yield sport, season, f"{base}/sports/{slug}/schedule/{season}"
            elif p == "presto":
                slug = {"m": "mbkb", "w": "wbkb"}[sport]
                yield sport, season, f"{base}/sports/{slug}/{season}/schedule"
            elif p == "drupal":
                slug = {"m": "mens-basketball", "w": "womens-basketball"}[sport]
                yield sport, season, f"{base}/sports/{slug}/schedule"  # season id resolved below
            elif p == "barclay":
                slug = {"m": "mens-basketball", "w": "womens-basketball"}[sport]
                if season == SEASONS[0]:
                    yield sport, season, f"{base}/{slug}/"  # only current season is published
    for extra in sch.get("extraSchedules", []):
        yield extra["sport"], extra["season"], extra["url"]


def scrape_school(sch, cache, log):
    games = []
    for sport, season, url in schedule_urls(sch):
        if sch["platform"] == "drupal" and "?id=" not in url:
            st, s = fetch(url, cache)
            opts = dict((lab.strip(), v) for v, lab in re.findall(r'<option value="(\d+)"[^>]*>([^<]*)', s))
            if season not in opts:
                log.append({"school": sch["name"], "sport": sport, "season": season, "url": url,
                            "status": st, "games": 0, "note": "season not listed in selector"})
                continue
            url = f"{url}?id={opts[season]}"
        st, s = fetch(url, cache)
        title = clean((re.search(r"<title>(.*?)</title>", s, re.S) or [None, ""])[1]) if s else ""
        rows = PARSERS[sch["platform"]](s) if st == 200 else []
        note = ""
        if st != 200:
            note = f"HTTP {st}" + (" (AWS WAF / Cloudflare bot challenge)" if st in (202, 403) else "")
        elif sch["platform"] == "sidearm" and season not in title:
            note = f"page title '{title[:60]}' does not mention {season}; treated as no schedule"
            rows = []
        elif not rows:
            note = "no games found on page"
        log.append({"school": sch["name"], "sport": sport, "season": season, "url": url,
                    "status": st, "games": len(rows), "note": note})
        for r in rows:
            r.update({"school": sch["name"], "sport": sport, "season": season, "url": url})
            games.append(r)
    return games


def main():
    cache = sys.argv[1]
    os.makedirs(cache, exist_ok=True)
    allg, log = [], []
    for sch in [UNION] + LEVEL1:
        if not sch.get("site"):
            log.append({"school": sch["name"], "sport": "", "season": "", "url": "", "status": 0,
                        "games": 0, "note": sch.get("note", "no site configured")})
            continue
        g = scrape_school(sch, cache, log)
        print(f"{sch['name']}: {len(g)} games", file=sys.stderr)
        allg += g
    json.dump({"games": allg, "log": log}, open(os.path.join(cache, "games.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
