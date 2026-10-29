# CLAUDE.md — notes for agents working on this repo

`README.md` is for users. This file is for whoever changes the code.

## Purpose and URLs

A single-page game-film viewer used by the owner (a basketball coach): it plays Hudl / BlueFrame / GPAC broadcasts and YouTube videos, with review shortcuts, bookmarks, school search and casting.

- **Live:** https://film.origas.org (`index.html`). **Beta:** https://film.origas.org/beta/ (`beta/index.html`).
- **Repo:** https://github.com/borigas/film, branch `main`, served by GitHub Pages from the repo root (`.nojekyll` present). Every file in the repo is public, including `tools/`.
- **Custom domain:** the `CNAME` file holds `film.origas.org`. DNS is at Cloudflare as a DNS-only (grey cloud) CNAME to `borigas.github.io`, and Pages has HTTPS enforced.

## Repo layout

```
index.html          main site: the whole app in one file
beta/index.html     beta site: same app, labelled "beta"; changes land here first
README.md           user documentation
CLAUDE.md           this file
CNAME, .nojekyll    GitHub Pages settings
.gitignore
tools/directory/    school-list build: scrape.py, build.py, report.py, report_notes.py,
                    config.py, normalize.py, schools_master.py, export_viewer.py,
                    schools.json / schools.csv (outputs), report.md (latest build notes)
```

## Architecture

- **One HTML file**, plain JS in an IIFE. No build step, no server, no framework. It works from `file://` (minus Cast and YouTube). The only external script is hls.js 1.5.20 (cdnjs, with a jsDelivr fallback); the Cast sender and the YouTube IFrame API are loaded on demand.
- **Hudl lookup chain:**
  - `parseInput()` order: `?B=` (GPAC), `bfplayvid=`, `/broadcast/embed/<id>`, `/api/broadcast/vmap/<id>`, YouTube, `.m3u8`, bare digits, then the last run of 6+ digits. Hudl patterns win over YouTube.
  - The broadcast ID is resolved via the VMAP `https://vcloud.hudl.com/api/broadcast/vmap/<id>`, fetched through Hudl's JSONP fetch proxy `https://vcloud.hudl.com/api/viewer/app/rss?url=<encoded>&callback=<fn>`. The response is `fn({success, status, contents})`.
  - This proxy is **undocumented**. It's also used to fetch legacy playlists and YouTube pages.
  - From the VMAP only the Broadcast id/title/date/status, the Site name/slug and the Content URL/type/geoblocked are kept. `.mp4` URLs are rejected.
- **Legacy games:** `https://vcloud.hudl.com/file/broadcast/<id>.m3u8` has no CORS header.
  - The master playlist is fetched through the proxy, validated (`#EXTM3U`, at most 200 KB, every URI https), and handed to hls.js as a `blob:` URL.
  - Its variant playlists and segments are on CloudFront, which sends `Access-Control-Allow-Origin: *`; Hudl's other CDN URLs do too. Casting a legacy game sends the TV the H.264 variant URL directly.
