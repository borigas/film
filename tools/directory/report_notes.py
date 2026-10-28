"""Hand-written findings for report.md (update after each season's review)."""

SCHEDULE_NOTES = [
    "Every level-1 school's men's and women's schedules for 2026-27 and 2025-26 were read from its own athletics site, "
    "except the gaps below. None is completely unreadable.",
    "**York University (NE)** is on the level-1 list but is **not on Union's 2025-26 or 2026-27 schedule** (men or women). "
    "It is kept at level 1 as instructed. Its own schedules were read normally. (Barclay plays York in 2026-27.)",
    "**Barclay College** (bears.barclay.college) publishes only the current season (2026-27). There is no 2025-26 schedule page, "
    "so Barclay's level-2 opponents come from 2026-27 only.",
    "**Calvary University** has not posted a women's 2026-27 schedule yet (empty page). Its men's reserve (JV) schedule was also read. "
    "The 2026-27 reserve schedule has 13 games, and the 2025-26 one is empty.",
    "**Spurgeon College** has no women's basketball page (the URL redirects to the home page), so only men's schedules were read.",
    "**Doane, Bellevue, Andrews and Kansas Christian** (PrestoSports) sit behind an AWS WAF JavaScript challenge that sometimes "
    "answers curl with HTTP 202 and an empty body. The scraper retries with back-off and never tries to solve the challenge. "
    "All of their pages loaded on a retry this run. If a future run logs 'HTTP 202' for one of them, re-run later.",
    "**Ozark Christian College**: https://occambassadors.com fails TLS from Windows curl (schannel), so the scraper uses http://. "
    "OCC rows sometimes glue the city, time and result onto the opponent name. normalize.py strips them.",
    "**Andrews** lists some neutral-site games as 'Union Adventist University @ SWAU' or 'Me.-Augusta % @ Buffalo, N.Y.'. "
    "The '@ ...' part is the venue, and box scores confirm these are real Andrews games.",
]

REVIEW_NOTES = [
    "**Conference** is a heuristic: it is the conference named most often on the school's athletics home page (at least 2 mentions). "
    "If no conference is named, it falls back to the association most often named (NCCAA/USCAA/ACCA). It is blank when the site was not identified. "
    "Spot-check it before relying on it. For example, Sterling College shows NCCAA but is a KCAC member, and Arizona Christian shows Frontier.",
    "**Hudl matches were reviewed by hand.** 23 automatic picks were corrected in build.py `HUDL_OVERRIDE` "
    "(e.g. Bellevue University -> `bellevuebruins`, not `bellevue` = Bellevue College WA; Concordia NE -> `cune`; "
    "University of Sioux Falls -> `usfcougars`). Overrides marked None mean that a search by full name, short name and nickname found nothing credible.",
    "**Lincoln University (MO)** -> `lincolnbluetigers` (title just 'Lincoln', city listed as Springfield MO, active). "
    "The alternative `lubluetigers` ('Lincoln University of Missouri (MIAA)', Jefferson City) is the conference copy. Confirm which one carries basketball.",
    "**Northern Oklahoma College** (Barclay opponent) has two campus sites: `jets` (Enid) and `gomavericks` (Tonkawa). The script picked Enid because it is the more recent. "
    "Barclay's schedule doesn't say which campus.",
    "**Calumet College of St. Joseph**: both `ccsjcrimsonwave` and `CalulmetCollege` (sic) are active. The script picked the first because it is more recent.",
    "**Nelson University** (Mount Marty opponent, 'Nelson University (AZ)') -> `nuazwarriors` (Arizona campus). `nulions` is the Texas main campus.",
    "**Minnesota State Community and Technical College** (Trinity Bible opponent) -> `fergusfalls` (Fergus Falls campus site). The schedule does not name a campus.",
    "**Union Adventist's own Hudl site (`unionadventist`) is stale**: its last archived broadcast was 2025-04-13. Union now streams on YouTube (@unionadventistlive).",
    "Hudl status rule: 'active' = latest archived broadcast within 365 days of the build date, 'stale' = older, 'none' = site exists with 0 archived broadcasts or no site. "
    "The count is all archived broadcasts on the site, all sports.",
    "**YouTube coverage for level 2 is partial by design.** Channels were taken from links on the school's athletics site, "
    "and a level-2 school's athletics site is known only when a level-1 Sidearm schedule links to it (124 of 229 schools). "
    "The other ~105 level-2 schools were not searched, so `youtube: null` there means 'not checked', not 'no channel'.",
    "YouTube channels were checked by fetching each channel page and reading its canonical channel ID (RSS feeds currently 404). "
    "Auto-picked channels had to mention the school (a name word, its initials, or the athletics-site domain). Rejected and hand-picked ones are noted under `YOUTUBE_OVERRIDE` in build.py. "
    "Mount Marty's linked channels are dead (one 404s, and YouTube removed the other). Trinity Bible's linked handle 404s. Andrews links only a student-association playlist.",
    "Some YouTube picks are university-wide channels, not athletics ones (e.g. Spalding `@SpaldingDotEDU`, Grand View `@GrandViewUniversityVideo`, Barclay `@BarclayCollege`). They were kept because the athletics site links them.",
    "`youtubeStreamsBasketball` is true when a schedule row links a YouTube video or channel, either on the school's own home game or on a level-1 opponent's row for a game at that school. "
    "It is false for schools whose schedules we never saw, so it is not evidence that they don't stream on YouTube.",
    "`otherPlatform` is filled only from schedule links we actually saw (e.g. Mount Marty -> GPAC Network, Peru State -> Heart Network, Nebraska Wesleyan -> Team1Sports). It is blank for most level-2 schools.",
    "**Four Winds University** (Barclay 2026-27 home opponent) could not be identified, so it has no city or state. Hudl only has Four Winds High School (Fort Totten, ND).",
    "City/state for level-2 schools come from schedule location fields where shown. Otherwise they were filled from general knowledge in `schools_master.py`, so treat them as unverified.",
    "Fields: `playedBy` lists the level-1 schools whose schedules include the school. For level-1 entries it also includes "
    "'Union Adventist University' when Union's schedule lists them. For Union itself, it lists the level-1 schools whose own schedules include Union "
    "(Nebraska Wesleyan, Doane and York don't list Union in either season). `source` is the school's own schedule URLs for levels 0 and 1, "
    "and the level-1 schedule URLs it appears on for level 2. `athleticsSite` and `youtubeStreamsBasketball` are extra fields beyond the requested schema.",
    "Level-1 schools that are mapped to Hudl but have no active Hudl broadcasts: Union (stale), Barclay (stale, 2025-02), Central Bible (stale, 2025-05) "
    "and Manhattan Christian (site exists, 0 broadcasts). None was found for Kansas Christian, Southwestern Adventist or Trinity Bible. "
    "Most of these stream basketball on YouTube instead (see their `youtube` field).",
]
