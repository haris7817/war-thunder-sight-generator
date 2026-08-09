# War Thunder Sight Generator — User Guide

Turn artwork into a War Thunder custom sight (`.blk`): import an image, auto-trace it
to line geometry, add shading, tidy it up by hand, and export. The goal is to remove
most of the manual tracing — you clean up the rest.

## 1. Launch

Unzip the delivered folder anywhere and run **`WarThunderSightGenerator.exe`**. No
installation, no Python needed. The first launch may take a few seconds.

## 2. The window

- **Left rail** — tools: **Select ▶**, **Draw line ✎**, **Erase ⌫**.
- **Middle** — the canvas, with faint centre guides marking the sight's aim point (origin).
- **Right panel** — **SOURCE**, **TRACE**, **SHADING**, **TRANSFORM**, and a pinned **Export** footer.
- **Bottom** — status line: `lines N · quads N · zoom N%`.

## 3. Navigate the canvas

- **Zoom**: mouse wheel (zooms around the cursor).
- **Pan**: hold **Spacebar** and drag, **or** drag with the **Select ▶** tool, **or** middle-mouse drag.

## 4. Workflow

1. **SOURCE → Import image…** — pick a PNG/JPG. Transparent art is flattened onto white.
   - The **Otsu / Global / Adaptive** chips + **Threshold** slider let you preview how the
     image binarises. (Tracing uses edge detection, so this is mainly for inspection.)
2. **TRACE** — pick a preset (**Fast / Balanced / High**) or set **Detail**, then click
   **Re-trace**. Blue lines appear over the artwork.
   - Higher detail = more, finer segments. Very detailed art can produce thousands of
     lines (that's normal — the game handles it).
3. **SHADING** *(optional)* — raise **Intensity** above 0 to fill solid dark areas and add
   hatching for mid-tones. Set it to 0 to turn shading off entirely.
4. **Tidy up** — use **Draw line ✎** to add missing strokes and **Erase ⌫** to remove
   stray lines (click or drag). **Ctrl+Z** undoes your last draw/erase.
   - **Your manual edits survive a Re-trace** — only the auto-traced lines are regenerated.
5. **TRANSFORM** — nudge **Offset X/Y**, **Scale**, **Rotation** to position the artwork
   relative to the aim point. **Reset** returns to default. The canvas updates live.
6. **Export .blk** — choose where to save. A confirmation appears with **Open folder**.

## 5. Install the sight in-game

Copy the exported file to (create folders if missing):

```
Documents\My Games\WarThunder\Saves\<your user ID>\production\UserSights\all_tanks\sight_1.blk
```

- Use `all_tanks` for every vehicle, or a specific `<vehicle_id>` folder for one vehicle.
- Enter a **tank test drive**, then press **Alt+F9** to (re)load the sight — no need to
  restart the game. Repeat Alt+F9 after each new export.

## 6. Tips

- **Lead with clean line-art** for the best auto-trace; painterly/colour images trace as
  approximate outlines you then refine by hand.
- If the whole sight looks shifted or the wrong size in-game, adjust **TRANSFORM** and
  re-export — you don't need to re-trace.
- Logs are written to `logs\app.log` next to the executable if you need to report a problem.
