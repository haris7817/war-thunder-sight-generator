# Troubleshooting

## The app won't start / closes immediately

- Check `logs\app.log` next to `WarThunderSightGenerator.exe` for the error.
- Make sure you unzipped the whole folder (the `.exe` needs the files beside it) — running it from inside the zip will not work.
- Windows SmartScreen may warn on first run (unsigned app): click More info, then Run anyway.

## A "missing DLL" dialog appears

- The build is self-contained; this usually means the folder was only partially copied. Re-unzip the full folder and run again.

## The exported sight doesn't show in-game

- Confirm the exact path and filename: `Documents\My Games\WarThunder\Saves\<user ID>\production\UserSights\all_tanks\sight_1.blk`.
- In a tank test drive, press Alt+F9 to reload; selecting the sight in the game's sight settings can also help.
- The whole file fails to load if it's malformed. This app always writes valid syntax, but if you hand-edit the `.blk`, a single wrong value (a stray letter, or scientific notation like `1e-05`) makes the game silently ignore the entire file.

## The artwork is shifted / too big / rotated in-game

- Use the Transform panel (Offset X/Y, Scale, Rotation) and re-export — no re-trace needed. The coordinate mapping has been verified in-game (isotropic, no Y-flip).

## The trace is too noisy or too sparse

- Lower Detail (or use the Fast preset) for fewer, cleaner lines; raise it for more detail.
- Use the Erase tool to remove stray segments and Draw to add missing ones.
- A "too many elements" note in the log means the trace is very dense; lower Detail. The game tolerates several thousand elements, but denser sights are slower to edit.

## Shading fills the whole background

- Shading only fills interior dark regions (background touching the image edge is excluded). If fills look wrong, lower Intensity or set it to 0 to disable shading.

## Developer note: running from source fails with "SRE module mismatch"

- This machine has a global `PYTHONHOME` variable pointing at another Python, which breaks source runs (not the packaged `.exe`). Remove that variable (System → Environment Variables → delete `PYTHONHOME`), or launch with it cleared:

```
$env:PYTHONHOME=$null; $env:PYTHONNOUSERSITE=1; .\.venv\Scripts\python.exe -m app.main
```

The packaged executable is unaffected by this.
