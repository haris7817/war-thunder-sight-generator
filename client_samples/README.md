# Client samples (gitignored)

This directory holds the client's artwork and reference sights. **Nothing here is
committed to git** (see `.gitignore`) — the client's artwork never enters version
history. Only this manifest is tracked.

Place samples on disk in this layout before running the analysis/prototype scripts:

```
client_samples/
  Remielle/
    input.png        # source artwork (color, dark background)
    reference.blk    # client's finished hand-traced sight
  Acherona/
    input.png        # source artwork (color, black background, red umbrella)
    reference.blk
  Faye_Spike/
    input.png        # source artwork (grayscale line-art, white background)
    reference.blk
```

## Provenance (as received 2026-08-09)

Reference sights were received as `.txt` files in `E:\Downloads` and should be
renamed to `reference.blk`:

| Vehicle    | Reference source file      | Notes                                   |
|------------|----------------------------|-----------------------------------------|
| Remielle   | `Remielle.txt`  (778 KB)   | color painting, dark background         |
| Acherona   | `Acherona.txt`  (410 KB)   | color, black background, red umbrella   |
| Faye_Spike | `Faye_Spike_left.txt` (639 KB) | grayscale line-art, white background |

Source artwork images were provided by the client via chat on the same date; save
each as `input.png` in the matching folder.

## Characteristics that drive tracing

- **Faye_Spike** — clean grayscale line-art on white → the easy case; use for demos.
- **Remielle / Acherona** — color paintings on dark backgrounds with soft edges →
  require background-polarity inversion + adaptive threshold + Canny; expect dense
  geometry that approaches (not equals) the artwork.
