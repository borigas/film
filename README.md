# Game Film Viewer (Hudl / BlueFrame / GPAC streams and YouTube)

A single static page (`index.html`) for watching game film. It plays the HLS stream behind a Hudl vCloud / BlueFrame / GPAC Network game in a normal HTML5 `<video>` (via hls.js), or a YouTube video in YouTube's player, with fast seeking, film-review shortcuts and bookmarks. No server, no install, no Node.

## Open it

- Go to **https://film.origas.org** (this repo, served by GitHub Pages). Casting works from there, and links such as `https://film.origas.org/?src=4679968&t=5000` can be shared and bookmarked.
- Or double-click `index.html` (works from `file://`, but Chrome may not offer casting there and YouTube refuses to play), or host it on any other static web host.
- **https://film.origas.org/beta/** is the beta site (see [Beta](#beta)).

## The header

While you watch, the header is a single slim bar: the game's name, date and source on the left (cut off with "…" when long; hover for the full text) and **Find a game** on the right. Notices and errors appear just under it.

**Find a game** (or the **/** key) opens the finder, which also opens by itself when no game is loaded. It has one box, quick chips and the game list:

- **The box:** paste a game link (see below) or type a school name, then press Enter or **Go**. A game link loads the game; anything else is a school search.
- **Chips:** **Union games**, **Union YouTube**, and up to 4 recently opened schools or Hudl sites (× removes one from the recent list).
- **The game list** opens under the chips.

Picking or loading a game, pressing Escape, or clicking **Find a game** again folds the finder back to the slim bar. Clicking elsewhere on the page leaves it open. Reopening brings it back exactly as it was: box text, school, tab, sport, search, loaded pages and scroll position. The list's **Close** closes just the list.

## Load a game

Paste any of these into the **Find a game** box and press Enter:

- GPAC page: `https://www.gpacnetwork.com/mountmarty/?B=4679968`
- BlueFrame share link: `...watch-live?bfplayvid=4209918`
- Embed URL or a whole `<iframe src="https://vcloud.hudl.com/broadcast/embed/4679968?...">` snippet
- Broadcast ID: `4679968`
- Direct `.m3u8` URL
- YouTube link: `watch?v=`, `youtu.be/`, `/live/`, `/shorts/`, `/embed/` (an `<iframe>` snippet works), with an optional `t=` or `start=`. A bare YouTube ID needs a prefix: `yt:VIDEOID`. Hudl links take priority.
- A timestamp copied from **Copy link**, e.g. `4679968 @ 1:23:20`

A bare number is treated as a broadcast ID. The box shows what it will do ("Load broadcast 4679968", "Play YouTube video …") before you press Enter.

The header shows the game's name, date and source, e.g. `Mount Marty vs Union · Oct 26, 2026, 5:00 PM · Hudl (mountmarty)`, and so does the browser tab title. Hudl dates and times come from the broadcast, in your time zone. YouTube gives no date, so the viewer uses a date written in the video title. If there isn't one and the video was picked from a channel list, it shows an approximate date from "Streamed 3d ago", marked with `~`. Otherwise no date is shown.

## Find a game

### School search

Type a school name in the **Find a game** box. Matches come from a built-in directory of 229 schools (Union Adventist, its opponents and their opponents). Case and punctuation don't matter. Partial words, word starts and initials all match, e.g. `Bellevue`, `neb wes`, `occ` (Ozark Christian College) and `Ozark`. Union and its opponents are listed first. Each result shows the state and badges: **Hudl** (or Hudl stale/none), **YouTube**, or another platform.

- Pick a school with a Hudl site to open its game list.
- If it has a YouTube channel, a **YouTube** button switches to its recent videos (and **Hudl games** switches back).
- If a school isn't in the directory, the box searches Hudl's own list of sites, so any school on Hudl can still be found. **Search all Hudl schools for "…"** at the end of the list does the same on demand.

A Hudl site's list can also be opened with a link: `?site=<slug>` (e.g. `mountmarty`, `occambassadors`; for GPAC it's the part after `gpacnetwork.com/`), or by pasting a GPAC school page into the box.

The school list is rebuilt each season; the tools and data are in `tools/directory/` (see `tools/directory/report.md` for the latest build's notes).

### Union games

The **Union games** chip lists every Hudl game with "Union" in its title across Union's Hudl site and the Hudl sites of all of Union's opponents in the directory, newest first. The **Union YouTube** chip shows Union's channel (@unionadventistlive).

### Game lists

A Hudl list shows games that are live now first (under **Live now**), then recent games (with **Load more**). Scheduled games aren't listed, since they have no video yet.

**Men's Basketball first.** Every Hudl list opens with **Sport** set to **Men's Basketball**, for both live and recent games. Pick **All sports** or another sport to switch. If a school has no Men's Basketball games, the list says so and shows all sports instead. Men's Basketball also includes games filed under the generic "Basketball" sport (as Mount Marty does), except ones whose title says women's (Women's, Lady, WBB, (W) ...) without also saying men's. Because of that filter the archived count is shown as "up to N" when it can't be exact. Pick **Basketball** to see the generic sport on its own.

The list's search bar searches the school's **whole archive** on Hudl's server, not only the games already listed:

- **Search box**: an opponent or any word from the game title, e.g. `Hastings`, `volleyball`, `homecoming`. Case doesn't matter, partial words match (`hasti`), and with several words every word must appear in the title, in any order. It runs 0.4 s after you stop typing, or straight away when you press Enter. Esc clears it.
- **Sport**: the sports found in the school's 100 most recent games (plus any found as you search), because Hudl has no per-school sport list.
- **From / To**: limits the search to a date range (whole days, your time zone).
- The filters combine. **Clear** empties the search words and dates; the sport stays.

Search only covers previous (archived) games, and only the title text. Games shared with the school by another site (for example the opponent's home broadcast) are included, as on the school's own page.

### YouTube channel lists

A school's YouTube list shows its most recent **Live streams** or **Videos** (about 30, the most YouTube's page includes). Click one to play it. Scheduled streams and premieres are hidden (live ones still show), and the count line says how many.

**Channel lists are fragile.** YouTube offers no key-free feed (its RSS feeds currently return errors), so the list is read from the channel's public page, fetched through the same undocumented Hudl proxy the viewer uses for game lookups. If YouTube changes that page or Hudl changes the proxy, the list fails with a link to open the channel on YouTube instead.

## Playback

- **Hudl:** quality is Auto or a fixed H.264 level. HEVC variants are hidden so every browser can play. Some older archived games use a legacy Hudl stream address that doesn't allow cross-site loading; for those the page fetches the playlist through the same Hudl JSONP endpoint it uses for lookups, and the video itself still streams directly from Hudl's CDN.
- **YouTube:** the video plays in YouTube's player, and the usual shortcuts control it: play/pause, all the jumps, 0–9, speed (snapped to the speeds YouTube offers), reset speed, fullscreen and bookmarks. Frame step pauses and moves 1/30 s, but YouTube may only show the nearest frame it can decode. The quality menu and our Cast button are hidden: use the YouTube player's own settings and Cast button. If you click inside the YouTube player, YouTube's own keys apply until you click outside it. If YouTube refuses to play a video (removed, private, embedding disabled, or a local `file://` page), a message with an **Open on YouTube** link is shown.
- **Touch gestures** (phones and tablets): double-tap the left or right side of the video to go back or forward 10 s (each further quick tap adds another 10 s), double-tap the middle for full screen, and press and hold to play at 2× until you let go (holding does nothing while paused). The bottom of the video is left to the player's own controls. On YouTube videos the gestures start once the video is playing, and a single tap there plays or pauses.

The page looks up the stream URL for a broadcast ID through Hudl's own viewer endpoint (`vcloud.hudl.com/api/viewer/app/rss`, JSONP), and lists and searches games with `vcloud.hudl.com/api/viewer/broadcast` (JSONP; search uses its `title`, `section_id`, `after` and `before` parameters, the same ones BlueFrame's own widget sends). **These endpoints are undocumented and Hudl could change or remove them at any time**; if lookups start failing, that is the likely cause. Pasting a direct `.m3u8` URL still works regardless. Only the stream URL, title, date and status are kept from the lookup response.

## Links and bookmarks

- `?src=<link or ID>&t=<seconds>` loads a game and starts there; `?site=<slug>` opens the school's game list.
- **Address bar time:** when the page runs at its own URL (https://film.origas.org, a local file or another static host), the address bar's `t=` changes only while the game is paused (on pause, at the end, and after seeking or frame-stepping while paused), so it stays still and is easy to copy during playback. Reloading the page or going back to it resumes where you were, even mid-playback: the tab remembers the live position per game (sessionStorage). A link with its own `t=` always goes to that time.
- **Copy link** copies a resume link at the live time. Inside an embedded frame (such as an artifact page) it copies a timestamp like `4679968 @ 1:23:20` instead; paste that into the **Find a game** box to resume.
- **Bookmarks** are saved per game in this browser's localStorage (not synced between machines). Click a time to seek and type a note next to it.
- **Order:** drag a bookmark by its grip (the dotted handle on the left; works with a mouse or a finger) to put the list in any order, or focus the grip and press Up / Down. New marks go in by time, and when the list is out of time order a **Sort by time** button appears next to **+ Mark**.
- **Offense / defense:** the **O/D** button on each bookmark tags it as **O**ffense or **D**efense (click again to change or clear). Once anything is tagged, **All / Offense / Defense** buttons (with counts) appear above the list to show only one kind. While filtered, **M** tags new marks with that kind, and the link icon copies a link with only the bookmarks shown. The filter resets when you load another game.
- **Sharing bookmarks:** the link icon in the bookmarks panel (**Copy link with bookmarks**) copies a link that opens this game with all your bookmarks (times, notes, tags and order) included. The bookmarks travel in the part of the link after `#`, which is never sent to a server. With no bookmarks it copies a plain link to the game at the current time. Opening such a link shows them under **Shared with you (not saved)**, separate from **My bookmarks**. Nothing is saved automatically, so a shared link can never overwrite anyone's own bookmarks. Shared bookmarks you already have (same time and note) are left out of that list, and a line under it says how many. Use the save icon on a shared bookmark to add a copy to your bookmarks; it then drops out of the shared list. The shared list stays while that game is loaded (a reload keeps it) and goes away when you load another game. A link with 30 typical bookmarks is about 500 characters.
- **Panel size:** drag the left edge of the bookmarks/shortcuts panel to resize it (or focus the edge and use the arrow keys; double-click resets). The size is remembered. On narrow screens the panel sits below the video and isn't resizable.

## Casting (Chromecast / Google TV)

Use https://film.origas.org (or another `https://` address) to cast Hudl games. In Chrome or Edge, a **Cast** button appears in the control bar when a Cast device is found. It plays the current game on the TV, starting where you were, and pauses the page. While casting:

- The shortcuts and the bookmark list control the TV: play/pause, seeking, 0 to 9 jumps, and bookmarks (M marks the TV's current time). Frame step is off. Speed changes are sent to the TV, but the default Cast player may ignore them. If it does, the page says so.
- The video area shows "Casting to *device*" with the TV's time, and the address bar's `t` follows the TV when it pauses.
- Loading another Hudl game plays it on the TV. Loading a YouTube video stops casting (use the YouTube player's own Cast button).
- **Stop casting** (or stopping from the TV or Chrome) resumes playback here at the TV's position.

Older (legacy) games are cast from their H.264 variant stream, because Hudl's legacy playlist address can't be read by the TV.

**Opened as a local file?** Chrome may not find Cast devices for a `file://` page. If no Cast button appears, click the small **Cast?** note for options: open it from https://film.origas.org instead, or use Chrome's ⋮ menu > **Cast...** to mirror the tab.

## Beta

**https://film.origas.org/beta/** (`beta/index.html`) is where changes are tried out before they reach the main site. Its page is labelled "beta" (in the tab title and a small tag in the header), and it's the same as the main site until the next change is tried out there.

Links work the same way there, e.g. `https://film.origas.org/beta/?src=4679968&t=5000`. Bookmarks, recent schools and panel settings are shared between the two, since they're on the same site.

## Shortcuts

| Key | Action |
| --- | --- |
| Space | Play / pause |
| ← / → | Back / forward 5 s |
| J / K | Back / forward 10 s |
| Shift + ← / → | Back / forward 30 s |
| , / . | Step one frame back / forward (~1/30 s, pauses; off while casting; approximate on YouTube) |
| ↓ / ↑ (or [ / ]) | Slower / faster (0.25x to 2x) |
| \ | Reset speed to 1x |
| 0 to 9 | Jump to 0% to 90% |
| M | Bookmark current time (type a note, Enter to finish) |
| F | Fullscreen |
| B | Hide / show the bookmarks and shortcuts panel (remembered; also the chevron button at the top of the panel) |
| / | Open **Find a game** and put the cursor in its box |

Shortcuts are ignored while you type in a text field. While casting they control the TV.
