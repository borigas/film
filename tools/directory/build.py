"""Build schools.json / schools.csv / report.md.

    python -I scrape.py <cache_dir>        # 1. download + parse level-0/1 schedules
    python -I build.py  <cache_dir>        # 2. normalise, Hudl + YouTube lookups, write outputs

<cache_dir> holds downloaded pages (cache_dir/http) so re-runs are cheap; delete it
to refresh.  Outputs are written next to this script.  All network access is via
curl with throttling (see scrape.fetch).
"""
import collections, csv, datetime, difflib, html, json, os, re, sys, urllib.parse

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from config import LEVEL1, UNION, SEASONS  # noqa: E402
from normalize import strip_name, is_dropped  # noqa: E402
from schools_master import S as MASTER, NOTES  # noqa: E402
from scrape import fetch  # noqa: E402

TODAY = datetime.date.today()
ACTIVE_DAYS = 365

# Known dead/duplicate Hudl sites -> preferred slug.
HUDL_AVOID = {"dordtuniversity": "dordtuniv", "MidAmericaNazarene": "mnu", "ebc": "emmauseagles"}
# Manual Hudl decisions (slug, or None for "checked, no site").  Filled in after review.
HUDL_OVERRIDE = {
    # Reviewed 2026-10: the automatic match was wrong, or missed a site whose title differs.
    "Bellevue University": "bellevuebruins",          # 'bellevue' is Bellevue College (WA)
    "Southwestern Adventist University": None,        # only Southwestern University (Georgetown, TX) matched
    "Central College": "centraldutchsports",          # 'Central Dutch Sports', Pella IA ('centralcollegeacademics' also exists)
    "Central Christian College of Kansas": "centralchristian",
    "Oklahoma Christian University": "oc",            # 'oceagles' is the GLVC copy
    "University of Wisconsin-Platteville": "uwplatteville",
    "University of Wisconsin-Stevens Point": "stevenspoint",  # 'wausauhuskies' is the Wausau branch campus
    "University of Health Sciences and Pharmacy in St. Louis": "UHSPathletics",
    "Minnesota State Community and Technical College": "fergusfalls",  # Fergus Falls campus
    "University of Northwestern-St. Paul": "unorthwesterneagles",
    "University of Texas at Tyler": "1500",           # titled 'UT Tyler'
    "University of Dallas": "universityofdallas",
    "Simmons College of Kentucky": None,              # 'simmons' is Simmons University (Boston)
    "University of Nebraska-Lincoln": None,           # only UNK (Kearney) matched
    "University of South Dakota": None,               # only SD Mines matched
    "University of Tulsa": None,                      # only Tulsa clubs matched
    "Webster University": None,                       # only a St. Louis prep network matched
    "Lincoln University": "lincolnbluetigers",        # ambiguous; 'lubluetigers' is the MIAA copy
    "Penn State York": "psuyork",
    "Colorado College": "coloradocollege",            # name is only a state word, so auto-match skips it
    "Park University": "parkathletics",               # 'parkumedia' is the student-media channel
    "Bryant & Stratton College (Buffalo)": "bscnyb",
    "University of Sioux Falls": "usfcougars",
}
# Manual YouTube channel overrides: name -> handle or UC id (or None).
# name -> (handle or UC id or None, why).  Reviewed 2026-10.
YOUTUBE_OVERRIDE = {
    "Spurgeon College": ("@knightsathletics5832", "athletics site spurgeonknights.com links it; channel is titled 'Knights Athletics'"),
    "Coe College": ("@CoeCollegeAthletics", "athletics site kohawkathletics.com"),
    "Central College": ("@CentralAthletics", "athletics site athletics.central.edu"),
    "Central Christian College of Kansas": ("@CCCTigerAthletics", "athletics site ccctigers.com"),
    "Randall University": ("@RUAthletics", "stream links on Ozark Christian's schedule for games at Randall"),
    "University of Minnesota Morris": ("@cougarathletics659", "athletics site morriscougars.com"),
    "Dakota State University": ("@DakotaStateUniversityAthletics", "athletics site dsuathletics.com"),
    "Mayville State University": ("@Comet_Athletics", "athletics site msucomets.com ('Comet Athletics Network'); auto-pick of @msu-northern... was wrong"),
    "Nebraska Wesleyan University": ("@NebraskaWesleyanAthletics", "owner of the YouTube video embedded on nwusports.com"),
    "Mount Marty University": (None, "mountmartyathletics.com links @mountmartysportsnetwork (404) and channel UCp0J-b8xPx4-vHlWGsGKVAg (removed by YouTube)"),
    "Trinity Bible College": (None, "tbclions.com links @trinitybiblecollegelionsat1139, which returns 404"),
    "Andrews University": (None, "aucardinals.com only links a playlist owned by @weareAUSA (student association), not an athletics channel"),
}
# Manual athletics-site URLs for schools whose site is not linked from any schedule.
SITE_OVERRIDE = {}

