# Cropping utility

A lightweight Python CLI (`tools/cropper.py`) that can crop one or many images at once. It supports cropping by explicit bounding box or by width/height with a chosen gravity (center, top-left, top-right, bottom-left, bottom-right).

## Requirements
- Python 3.9+
- [Pillow](https://python-pillow.org/): `python -m pip install -r tools/requirements.txt`

If your network uses a proxy, ensure it allows access to PyPI or configure `--proxy` for `pip`.

## Usage
Crop every PNG/JPG/BMP/TIFF/WEBP in a folder to the largest possible centered square (no arguments needed beyond the folder):

```bash
python tools/cropper.py ./shots
```

Crop using an explicit box on a single image:

```bash
python tools/cropper.py ./shots/example.png --box 100 200 700 800
```

Additional options:
- `--gravity {center,top-left,top-right,bottom-left,bottom-right}` to align the crop before applying offsets.
- `--offset-x` / `--offset-y` to nudge the crop after alignment.
- `--suffix` to customize the filename suffix when writing to the output directory.
- `--overwrite` to replace the original image instead of writing to `--output`.
- `--no-auto-square` to disable the default centered square crop and instead require `--width/--height` or `--box`.

Supported input formats: png, jpg/jpeg, bmp, tiff, webp.