- **hls.js** keeps only `avc1` levels (`restrictToAvc`), so HEVC variants are hidden. Safari uses native HLS if MediaSource is missing.
- **Listing and search:** `https://vcloud.hudl.com/api/viewer/broadcast` (JSONP).
  - Params: `sites=a,b,c` (comma list; slugs are case-insensitive, but responses keep the site's own case, e.g. `NebWesleyan`), `viewer_status` (`2` = live now, `status` "Streaming"; `1` = upcoming, `status` "Upcoming"; `3` = both; `4` = archived; checked against real responses Oct 2026). Beta's default list uses `2` (sort asc) for **Live now** plus `4` (sort desc) for recent games; upcoming games are never listed (no video yet), and `renderNormal` also drops any `status` matching /upcoming/. Main still uses `3` until promoted. Other params: `sort_by=date`, `sort_dir`, `per_page` (30; 100 for the sport-menu sample), `page`, `title` (every word must appear), `section_id`, `after` / `before` (ISO instants).
  - Response: `broadcasts[]`, `item_count`, `num_pages`.
  - **Section ids are global** (`api/viewer/section` lists them with `site: null`): 45 Men's Basketball, 46 Women's Basketball, 1 generic Basketball (also 4900 Boys, 4901 Girls).
  - `section_id=45,1` (comma list) returns one date-sorted, correctly paged result across both. A repeated `section_id=` keeps only the last value. `id=` is ignored.
- **Site search:** `https://vcloud.hudl.com/api/viewer/site?title=<substring>&per_page=100` returns `sites[]` (`title`, `slug`, `city`, `state`). It's used as the fallback when the inlined school directory has no match.
- **School directory:** `tools/directory/schools.json`, compacted and inlined between `/*SCHOOLS-START*/` and `/*SCHOOLS-END*/` by `export_viewer.py`. The page's typeahead matches names, aliases, slugs, handles and initials. Union is level 0, its opponents level 1 and their opponents level 2; levels 0 and 1 are listed first.
- **YouTube:**
  - Playback uses the IFrame Player API (`https://www.youtube.com/iframe_api`). It replaces the `<video>` and is fully torn down when a Hudl game loads.
  - `onError` codes handled: 2, 5, 100, 101, 150 and 153. 153 is the missing referrer, which always happens on `file://`.
  - Channel lists come from `https://www.youtube.com/channel/<UC…>/streams` or `/videos`, fetched through the proxy (about 1.3 MB). `ytInitialData` is cut out (`var ytInitialData = ` … `;</script>`), `JSON.parse`d, and walked for `lockupViewModel`, `videoRenderer` and `gridVideoRenderer`. That gives about 30 videos.
  - YouTube RSS feeds return 404 for every channel, so they aren't used.
- **Touch gestures** (beta; the "touch gestures" block just before CastPlan): pointer events on `#videoWrap`, `pointerType === 'touch'` only, so mouse behaviour is unchanged.
  - Double-tapping the left or right 40% calls `seekBy(∓10)` (the J/K path); further taps within 700 ms add 10 s each. Double-tapping the middle calls `toggleFullscreen()` (shared with F). Holding for 400 ms with less than 10 px of movement calls `applyRate(2)`, and release or pointercancel restores the previous rate. Hold is ignored while paused or casting. The bottom 48 px of the player is ignored.
  - Consumed touches `preventDefault` their `touchend`, so the native `<video>` doesn't also react; single taps are untouched.
  - YouTube: the iframe swallows touches, so `#tapPad` (transparent, positioned over the iframe minus its bottom 48 px by `padSync()`) takes them. It is shown only when the primary pointer is coarse (`matchMedia('(pointer: coarse)')`) and after the video first plays (`YTP.started`), so YouTube's own play button gets the first tap. A single tap on the pad toggles play after 300 ms.
- YouTube channel lists drop `upcoming` items (scheduled streams and premieres) unless they're `live`; the count line says how many were hidden.
- **Cast:** Google Cast Web Sender with the Default Media Receiver. Only Hudl HLS is cast; on YouTube the button is hidden and an active session is ended. `CastPlan` chooses the URL and the HLS segment format.
- **Storage keys** (all access goes through try/catch helpers):
  - localStorage:
    - `hudl-film-viewer:bookmarks:<key>`, where `<key>` is the broadcast ID, `yt:<videoId>` or `url:<m3u8 without query>`; the value is `[{t, note, at}]`;
    - `hudl-film-viewer:lastSite`;
    - `hudl-film-viewer:panelCollapsed`;
    - `hudl-film-viewer:panelWidth`;
    - `hudl-film-viewer:recentLists`.
  - sessionStorage: `hudl-film-viewer:pos:<key>` holds `{t, urlT, urlFinalT}`.
  - Main and beta share these, because they're on the same origin. Never rename a key without migrating it.
- **Deep links:**
  - `?src=<anything the box accepts>` and `&t=<seconds>`; `?site=<hudl slug>`; `#bm=<share data>`.
  - The address bar's `t=` is written only while paused, and on pagehide/beforeunload. `#bm=` is kept through these updates.
  - **Resume rule:** on load, the sessionStorage live time is used only if the navigation type is `reload` or `back_forward`, it's the same game, and the URL's `t=` equals `urlT` or `urlFinalT` (what this tab last wrote). Otherwise the URL's `t=` wins. A reload uses the URL from before the unload-time write; back/forward uses the one after it.
  - A same-document `#bm=` change (a share link pasted for the open game) is applied on `hashchange`.
- **Share links (`#bm=`):**
  - Encoding: `1.` + base64url(deflate-raw(JSON)) when CompressionStream exists, else `0.` + base64url(JSON). The JSON is `{v:1, b:[[tenthsOfSecond, note], …]}`.
  - Decode limits: fragment ≤ 200 KB; decompressed ≤ 64 KB; ≤ 300 bookmarks; notes ≤ 300 characters; times finite, ≥ 0 and ≤ 10 days. Anything malformed shows a small notice.
  - Shared bookmarks are shown in their own section and saved only by an explicit per-item save, which adds and never replaces.

## Hard rules

- **Never log, display, store or commit the raw VMAP response.** It contains AWS credentials. Extract the few fields needed and drop it (`lookupBroadcast` nulls it in `finally`).
- Render untrusted text (titles, notes, API data, fragments) only via `textContent` or `escapeHtml`.
- All localStorage and sessionStorage access goes through try/catch.
- No `eval`, and never execute fetched content. JSONP is limited to Hudl's endpoints, and YouTube data is `JSON.parse`d.
- Keep the app a single file. Inline script string literals must not contain a literal `</script>`; write `<\/script>`.

## Workflow

1. Change `beta/index.html` first.
2. Test locally: `python -m http.server 8765 --bind 127.0.0.1 --directory <repo>`, then open http://127.0.0.1:8765/beta/.
   - Quick checks: extract the last inline `<script>` and run `node --check` on it. The pure helpers (`YtParse`, `SchoolSearch`, `CastPlan`) sit between `/* …-BEGIN */` and `/* …-END */` markers so they can be unit-tested in Node.
3. Commit and push. Verify live with a cache-buster such as `https://film.origas.org/beta/?v=<commit>`; Pages takes about a minute.
4. **Promote to main:** copy `beta/index.html` to `index.html`, then remove only `" (beta)"` from `<title>` and the `<span class="badge tag" …>beta</span>` in the top bar.
   - Check that `git show HEAD:beta/index.html | diff - index.html` shows only those two lines.
   - Update `README.md` for user-visible changes. Don't keep copies outside the repo.
5. **Commits:**
   - The commit identity is the GitHub noreply address (`2268265+borigas@users.noreply.github.com`).
   - Messages end with `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.
   - Commit or push only when asked. The owner reviews, then pushes or asks for the push.
6. **Line endings:** `core.autocrlf=true` is set globally on the owner's machine, and files are stored with LF. To restore a file byte-for-byte, use `git -c core.autocrlf=false checkout -- <file>`.

## Rebuilding the school list (each season)

1. Edit `tools/directory/config.py`:
   - `SEASONS`, newest first;
   - the level-1 list (`LEVEL1`), each with its athletics site and platform: sidearm, presto, drupal or barclay.
2. Run with a cache directory **outside the repo** (downloaded pages are cached in `<cache>/http`; delete it to refresh):
   ```
   python -I tools/directory/scrape.py <cache>    # level-0/1 schedules -> <cache>/games.json
   python -I tools/directory/build.py  <cache>    # names, Hudl + YouTube lookups -> schools.json, schools.csv, <cache>/review.json
   python -I tools/directory/report.py <cache>    # report.md
   python -I tools/directory/export_viewer.py     # inline into beta/index.html (--main, --both, or paths)
   ```
3. **Network access:**
   - Everything goes through `curl` with throttling: `fetch()` waits 0.4–1.0 s between requests and retries with back-off.
   - Some PrestoSports sites (Doane, Bellevue, Andrews, Kansas Christian) sit behind an AWS WAF JavaScript challenge that sometimes answers HTTP 202 with an empty body. Re-run later. **Never try to solve or bypass the challenge.**
   - Ozark Christian's site needs `http://` because TLS fails from Windows curl.
4. **Review:**
   - New opponent spellings show up as "unmapped" in `report.md`; add them to `schools_master.py`.
   - Fix wrong automatic matches by hand in `build.py`: `HUDL_OVERRIDE` (name → slug, or `None` for no site) and `YOUTUBE_OVERRIDE` (name → (handle or UC id, reason)).
   - Update the hand-written notes in `report_notes.py`, then re-run build and report.
5. Test on beta, then promote.

## Fragile spots, and what has never been tested

- **Undocumented endpoints:** the Hudl proxy, the listing, site and VMAP endpoints, and YouTube channel-page parsing. If YouTube's page shape changes, `YtParse.videos` stops finding videos and the list shows a link to the channel instead.
- **Never tested:** casting to a real Chromecast, Safari (native-HLS path, iOS), live games (DVR window, live casting), and `file://` beyond the basics (YouTube can't play there; Cast usually isn't offered).
- **Touch gestures were tested only with synthetic PointerEvents and TouchEvents** (desktop Chrome, mobile emulation), never on a real phone or tablet. Untested:
  - whether Chrome Android's native video controls have their own double-tap seek, and whether cancelling the `touchend` suppresses it;
  - the iOS long-press callout and Safari's handling of hold;
  - full screen on iPhone (there's no element `requestFullscreen`, so the middle double tap does nothing);
  - whether the YouTube iframe obeys `playVideo` from a pad tap on real mobile browsers.
- **Browser automation can't take screenshots here.** UI checks so far have been done through DOM and JS measurements.

## Owner preferences learned so far

- Game lists open on **Men's Basketball** by default, including games in the generic "Basketball" section (women's-titled ones excluded); the other sports stay one click away.
- **Shared bookmarks are never saved automatically.** Saving is one item at a time, adds a copy, and never overwrites.
- The address bar's `t=` updates **only when paused**, so it's easy to copy during playback.
- The finder does **not** fold on outside clicks. It folds on picking or loading a game, on Escape, or from the Find a game button.
- **Show or preview big changes before shipping them** (beta first), and keep the header compact.