GENERIC = set("""university college of the at and state community christian bible baptist
institute school technical technology saint st st. adventist wesleyan lutheran
nazarene methodist international national northern southern eastern western central
north south east west mount mt campus""".split())

CONFERENCES = [  # (name, regex)  -- first match wins, so specific leagues precede associations
    ("GPAC", r"Great Plains Athletic Conference|gpacsports\.com"),
    ("KCAC", r"Kansas Collegiate Athletic Conference|kcacsports\.com"),
    ("Heart of America Athletic Conference", r"Heart of America"),
    ("Frontier Conference", r"Frontier Conference|frontierconference"),
    ("North Star Athletic Association", r"North Star Athletic|northstarathletic"),
    ("American Rivers Conference", r"American Rivers Conference|americanriversconference|iowaconference\.com"),
    ("Midwest Christian College Conference", r"Midwest Christian College Conference|mcccsports|\bMCCC\b"),
    ("Red River Athletic Conference", r"Red River Athletic Conference|redriverconference"),
    ("Sooner Athletic Conference", r"Sooner Athletic Conference|sooner-athletic"),
    ("Continental Athletic Conference", r"Continental Athletic Conference"),
    ("Crossroads League", r"Crossroads League"),
    ("American Midwest Conference", r"American Midwest Conference"),
    ("Chicagoland Collegiate Athletic Conference", r"Chicagoland Collegiate"),
    ("Upper Midwest Athletic Conference", r"Upper Midwest Athletic Conference|umacathletics"),
    ("Northern Athletics Collegiate Conference", r"Northern Athletics Collegiate Conference|naccsports"),
    ("Minnesota Intercollegiate Athletic Conference", r"Minnesota Intercollegiate Athletic Conference|miacathletics"),
    ("Northern Sun Intercollegiate Conference", r"Northern Sun Intercollegiate|northernsun\.org"),
    ("MIAA", r"Mid-America Intercollegiate Athletics Association|themiaa\.com"),
    ("Great Lakes Valley Conference", r"Great Lakes Valley Conference|glvcsports"),
    ("Lone Star Conference", r"Lone Star Conference|lonestarconference"),
    ("Association of Christian College Athletics", r"Association of Christian College Athletics|accasports"),
    ("USCAA", r"United States Collegiate Athletic Association|theuscaa\.com|uscaa\.org"),
    ("NCCAA", r"National Christian College Athletic Association|thenccaa\.org"),
]


def norm(s):
    return re.sub(r"[^a-z0-9&]+", " ", s.lower()).strip()


def alias_index():
    idx = {}
    for name, (_c, _s, al) in MASTER.items():
        for a in [name] + al:
            idx[norm(a)] = name
    return idx


# ---------------------------------------------------------------- Hudl
def hudl_json(url, cache):
    st, txt = fetch(url, cache, delay=0.4)
    try:
        return json.loads(txt)
    except Exception:
        return {}


def hudl_search(q, cache):
    out, page = [], 1
    while page <= 3:
        d = hudl_json("https://vcloud.hudl.com/api/viewer/site?title=%s&per_page=100&page=%d"
                      % (urllib.parse.quote(q), page), cache)
        out += d.get("sites", [])
        if page >= int(d.get("num_pages") or 1):
            break
        page += 1
    return out


def hudl_activity(slug, cache):
    d = hudl_json("https://vcloud.hudl.com/api/viewer/broadcast?sites=%s&viewer_status=4&sort_by=date"
                  "&sort_dir=desc&per_page=1" % urllib.parse.quote(slug), cache)
    b = (d.get("broadcasts") or [None])[0]
    count = int(d.get("item_count") or 0)
    last = (b or {}).get("date", "")[:10]
    status = "none"
    if last:
        age = (TODAY - datetime.date.fromisoformat(last)).days
        status = "active" if age <= ACTIVE_DAYS else "stale"
    return {"lastGame": last, "count": count, "status": status}


