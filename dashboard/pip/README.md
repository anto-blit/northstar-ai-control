# Pip integration

`source.html` is a byte-for-byte copy of the user's supplied
`Pip breaks the rules_ Ten to Zero cartoons.html`. Do not edit its content.
`test_pip.py` pins its SHA-256. The build reuses its complete scene, caption,
duration, explanatory-text and Web Audio definitions verbatim.

The homepage places episode 1 by TPS2, episode 2 by the reproducer commands,
and episode 3 in the open accountability section before the recipe.
The standalone sharing routes supplement those inline placements.

- `watch/player.html?ep=1&embed=1`: compact embed; `ep` accepts 1–3.
- `watch/holding-message/`, `watch/wrong-label/`, `watch/too-easy-test/`:
  share pages with PNG previews and server-rendered caption transcripts.
- `watch/too-easy-test/#verdict`: paused scene deep link; clicking plays with sound.
- `watch/player.html?ep=3&format=vertical`: 9:16 layout with a browser video
  exporter. It retains every scene and caption at the original running time.
  Download produces 1080×1920 MP4 where supported, otherwise WebM, with
  synthesized audio and captions burned into the frame. The illustration,
  title and captions are laid out separately; the illustration is never cropped.
  Keep the tab visible for the full episode. Stopping early saves a partial clip.

Episodes run 77.5, 79.5 and 103 seconds. The requested “60-second” invitation
is retained; the player displays the actual duration. No scenes were shortened.

## Funnel events

The parent validates iframe sender, origin and episode before forwarding:

```js
window.addEventListener('northstar:pip', ({detail}) => {
  // detail.event: play | finish | evidence_click
  // detail.episode: 1 | 2 | 3
  // detail.scene, watchedSeconds, durationSeconds, placement
});
```

These also enter `window.dataLayer` as `pip_play`, `pip_finish`,
`pip_evidence_click`. Connect these to the site's chosen analytics collector.
No analytics service is configured and aggregate visitor measurement is not
yet running. The integration sends no network telemetry, cookies or identifiers.
`finish` means playback reached the end; use `watchedSeconds` to distinguish
watching the full episode from skipping to its final scene. Pauses do not count
as another play; restarting does. Below-player evidence clicks use placement
`below_player` and need not have a preceding play.

## Offline validation

```sh
node dashboard/build_styles.mjs
python dashboard/build_dashboard.py
python -m unittest discover -s dashboard -p 'test_*.py'
node dashboard/pip_browser_check.cjs
python dashboard/build_dashboard.py --check
```

`node dashboard/pip_browser_check.cjs --previews` also regenerates the three
1200×630 PNG previews from the actual SVG scenes in headless Chrome. Rebuild
afterwards to publish them. Chrome and Node 22+ are required for browser checks.
All these checks run locally and make no model calls.
