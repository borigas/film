# Game Film Viewer (beta)

Served at **https://film.origas.org/beta/**, the test bed for upcoming changes. It is the main viewer (see `../README.md` for everything it does) with the changes below. Deep links work here too, e.g. `https://film.origas.org/beta/?src=4679968&t=5000`, `?site=mountmarty`, or a shared `#bm=` bookmark link.

## Compact header

The header is a single slim bar while you watch, so the video gets the space.

- **The bar:** the game's name, date and source on the left (truncated, with the full text on hover), a small **beta** tag, and **Find a game** on the right. Notices and errors still appear just under the bar.
- **Find a game** (or the **/** key) opens the finder. It also opens by itself when no game is loaded.
- **One box:** type a school name, or paste a game link, broadcast ID, `.m3u8` URL, YouTube URL or a `4679968 @ 1:23:20` timestamp, then press Enter or **Go**.
  - A game link loads the game.
  - Anything else is a school search, with the same typeahead as before: the school directory first, then Hudl's own site list, and **Search all Hudl schools for "…"**.
  - A bare number is a broadcast ID. A `yt:VIDEOID` is a YouTube video.
- **Quick chips** under the box: **Union games**, **Union YouTube**, and up to 4 recently opened schools or Hudl sites. Click × to remove one from the recent list.
- **The game list** opens under the chips and works as before: Hudl/YouTube tabs, Sport (Men's Basketball first), search, dates and **Load more**. Its **Close** closes just the list.
- **Folding:** picking or loading a game, pressing Escape (while a game is loaded), or clicking **Find a game** again folds it back to the slim bar. Clicking elsewhere on the page leaves it open. **Find a game** brings it back exactly as it was: box text, school, tab, sport, search, loaded pages and scroll position.

The separate paste box, the **Hudl site** box with **Browse**, and the **▾ Games:** bar are gone. Their jobs are done by the one box, the chips and **Find a game**. `?site=<slug>` links still open a Hudl site's game list.

All shortcuts work as before. **/** is new and only opens the finder.