NON_COLLEGE = re.compile(r"high school|\bhs\b|academy|middle school|junior high|elementary|"
                         r"public schools|isd\b|usd\b|school district|prep\b|\bjr\b", re.I)


STATE_WORDS = set("""alabama alaska arizona arkansas california colorado connecticut delaware florida georgia
hawaii idaho illinois indiana iowa kansas kentucky louisiana maine maryland massachusetts michigan minnesota
mississippi missouri montana nebraska nevada hampshire jersey mexico york carolina dakota ohio oklahoma oregon
pennsylvania rhode tennessee texas utah vermont virginia washington wisconsin wyoming manitoba
ky kan neb mo minn mich ia ks ne nd sd mn mi tx ok il in oh wi""".split())
WEAK = set("university college of the at and campus inc athletics athletic sports".split())


STATE_ABBR = {"alabama": "AL", "alaska": "AK", "arizona": "AZ", "arkansas": "AR", "california": "CA",
              "colorado": "CO", "connecticut": "CT", "delaware": "DE", "florida": "FL", "georgia": "GA",
              "hawaii": "HI", "idaho": "ID", "illinois": "IL", "indiana": "IN", "iowa": "IA", "kansas": "KS",
              "kentucky": "KY", "louisiana": "LA", "maine": "ME", "maryland": "MD", "massachusetts": "MA",
              "michigan": "MI", "minnesota": "MN", "mississippi": "MS", "missouri": "MO", "montana": "MT",
              "nebraska": "NE", "nevada": "NV", "new hampshire": "NH", "new jersey": "NJ", "new mexico": "NM",
              "new york": "NY", "north carolina": "NC", "north dakota": "ND", "ohio": "OH", "oklahoma": "OK",
              "oregon": "OR", "pennsylvania": "PA", "rhode island": "RI", "south carolina": "SC",
              "south dakota": "SD", "tennessee": "TN", "texas": "TX", "utah": "UT", "vermont": "VT",
              "virginia": "VA", "washington": "WA", "west virginia": "WV", "wisconsin": "WI",
              "wyoming": "WY", "manitoba": "MB"}


def state_code(s):
    s = (s or "").strip()
    return STATE_ABBR.get(s.lower(), s.upper())


# conference-network copies, academic/church/test sites: never preferred
PENALTY = re.compile(r"\((heart|haac|glvc|miaa|amc|cacc)\)|affiliate|inactive|academics|wbds|hs broadcasts|"
                     r"high school broadcasts|test site|church", re.I)


def tokens(s):
    s = s.lower().replace("&", " and ").replace("saint", "st").replace("st.", "st")
    return [t for t in re.findall(r"[a-z0-9]+", s) if t not in WEAK]


def core(s):
    """Tokens of a name with any parenthetical (usually a state) removed."""
    return set(tokens(re.sub(r"\(.*?\)", " ", s)))


def distinctive(name):
    toks = [t for t in re.findall(r"[A-Za-z&'-]+", name) if t.lower() not in GENERIC and len(t) > 2]
    return sorted(set(toks), key=len, reverse=True)


def name_match(names, title):
    """True when one of the school's names and the Hudl title describe the same school."""
    tt = set(tokens(title))
    tc = core(title)
    for n in names:
        nc = core(n)
        if not nc:
            continue
        if nc <= {k for k in STATE_ABBR if " " not in k}:   # "University of Nebraska" alone is too vague
            continue
        if nc <= tt:                 # every word of our name appears in the title
            return True
        if tc and tc <= nc and len(tc) >= 1 and not (tc <= STATE_WORDS):
            # the title is a shorter form of our name ("Dordt" for "Dordt University");
            # require at least one non-generic, non-state word in common
            if tc - GENERIC - STATE_WORDS:
                return True
    return False


