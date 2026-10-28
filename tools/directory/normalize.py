"""Opponent-name cleanup shared by build.py."""
import re

# Event / placeholder names that are not opponents.
DROP_PATTERNS = [
    r"^tba$", r"^tbd$", r"bye$", r"tournament", r"championship", r"quarterfinal", r"semifinal",
    r"^alumni", r"alumni$", r"knights night", r"^national tournament$", r"classic$",
    r"\bprep\b", r"high school", r"^bvu vs", r"^simpson vs", r" vs\.? ",
    r"national team",
]

# Trailing event labels some sites append to the opponent name.
TRAIL = [
    r"MCCC Tournament.*$", r"Central Regional? Tournament.*$", r"Bellevue Classic$",
    r"Manhattan Classic$", r"Virgin Islands National Team$",
    r"\s+%?\s*@\s.*$",   # "Union Adventist University @ SWAU" = neutral-site venue
    # OCC rows sometimes carry "City, St. time Video" / "City, St. W, 80-53"
    r"\s[A-Z][a-z]+(?: [A-Z][a-z]+)? ?, [A-Z][a-z]{1,4}\..*$",
]


def strip_name(raw):
    """Return (clean_name, flags) where flags notes exhibition/JV/scrimmage."""
    s = raw.strip()
    flags = set()
    for t in TRAIL:
        s2 = re.sub(t, "", s).strip()
        if s2 != s:
            s = s2
    s = re.sub(r"^(at|vs\.?|@)\s+", "", s, flags=re.I)
    # rankings: "#4", "#4/6", "(RV)", "(12)", "RV/1", leading bare seed digits
    s = re.sub(r"^(#\d+(/\d+)?|\(\s*(RV|\d+)\s*\)|RV(/\d+)?|\d+)\s+", "", s)
    s = re.sub(r"^(#\d+(/\d+)?|RV)\s+", "", s)
    for pat, flag in [(r"\(\s*exh(ibition)?\.?\s*\)|\*exhibition\*", "exhibition"),
                      (r"\(\s*scrimmage\s*\)", "scrimmage"), (r"\bJV\b", "jv")]:
        if re.search(pat, s, re.I):
            flags.add(flag)
            s = re.sub(pat, "", s, flags=re.I)
    s = re.sub(r"[\s#*^%]+$", "", s)       # conference / footnote markers
    s = re.sub(r"\s+", " ", s).strip(" -,")
    return s, flags


def is_dropped(name):
    n = name.lower().strip()
    if not n:
        return True
    return any(re.search(p, n) for p in DROP_PATTERNS)
