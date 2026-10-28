"""Inputs for the school directory build. Edit SEASONS each year."""

# Newest first. The first entry is "current season".
SEASONS = ["2026-27", "2025-26"]

UNION = {"name": "Union Adventist University", "city": "Lincoln", "state": "NE", "level": 0,
         "site": "https://uauwarriors.com", "platform": "drupal"}

# platform: sidearm | presto | drupal (Union-style Drupal vendor) | barclay (one-off WordPress page)
LEVEL1 = [
    {"name": "Mount Marty University", "city": "Yankton", "state": "SD",
     "site": "https://mountmartyathletics.com", "platform": "sidearm"},
    {"name": "Peru State College", "city": "Peru", "state": "NE",
     "site": "https://pscbobcats.com", "platform": "sidearm"},
    {"name": "Bellevue University", "city": "Bellevue", "state": "NE",
     "site": "https://bubruins.com", "platform": "presto"},
    {"name": "Kansas Christian College", "city": "Overland Park", "state": "KS",
     "site": "https://kccfalcons.com", "platform": "presto"},
    {"name": "Calvary University", "city": "Kansas City", "state": "MO",
     "site": "https://calvarywarriors.com", "platform": "drupal",
     "extraSchedules": [{"sport": "m-jv", "season": s, "url": "https://calvarywarriors.com/sports/mens-basketball-reserve/schedule"}
                        for s in ["2026-27", "2025-26"]]},
    {"name": "Central Bible University", "city": "Moberly", "state": "MO",
     "site": "https://cbusaints.com", "platform": "drupal"},
    {"name": "Barclay College", "city": "Haviland", "state": "KS",
     "site": "https://bears.barclay.college", "platform": "barclay"},
    # HTTPS fails from Windows curl (schannel); plain http works.
    {"name": "Ozark Christian College", "city": "Joplin", "state": "MO",
     "site": "http://occambassadors.com", "platform": "drupal"},
    {"name": "Manhattan Christian College", "city": "Manhattan", "state": "KS",
     "site": "https://mccthunder.com", "platform": "drupal"},
    # Spurgeon has no women's basketball page (redirects to home page).
    {"name": "Spurgeon College", "city": "Kansas City", "state": "MO",
     "site": "https://spurgeonknights.com", "platform": "sidearm", "noSport": "w"},
    {"name": "Trinity Bible College", "city": "Ellendale", "state": "ND",
     "site": "https://tbclions.com", "platform": "presto"},
    {"name": "Faith Baptist Bible College", "city": "Ankeny", "state": "IA",
     "site": "https://fbbceagles.com", "platform": "presto"},
    {"name": "Nebraska Wesleyan University", "city": "Lincoln", "state": "NE",
     "site": "https://nwusports.com", "platform": "sidearm"},
    {"name": "Emmaus University", "city": "Dubuque", "state": "IA",
     "site": "https://emmauseagles.com", "platform": "presto"},
    {"name": "Andrews University", "city": "Berrien Springs", "state": "MI",
     "site": "https://aucardinals.com", "platform": "presto"},
    {"name": "Southwestern Adventist University", "city": "Keene", "state": "TX",
     "site": "https://swauknights.com", "platform": "presto"},
    {"name": "Doane University", "city": "Crete", "state": "NE",
     "site": "https://doaneathletics.com", "platform": "presto"},
    {"name": "York University", "city": "York", "state": "NE",
     "site": "https://yorkpanthers.com", "platform": "sidearm"},
]
