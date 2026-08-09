# War Thunder Sight Generator — User Guide

Turn artwork into a War Thunder custom sight (`.blk`): import an image, auto-trace it to line geometry, add shading, tidy it up by hand, and export. The goal is to remove most of the manual tracing — you clean up the rest.

## 1. Launch

Unzip the delivered folder anywhere and run `WarThunderSightGenerator.exe`. No installation, no Python needed. The first launch may take a few seconds.

## 2. The window

- **Left rail** — tools: Select (arrow), Draw line (pencil), Erase (eraser).
- **Middle** — the canvas, with faint centre guides marking the sight's aim point (origin).
- **Right panel** — Source, Tracing, Shading, Transform, and a pinned Export section.
- **Bottom** — status line: `lines N · quads N · zoom N%`.

## 3. Navigate the canvas

- **Zoom** — mouse wheel (zooms around the cursor).
- **Pan** — hold Spacebar and drag, or drag with the Select tool, or middle-mouse drag.

## 4. Workflow

1. **Import** (Source → Import PNG / JPG) — pick a PNG/JPG; transparent art is flattened onto white. The Otsu / Global / Adaptive chips and Threshold slider preview how the image binarises (mainly for inspection; tracing uses edge detection).
2. **Trace** (Tracing → Re-trace) — choose a preset (Fast / Balanced / High) or set Detail, then click Re-trace; blue lines appear over the artwork. Higher detail means more, finer segments — very detailed art can produce thousands of lines, which is normal.
3. **Shade** (optional) — in Shading, raise Intensity above 0 to fill solid dark areas and add hatching for mid-tones; set it to 0 (pill shows OFF) to disable shading.
4. **Tidy up** — use Draw line to add missing strokes and Erase to remove stray segments (click a segment, or drag across several). Press Ctrl+Z to undo. Your manual edits survive a Re-trace — only the auto-traced lines are regenerated.
5. **Position** (Transform) — nudge Offset X/Y, Scale, and Rotation to place the artwork relative to the aim point; Reset returns to default. The canvas updates live.
6. **Export** — click Export .blk and choose where to save. A confirmation appears with an Open folder button.

## 5. Install the sight in-game

Copy the exported file to (create the folders if missing):

```
Documents\My Games\WarThunder\Saves\<your user ID>\production\UserSights\all_tanks\sight_1.blk
```

- Use `all_tanks` for every vehicle, or a specific `<vehicle_id>` folder for one vehicle.
- Enter a tank test drive, then press Alt+F9 to (re)load the sight — no game restart needed. Press Alt+F9 again after each new export.

## 6. Tips

- Lead with clean line-art for the best auto-trace; painterly or colour images trace as approximate outlines that you refine by hand.
- If the whole sight looks shifted or the wrong size in-game, adjust Transform and re-export — you do not need to re-trace.
- Logs are written to `logs\app.log` next to the executable if you need to report a problem.
