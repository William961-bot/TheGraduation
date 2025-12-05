"""
A small CLI utility to crop images in bulk.

Features
- Supports cropping to an exact box or by width/height with alignment.
- Accepts single files or directories of images.
- Automatically creates the output directory and preserves file names.

Usage examples
--------------
Crop a centered 800x800 square from each image in `./shots` and write them to `./cropped`:

    python tools/cropper.py ./shots --width 800 --height 800 --output ./cropped

Crop using an explicit box (x0 y0 x1 y1) on a single file:

    python tools/cropper.py ./shot.png --box 100 200 700 800

Install Pillow if it is missing:

    python -m pip install -r tools/requirements.txt
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Tuple

from PIL import Image

SUPPORTED_SUFFIXES = {".png", ".jpg", ".jpeg", ".bmp", ".tiff", ".tif", ".webp"}


@dataclass
class CropJob:
    source: Path
    destination: Path
    box: Tuple[int, int, int, int]


@dataclass
class CropSettings:
    width: int | None
    height: int | None
    box: Tuple[int, int, int, int] | None
    gravity: str
    offset_x: int
    offset_y: int
    suffix: str
    overwrite: bool
    auto_square: bool


GRAVITY_OFFSETS = {
    "center": (0.5, 0.5),
    "top-left": (0.0, 0.0),
    "top-right": (1.0, 0.0),
    "bottom-left": (0.0, 1.0),
    "bottom-right": (1.0, 1.0),
}


def discover_images(path: Path) -> List[Path]:
    if path.is_dir():
        return [
            p
            for p in path.iterdir()
            if p.is_file() and p.suffix.lower() in SUPPORTED_SUFFIXES
        ]
    if path.is_file() and path.suffix.lower() in SUPPORTED_SUFFIXES:
        return [path]
    return []


def clamp(value: int, min_value: int, max_value: int) -> int:
    return max(min_value, min(value, max_value))


def compute_box(image: Image.Image, settings: CropSettings) -> Tuple[int, int, int, int]:
    if settings.box:
        return settings.box

    img_w, img_h = image.size

    if settings.auto_square and (settings.width is None or settings.height is None):
        crop_w = crop_h = min(img_w, img_h)
    else:
        if settings.width is None or settings.height is None:
            raise ValueError("width and height must be provided when box is not set unless --auto-square is used")
        crop_w = clamp(settings.width, 1, img_w)
        crop_h = clamp(settings.height, 1, img_h)

    gravity = settings.gravity.lower()

    if gravity not in GRAVITY_OFFSETS:
        raise ValueError(f"Unknown gravity '{settings.gravity}'")

    gx, gy = GRAVITY_OFFSETS[gravity]
    x0 = int(gx * (img_w - crop_w)) + settings.offset_x
    y0 = int(gy * (img_h - crop_h)) + settings.offset_y

    # Ensure the crop stays inside the image bounds.
    x0 = clamp(x0, 0, img_w - crop_w)
    y0 = clamp(y0, 0, img_h - crop_h)
    x1 = x0 + crop_w
    y1 = y0 + crop_h
    return x0, y0, x1, y1


def prepare_jobs(inputs: Iterable[Path], output_dir: Path | None, settings: CropSettings) -> List[CropJob]:
    if not settings.overwrite and output_dir is not None:
        output_dir.mkdir(parents=True, exist_ok=True)

    jobs: List[CropJob] = []
    for src in inputs:
        with Image.open(src) as image:
            box = compute_box(image, settings)
        destination = src if settings.overwrite else (output_dir / f"{src.stem}{settings.suffix}{src.suffix}")
        jobs.append(CropJob(source=src, destination=destination, box=box))
    return jobs


def crop(job: CropJob) -> None:
    with Image.open(job.source) as image:
        cropped = image.crop(job.box)
        cropped.save(job.destination)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Crop one or many images with a single command.")
    parser.add_argument("input", type=Path, help="Image file or directory to crop.")
    parser.add_argument("--output", type=Path, default=Path("cropped"), help="Directory where cropped images are written. Ignored when --overwrite is set.")
    parser.add_argument("--width", type=int, help="Width of the crop region. Required unless --box is provided or --auto-square is enabled.")
    parser.add_argument("--height", type=int, help="Height of the crop region. Required unless --box is provided or --auto-square is enabled.")
    parser.add_argument(
        "--box",
        type=int,
        nargs=4,
        metavar=("X0", "Y0", "X1", "Y1"),
        help="Explicit crop box. Overrides width/height/gravity settings.",
    )
    parser.add_argument(
        "--gravity",
        default="center",
        choices=list(GRAVITY_OFFSETS.keys()),
        help="Where to anchor the crop when using width/height.",
    )
    parser.add_argument("--offset-x", type=int, default=0, help="Horizontal offset applied after gravity alignment.")
    parser.add_argument("--offset-y", type=int, default=0, help="Vertical offset applied after gravity alignment.")
    parser.add_argument("--suffix", default="_cropped", help="Suffix appended to filenames.")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite the source image instead of writing to --output.")
    parser.add_argument(
        "--auto-square",
        action=argparse.BooleanOptionalAction,
        default=True,
        help=(
            "Automatically crop to the centered largest possible square when width/height are not provided. "
            "Use --no-auto-square to disable."
        ),
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    input_path: Path = args.input
    images = discover_images(input_path)

    if not images:
        raise SystemExit(f"No supported images found in {input_path}")

    settings = CropSettings(
        width=args.width,
        height=args.height,
        box=tuple(args.box) if args.box else None,
        gravity=args.gravity,
        offset_x=args.offset_x,
        offset_y=args.offset_y,
        suffix=args.suffix,
        overwrite=args.overwrite,
        auto_square=args.auto_square,
    )

    output_dir = None if args.overwrite else args.output
    jobs = prepare_jobs(images, output_dir, settings)

    for job in jobs:
        crop(job)
        print(f"Cropped {job.source} -> {job.destination} with box {job.box}")


if __name__ == "__main__":
    main()
