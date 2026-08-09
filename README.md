# War Thunder Sight Generator

A Windows desktop app that imports artwork (PNG/JPG), auto-traces it into vector
geometry, generates basic shading, lets you correct and move/scale/rotate the
result, and exports a valid War Thunder custom sight (`.blk`).

The goal is **not** perfect reproduction — it is to remove most of the manual
tracing work done in the WTDraw web editor and let you fix the rest by hand.

## Status

Under active development. See milestones in the delivery plan.

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
