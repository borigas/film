# Game Film Viewer (beta)

Served at **https://film.origas.org/beta/**. It is the main viewer (see `../README.md`) plus the features below. Keyboard shortcuts, bookmarks, Copy link, Cast and the Hudl Browse/search are unchanged. Deep links work here too, e.g. `https://film.origas.org/beta/?src=4679968&t=5000` or `?site=mountmarty`.

## Men's Basketball first

Every Hudl game list (Browse, a picked school, Union games, `?site=` links) opens with **Sport** set to **Men's Basketball**, for both Live & upcoming and Recent games. Pick **All sports** or another sport in the menu to switch. If a school has no Men's Basketball games, the list says so and shows all sports instead. Men's Basketball also includes games filed under the generic "Basketball" sport (as Mount Marty does), except ones whose title says women's (Women's, Lady, WBB, (W) ...) without also saying men's. Because of that filter, the archived count is shown as "up to N" when it can't be exact. Pick **Basketball** in the menu to see the generic sport on its own.

## Game date

The header (and the browser tab title) shows the game's date next to its name and source, e.g. `Mount Marty vs Union · Oct 26, 2026, 5:00 PM · Hudl (mountmarty)`. Hudl dates and times come from the broadcast, in your time zone. YouTube gives no date, so the viewer uses a date written in the video title. If there isn't one and the video was picked from a channel list, it shows an approximate date from "Streamed 3d ago", marked with `~`. Otherwise no date is shown.

## Game list folds away

Picking a game from a list (a school's Hudl games, Union games or a YouTube list) folds the list away so the video gets the space. **▾ Games: …** brings it back exactly as it was: same school, tab, sport, search, loaded pages and scroll position. The list's **Close** closes it fully.

## Panel size

Drag the left edge of the bookmarks/shortcuts panel to resize it (or focus the edge and use the arrow keys; double-click resets). The size is remembered. On narrow screens the panel sits below the video and isn't resizable.

## School search

Type in the **School** box. Matches come from a built-in directory of 229 schools (Union Adventist, its opponents and their opponents). Case and punctuation don't matter. Partial words, word starts and initials all match, e.g. `Bellevue`, `neb wes`, `occ` (Ozark Christian College) and `Ozark`. Union and its opponents are listed first. Each result shows the state and badges: **Hudl** (or Hudl stale/none), **YouTube**, or another platform.

- Pick a school with a Hudl site to open its game list, with the usual search, sport filter and **Load more**.
- If it has a YouTube channel, a **YouTube** button switches to its recent videos (and **Hudl games** switches back).
- If a school isn't in the directory, the box searches Hudl's own list of sites, so any school on Hudl can still be found. **Search all Hudl schools for "…"** at the end of the list does the same on demand.

The directory is generated from `directory/schools.json`: run `python -I directory/export_viewer.py` to refresh the copy inlined in `beta/index.html` (between `/*SCHOOLS-START*/` and `/*SCHOOLS-END*/`).

## Union games

**Union games** lists every Hudl game with "Union" in its title across Union's Hudl site and the Hudl sites of all of Union's opponents in the directory, newest first, with the same search, sport filter and **Load more**. **Union YouTube** shows Union's channel (@unionadventistlive).

## YouTube

Paste a YouTube link into the top box: `watch?v=`, `youtu.be/`, `/live/`, `/shorts/`, `/embed/` (an `<iframe>` snippet works), with an optional `t=` or `start=` time. A bare ID needs a prefix: `yt:VIDEOID`. Hudl links still take priority.

The video plays in YouTube's player, and the usual shortcuts control it: play/pause, all the jumps, 0–9, speed (snapped to the speeds YouTube offers), reset speed, fullscreen, bookmarks (kept separately from Hudl games) and Copy link. Frame step (`,` `.`) pauses and moves 1/30 s, but YouTube may only show the nearest frame it can decode. The quality menu and our Cast button are hidden: use the YouTube player's own settings and Cast button. If you click inside the YouTube player, YouTube's own keys apply until you click outside it.

If YouTube refuses to play a video (removed, private, embedding disabled, or opened as a local `file://` page, which YouTube blocks), a message with an **Open on YouTube** link is shown.

**Channel lists are fragile.** YouTube offers no key-free feed (its RSS feeds currently return errors), so the list is read from the channel's public **Live streams** or **Videos** page, fetched through the same undocumented Hudl proxy the viewer uses for game lookups. YouTube's page only includes the most recent ~30 videos. If YouTube changes that page or Hudl changes the proxy, the list fails with a link to open the channel on YouTube instead.