def hudl_lookup(sch, cache):
    """Return (best, candidates, note)."""
    name, state = sch["name"], sch["state"]
    names = [name] + sch["aliases"]
    short = re.sub(r"\s+(University|College)$", "", name)
    queries = [name, name.replace("-", " "), short] + [a for a in sch["aliases"] if len(a) > 5][:2] + \
        [t for t in distinctive(name) if t.lower() not in STATE_WORDS][:2]
    queries = list(dict.fromkeys(queries))
    seen = {}
    for q in queries:
        for s in hudl_search(q, cache):
            seen[s["slug"]] = s
    cands = []
    for s in seen.values():
        t = s["title"] or ""
        if NON_COLLEGE.search(t) and not re.search(r"college|universit", t, re.I):
            continue
        if not name_match(names, t):
            continue
        hs = state_code(s.get("state"))
        if state and hs and hs != state.upper():
            continue
        cands.append(s)
    for c in cands:
        c["_act"] = hudl_activity(c["slug"], cache)
    for bad, good in HUDL_AVOID.items():
        if any(c["slug"] == good for c in cands):
            cands = [c for c in cands if c["slug"] != bad]

    def sim(c):
        t = norm(re.sub(r"\(.*?\)", " ", c["title"] or ""))
        return max(difflib.SequenceMatcher(None, norm(n), t).ratio() for n in names)

    def score(c):
        a = c["_act"]
        return (not PENALTY.search(c["title"] or ""),
                sim(c) >= 0.8,
                bool(state) and state_code(c.get("state")) == state.upper(),
                {"active": 2, "stale": 1, "none": 0}[a["status"]], a["lastGame"], a["count"])
    cands.sort(key=score, reverse=True)
    note = ""
    plausible = [c for c in cands if c["_act"]["status"] != "none" and not PENALTY.search(c["title"] or "")
                 and sim(c) >= 0.75]
    if len(plausible) > 1:
        note = "multiple Hudl sites with broadcasts: " + ", ".join(
            "%s (%s, %s, %s %s, %d)" % (c["slug"], c["title"], c.get("state") or "?", c["_act"]["status"],
                                       c["_act"]["lastGame"], c["_act"]["count"]) for c in plausible[:5])
    return (cands[0] if cands else None), cands, note


# ---------------------------------------------------------------- YouTube
YT_CHAN = re.compile(r"https?://(?:www\.|m\.)?youtube\.com/(@[A-Za-z0-9_.\-]+|channel/UC[A-Za-z0-9_\-]{22}|c/[^/\"'?#\s]+|user/[^/\"'?#\s]+)", re.I)
YT_VIDEO = re.compile(r"https?://(?:www\.|m\.)?(?:youtube\.com/(?:watch\?v=|live/)|youtu\.be/)[A-Za-z0-9_\-]{6,}", re.I)


def yt_channel_links(text):
    out = []
    for m in YT_CHAN.finditer(html.unescape(text)):
        p = m.group(1)
        out.append(p.rstrip("/").strip())
    return out


def yt_resolve(path, cache):
    """path like '@handle' or 'channel/UC..' -> dict or None (confirmed from channel page)."""
    url = "https://www.youtube.com/" + urllib.parse.quote(path, safe="@/_-.")
    st, s = fetch(url, cache, delay=1.0)
    if st != 200:
        return None
    cid = re.search(r'<link rel="canonical" href="https://www\.youtube\.com/channel/(UC[\w-]{22})"', s) or \
        re.search(r'"externalId":"(UC[\w-]{22})"', s)
    if not cid:
        return None
    handle = re.search(r'"vanityChannelUrl":"https?://www\.youtube\.com/(@[^"]+)"', s) or \
        re.search(r'"canonicalBaseUrl":"/(@[^"]+)"', s)
    title = re.search(r"<title>(.*?) - YouTube</title>", s, re.S)
    return {"channelId": cid.group(1), "handle": html.unescape(handle.group(1)) if handle else
            (path if path.startswith("@") else ""),
            "url": "https://www.youtube.com/channel/" + cid.group(1),
            "title": html.unescape(title.group(1)).strip() if title else ""}


