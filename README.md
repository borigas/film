# Game Film Viewer (Hudl / BlueFrame / GPAC streams)

A single static page (`index.html`) that plays the HLS stream behind a Hudl vCloud / BlueFrame / GPAC Network game in a normal HTML5 `<video>` (via hls.js) with fast seeking, film-review shortcuts and bookmarks. No server, no install, no Node.

## Open it

- Go to **https://film.origas.org** (this repo, served by GitHub Pages). Casting works from there, and links such as `https://film.origas.org/?src=4679968&t=5000` can be shared and bookmarked.
- Or double-click `index.html` (works from `file://`, but Chrome may not offer casting there), or host it on any other static web host.

## Load a game

Paste any of these into the top box and press Enter:

- GPAC page: `https://www.gpacnetwork.com/mountmarty/?B=4679968`
- BlueFrame share link: `...watch-live?bfplayvid=4209918`
- Embed URL or a whole `<iframe src="https://vcloud.hudl.com/broadcast/embed/4679968?...">` snippet
- Broadcast ID: `4679968`
- Direct `.m3u8` URL
- A timestamp copied from **Copy link**, e.g. `4679968 @ 1:23:20`

No link? Type the school's site name in **Browse school** (e.g. `mountmarty`, `occambassadors`; for GPAC it's the part after `gpacnetwork.com/`) and pick a game. Live and upcoming games are listed first, then recent games (with **Load more**). The last school is remembered.

### Search previous games

The school's game list has a search bar. It searches the school's **whole archive** on Hudl's server, not only the games already listed:

- **Search box**: an opponent or any word from the game title, e.g. `Hastings`, `volleyball`, `homecoming`. Case doesn't matter, partial words match (`hasti`), and with several words every word must appear in the title, in any order. It runs 0.4 s after you stop typing, or straight away when you press Enter. Esc clears it.
- **Sport**: limits the search to one sport. The list shows the sports found in the school's 100 most recent games (plus any found as you search), because Hudl has no per-school sport list. A sport the school hasn't played recently may be missing; search its name in the title box instead.
- **From / To**: limits the search to a date range (whole days, your time zone).
- The filters combine. Matches use the same list as recent games, newest first, with **Load more** past 30. **No matches** is shown when nothing fits. **Clear** (or emptying every filter) returns to the normal list.

Search only covers previous (archived) games, and only the title text: a game titled "Mount Marty vs Doane" won't match `volleyball` unless you pick the sport. Games shared with the school by another site (for example the opponent's home broadcast) are included, as on the school's own page. Hudl requires a school, so there is no all-schools search.

Some older archived games use a legacy Hudl stream address that doesn't allow cross-site loading. For those the page fetches the playlist through the same Hudl JSONP endpoint it uses for lookups; the video itself still streams directly from Hudl's CDN.

The page looks up the stream URL for a broadcast ID through Hudl's own viewer endpoint (`vcloud.hudl.com/api/viewer/app/rss`, JSONP), and lists and searches games with `vcloud.hudl.com/api/viewer/broadcast` (JSONP; search uses its `title`, `section_id`, `after` and `before` parameters, the same ones BlueFrame's own widget sends). **This endpoint is undocumented and Hudl could change or remove it at any time**; if lookups start failing, that is the likely cause. Pasting a direct `.m3u8` URL still works regardless. Only the stream URL, title, date and status are kept from the lookup response.

## Links and bookmarks

- `?src=<link or ID>&t=<seconds>` loads a game and starts there; `?site=<slug>` opens the school's game list.
- When the page runs at its own URL (https://film.origas.org, a local file or another static host), the address bar keeps `t` current and **Copy link** copies a resume link. Inside an embedded frame (such as an artifact page) it copies a timestamp like `4679968 @ 1:23:20` instead; paste that into the box to resume.
- Bookmarks are saved per broadcast in this browser's localStorage (not synced between machines). Click a time to seek, type a note next to it, and use **Export** to download the list (also copied to the clipboard).
- Quality: Auto, or a fixed H.264 level. HEVC variants are hidden so every browser can play.

## Casting (Chromecast / Google TV)

Use https://film.origas.org (or another `https://` address) to cast. In Chrome or Edge, a **Cast** button appears in the control bar when a Cast device is found. It plays the current game on the TV, starting where you were, and pauses the page. While casting:

- The shortcuts and the bookmark list control the TV: play/pause, seeking, 0 to 9 jumps, and bookmarks (M marks the TV's current time). Frame step is off. Speed changes are sent to the TV, but the default Cast player may ignore them. If it does, the page says so.
- The video area shows "Casting to *device*" with the TV's time, and the address bar's `t` follows the TV.
- Loading another game plays it on the TV.
- **Stop casting** (or stopping from the TV or Chrome) resumes playback here at the TV's position.

Older (legacy) games are cast from their H.264 variant stream, because Hudl's legacy playlist address can't be read by the TV.

**Opened as a local file?** Chrome may not find Cast devices for a `file://` page. If no Cast button appears, click the small **Cast?** note for options: open it from https://film.origas.org instead, or use Chrome's ⋮ menu > **Cast...** to mirror the tab.

## Shortcuts

| Key | Action |
| --- | --- |
| Space | Play / pause |
| ← / → | Back / forward 5 s |
| J / K | Back / forward 10 s |
| Shift + ← / → | Back / forward 30 s |
| , / . | Step one frame back / forward (~1/30 s, pauses; off while casting) |
| ↓ / ↑ (or [ / ]) | Slower / faster (0.25x to 2x) |
| \ | Reset speed to 1x |
| 0 to 9 | Jump to 0% to 90% |
| M | Bookmark current time (type a note, Enter to finish) |
| F | Fullscreen |

Shortcuts are ignored while you type in a text field. While casting they control the TV.
