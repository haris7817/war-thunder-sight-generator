# War Thunder Sight Generator

A Windows desktop app that imports artwork (PNG/JPG), auto-traces it into vector
geometry, generates basic shading, lets you correct and move/scale/rotate the
result, and exports a valid War Thunder custom sight (`.blk`).

The goal is **not** perfect reproduction — it is to remove most of the manual
tracing work done in the WTDraw web editor and let you fix the rest by hand.

## Status

Feature-complete MVP. See [docs/USER_GUIDE.md](docs/USER_GUIDE.md) for how to use it and
[docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) for common issues.

## For end users

Unzip the delivered build and run `WarThunderSightGenerator.exe` — no Python required.
Then follow the [User Guide](docs/USER_GUIDE.md).

## Requirements

- Windows 10/11
- Python 3.12 or 3.13 (for development)

## Development setup

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e .[dev]
pytest
python -m app.main
```

> On a machine with a global `PYTHONHOME` set to another Python, prefix source commands
> with `$env:PYTHONHOME=$null; $env:PYTHONNOUSERSITE=1;` (see TROUBLESHOOTING). The
> packaged `.exe` is unaffected.

## Building the Windows executable

```powershell
.\.venv\Scripts\Activate.ps1
python scripts/build_windows.py
```

Produces `dist/WarThunderSightGenerator/` (onedir). Zip that folder for delivery. Build
config lives in `app.spec` (icon, version, bundled `template.blk`, excluded modules).

## Project layout

```
app/
  domain/          # pure data model + validation (no I/O, no Qt)
  application/     # orchestration services
  processing/      # image import, thresholding, tracing, shading
  blk/             # War Thunder .blk parsing/export + coordinate mapping
  infrastructure/  # logging, config, filesystem helpers
  ui/              # PySide6 widgets, panels, tools, canvas
  utils/           # small math helpers
scripts/           # CLI tools: analyze_blk, prototype, export_demo
tests/             # unit / golden / integration
client_samples/    # gitignored; client artwork + reference sights
```

## Installing a generated sight in-game

Copy the exported `.blk` to:

```
Documents\My Games\WarThunder\Saves\<user ID>\production\UserSights\<vehicle_id or all_tanks>\sight_1.blk
```

Enter a test drive and press **Alt+F9** to reload the sight without restarting the game.

## License / attribution

Format knowledge is derived from public documentation and the MIT-licensed
`ShubbeLeontij/sightgenerator` project. No code is copied from all-rights-reserved
or GPL sources.