def yt_plausible(name, e, r):
    """Channel title/handle must mention the school (word, acronym or site-domain stem)."""
    blob = re.sub(r"[^a-z0-9]", "", (r["title"] + " " + r["handle"]).lower())
    keys = set()
    for n in [name] + sorted(e["aliases"]):
        words = re.findall(r"[A-Za-z]+", n)
        for w in words:
            if len(w) >= 4 and w.lower() not in GENERIC and w.lower() not in STATE_WORDS:
                keys.add(w.lower())
        sig = [w for w in words if w.lower() not in ("of", "the", "at", "and")]
        if len(sig) >= 2:
            keys.add("".join(w[0] for w in sig).lower())
            keys.add("".join(w[0] for w in sig if w.lower() not in ("university", "college")).lower())
    site = urllib.parse.urlparse(e.get("site") or "").netloc.lower().replace("www.", "")
    if site:
        stem = site.split(".")[0]
        for suf in ("athletics", "sports", "go", "lets"):
            stem = stem.replace(suf, "")
        if len(stem) >= 3:
            keys.add(stem)
    keys = {k for k in keys if len(k) >= 3}
    return any(k in blob for k in keys)


ASSOCIATIONS = {"NCCAA", "USCAA", "Association of Christian College Athletics"}


def detect_conference(text):
    """Most-mentioned conference on the home page (>= 2 mentions); else the most-mentioned
    association (NCCAA / USCAA / ACCA); else "".  A heuristic: see report."""
    counts = {name: len(re.findall(rx, text, re.I)) for name, rx in CONFERENCES}
    confs = [(c, n) for n, c in counts.items() if n not in ASSOCIATIONS and c >= 2]
    if confs:
        return max(confs)[1]
    assoc = [(c, n) for n, c in counts.items() if n in ASSOCIATIONS and c >= 1]
    return max(assoc)[1] if assoc else ""


# ---------------------------------------------------------------- main
def main():
    cache = sys.argv[1]
    data = json.load(open(os.path.join(cache, "games.json")))
    games, log = data["games"], data["log"]
    idx = alias_index()
    l1names = [s["name"] for s in LEVEL1]
    cfg = {s["name"]: s for s in [UNION] + LEVEL1}

    schools = {}
    unmapped = collections.Counter()
    dropped = collections.Counter()

    def get(name):
        if name not in schools:
            c, st, _al = MASTER.get(name, ("", "", []))
            lvl = 0 if name == UNION["name"] else 1 if name in l1names else 2
            schools[name] = {"name": name, "aliases": set(), "city": c, "state": st, "level": lvl,
                             "playedBy": set(), "sources": set(), "siteUrls": collections.Counter(),
                             "flags": set(), "videoLinks": collections.Counter(), "ytFromSchedules": collections.Counter()}
        return schools[name]

    for n in [UNION["name"]] + l1names:
        get(n)
        for l in log:
            if l["school"] == n and l["status"] == 200 and l["games"]:
                schools[n]["sources"].add(l["url"])

    for g in games:
        clean_name, flags = strip_name(g["raw"])
        if is_dropped(clean_name):
            dropped[clean_name] += 1
            continue
        canon = idx.get(norm(clean_name))
        if not canon:
            unmapped[(clean_name, g["school"])] += 1
            continue
        e = get(canon)
        if clean_name != canon:
            e["aliases"].add(clean_name)
        if g["school"] in l1names and canon != g["school"]:
            e["playedBy"].add(g["school"])
        if g["school"] == UNION["name"] and canon in l1names:
            e["playedBy"].add(UNION["name"])
        if e["level"] == 2:  # level 0/1 keep their own schedule URLs as the source
            e["sources"].add(g["url"])
        e["flags"] |= flags
        if g.get("oppUrl") and "thenccaa" not in g["oppUrl"]:
            u = urllib.parse.urlparse(g["oppUrl"])
            path = "" if re.search(r"/(sports|landing|index)", u.path) else u.path.rstrip("/")
            e["siteUrls"]["%s://%s%s" % (u.scheme, u.netloc, path)] += 1
        # YouTube links in the row of an away game at this opponent -> probably the host's stream
        for h in g["links"]:
            if YT_CHAN.match(h) and g["ha"] == "away":
                e["ytFromSchedules"][("hosted", YT_CHAN.match(h).group(1))] += 1
            if (YT_VIDEO.match(h) or YT_CHAN.match(h)) and g["ha"] == "away":
                e["videoLinks"]["youtube-hosted"] += 1
        host = schools[g["school"]] if g["school"] in schools else get(g["school"])
        for h in g["links"]:
            if YT_VIDEO.match(h) or YT_CHAN.match(h):
                if g["ha"] == "home":
                    host["videoLinks"]["youtube"] += 1
                    if YT_CHAN.match(h):
                        host["ytFromSchedules"][("own", YT_CHAN.match(h).group(1))] += 1
            for plat, rx in [("NFHS", r"nfhsnetwork"), ("Stretch", r"stretchlive|stretch\.com|stretchinternet"),
                             ("Hudl", r"vcloud\.hudl|hudl\.com|bluframe"), ("YouTube", r"youtube|youtu\.be"),
                             ("Team1Sports", r"team1sports"), ("BoxCast", r"boxcast"), ("Twitch", r"twitch\.tv"),
                             ("Facebook Live", r"facebook\.com/.*/(videos|live)"), ("FloSports", r"flosports|flocollege"),
                             ("ESPN+", r"espn\.com/(watch|espnplus)"), ("Heart Network", r"heartconferencenetwork"),
                             ("GPAC Network", r"gpacnetwork|gpactv"), ("PressBox", r"pressbox"), ("Vimeo", r"vimeo\.com")]:
                if re.search(rx, h, re.I) and g["ha"] in ("home", ""):
                    host["videoLinks"][plat] += 1

    # ---- athletics site homepages: conference + YouTube social links
    for n, e in schools.items():
        site = SITE_OVERRIDE.get(n) or (cfg[n]["site"] if n in cfg else
                                         (e["siteUrls"].most_common(1)[0][0] if e["siteUrls"] else ""))
        e["site"] = site
        e["homeYt"], e["conference"] = [], ""
        if not site:
            continue
        st, s = fetch(site, cache, delay=0.5)
        if st != 200:
            e["siteNote"] = "home page HTTP %s" % st
            continue
        e["homeYt"] = yt_channel_links(s)
        e["conference"] = detect_conference(s)
        # also look for video links on L0/L1 schedule pages beyond per-row links (watch-live buttons)
    # ---- YouTube resolution
    resolved = {}
    for n, e in schools.items():
        e["youtube"], e["ytNote"] = None, ""
        if n in YOUTUBE_OVERRIDE:
            p, why = YOUTUBE_OVERRIDE[n]
            e["ytNote"] = why
            if p:
                r = yt_resolve(p if p.startswith("@") else "channel/" + p, cache)
                if r:
                    r["source"] = why
                    e["youtube"] = r
                else:
                    e["ytNote"] = why + " (channel page did not resolve on this run)"
            continue
        cands = collections.Counter()
        for p in e["homeYt"]:
            cands[("home", p)] += 1
        for (kind, p), c in e["ytFromSchedules"].items():
            cands[(kind, p)] += c
        if not cands:
            continue
        # own home-game stream links first (that is where basketball is streamed), then the
        # athletics home page, then links from other schools' schedules; most frequent first
        rank = {"own": 0, "home": 1, "hosted": 2}
        order = sorted(cands.items(), key=lambda kv: (rank[kv[0][0]], -kv[1]))
        rejected = []
        for (src, p), _c in order:
            key = p.lower()
            if key not in resolved:
                resolved[key] = yt_resolve(p, cache)
            r = resolved[key]
            if not r:
                continue
            if not yt_plausible(n, e, r):
                rejected.append("%s (%s)" % (r["handle"] or p, r["title"]))
                continue
            r = dict(r)
            r["source"] = {"own": "stream link on this school's own schedule (home games)",
                           "home": "athletics site %s" % e["site"],
                           "hosted": "stream link on an opponent's schedule (game at this school)"}[src]
            e["youtube"] = r
            others = sorted({q for (_s, q) in cands if q.lower() != key})
            if others:
                e["ytNote"] = "other YouTube links seen: " + ", ".join(others)
            break
        if rejected:
            e["ytNote"] = (e["ytNote"] + "; " if e["ytNote"] else "") +                 "rejected (channel name does not match school): " + ", ".join(rejected)

    # ---- Hudl
    for n, e in sorted(schools.items()):
        sch = {"name": n, "state": e["state"], "aliases": sorted(e["aliases"])}
        if n in HUDL_OVERRIDE:
            slug = HUDL_OVERRIDE[n]
            if slug:
                d = hudl_json("https://vcloud.hudl.com/api/viewer/site?slug=%s&per_page=5" % urllib.parse.quote(slug), cache)
                site = next((s for s in d.get("sites", []) if s["slug"] == slug), {"slug": slug, "title": ""})
                a = hudl_activity(slug, cache)
                e["hudl"] = {"slug": slug, "title": site.get("title", ""), **a}
            else:
                e["hudl"] = None
            e["hudlNote"] = ""
            e["hudlManual"] = True
            e["hudlCands"] = []
            continue
        best, cands, note = hudl_lookup(sch, cache)
        e["hudl"] = {"slug": best["slug"], "title": best["title"], "city": best.get("city", ""),
                     "state": best.get("state", ""), **best["_act"]} if best else None
        e["hudlNote"] = note
        e["hudlCands"] = [(c["slug"], c["title"], c.get("city"), c.get("state"), c["_act"]["status"],
                           c["_act"]["lastGame"], c["_act"]["count"]) for c in cands]
        print("hudl", n, "->", e["hudl"]["slug"] if e["hudl"] else None, file=sys.stderr)

    write_outputs(schools, log, unmapped, dropped)


def other_platform(e):
    if e["hudl"] and e["hudl"]["status"] == "active":
        return ""
    vl = {k: v for k, v in e["videoLinks"].items() if not k.startswith("youtube")}
    parts = [k for k, _ in sorted(vl.items(), key=lambda kv: -kv[1])]
    if "YouTube" not in parts and (e["videoLinks"].get("youtube") or e["videoLinks"].get("youtube-hosted")):
        parts.append("YouTube")
    return ", ".join(parts)


def write_outputs(schools, log, unmapped, dropped):
    rows = []
    for n, e in schools.items():
        hud = e["hudl"]
        yt = e.get("youtube")
        rows.append({
            "name": n, "aliases": sorted(e["aliases"]), "city": e["city"], "state": e["state"],
            "conference": e.get("conference", ""), "level": e["level"],
            "playedBy": sorted(e["playedBy"]),
            "hudl": ({k: hud[k] for k in ("slug", "title", "status", "lastGame", "count")} if hud else None),
            "otherPlatform": other_platform(e),
            "youtube": ({"channelId": yt["channelId"], "handle": yt["handle"], "url": yt["url"],
                         "source": yt["source"]} if yt else None),
            "youtubeStreamsBasketball": bool(e["videoLinks"].get("youtube") or e["videoLinks"].get("youtube-hosted")),
            "athleticsSite": e.get("site", ""),
            "source": sorted(e["sources"]),
        })
    rows.sort(key=lambda r: (r["level"], r["name"]))
    json.dump(rows, open(os.path.join(HERE, "schools.json"), "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    with open(os.path.join(HERE, "schools.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["name", "level", "city", "state", "conference", "playedBy", "hudlSlug", "hudlTitle",
                    "hudlStatus", "hudlLastGame", "hudlCount", "otherPlatform", "youtubeHandle",
                    "youtubeChannelId", "youtubeStreamsBasketball", "athleticsSite", "aliases", "source"])
        for r in rows:
            h, y = r["hudl"] or {}, r["youtube"] or {}
            w.writerow([r["name"], r["level"], r["city"], r["state"], r["conference"], "; ".join(r["playedBy"]),
                        h.get("slug", ""), h.get("title", ""), h.get("status", "none"), h.get("lastGame", ""),
                        h.get("count", ""), r["otherPlatform"], y.get("handle", ""), y.get("channelId", ""),
                        r["youtubeStreamsBasketball"], r["athleticsSite"], "; ".join(r["aliases"]), " ".join(r["source"])])
    # sidecar for report writing
    json.dump({"unmapped": [[k[0], k[1], v] for k, v in unmapped.items()],
               "dropped": dropped,
               "hudl": {n: {"note": e.get("hudlNote", ""), "cands": e.get("hudlCands", [])} for n, e in schools.items()},
               "yt": {n: e.get("ytNote", "") for n, e in schools.items()},
               "videoLinks": {n: dict(e["videoLinks"]) for n, e in schools.items() if e["videoLinks"]},
               "siteNotes": {n: e.get("siteNote", "") for n, e in schools.items() if e.get("siteNote")},
               "log": log, "notes": NOTES},
              open(os.path.join(sys.argv[1], "review.json"), "w"), indent=1, default=list)
    print("wrote", len(rows), "schools", file=sys.stderr)


if __name__ == "__main__":
    main()
