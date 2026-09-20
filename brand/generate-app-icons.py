#!/usr/bin/env python3
"""
Generate every icon and splash size the two stores ask for, from `brand/`.

Run: python brand/generate-app-icons.py
Output: brand/generated/  (regenerable, so it need not be hand-maintained)

Two rules drive most of what is here, and both are rejection causes rather
than preferences:

1. **Apple's 1024 marketing icon must have no alpha channel.** A transparent
   PNG is rejected at upload, not at review, which is a confusing place to
   discover it. The dark mark is already RGB, and anything with alpha is
   flattened onto the brand background rather than onto white.
2. **Android's adaptive icon is masked by the launcher**, which may crop it to
   a circle. Only the centre 66% of the 108dp canvas is guaranteed visible, so
   the mark is inset inside the safe zone instead of filling the square — an
   icon that fills it loses its edges on most devices.
"""

import pathlib
import sys

try:
    from PIL import Image
except ImportError:
    sys.exit("Pillow is required: pip install Pillow")

BRAND = pathlib.Path(__file__).parent
OUT = BRAND / "generated"

SOURCE_OPAQUE = BRAND / "lumos-mark-1024-dark.png"
SOURCE_ALPHA = BRAND / "lumos-mark-1024-transparent.png"


def brand_background() -> tuple:
    """
    The artwork's own background, read from its corner.

    Hardcoding this is how you end up with two nearly-identical darks: the
    first attempt here guessed #0B0F19 while the mark is actually #0A0B12,
    a difference invisible in isolation and obvious as a seam once a padded
    icon sits next to an unpadded one.
    """
    return Image.open(SOURCE_OPAQUE).convert("RGB").getpixel((2, 2))


BACKGROUND = brand_background()


def flatten(image: Image.Image) -> Image.Image:
    """RGBA onto the brand background — never onto white, never left alpha."""
    if image.mode != "RGBA":
        return image.convert("RGB")
    canvas = Image.new("RGB", image.size, BACKGROUND)
    canvas.paste(image, mask=image.split()[3])
    return canvas


def resize(image: Image.Image, size: int) -> Image.Image:
    return image.resize((size, size), Image.LANCZOS)


def write(image: Image.Image, name: str) -> None:
    path = OUT / name
    path.parent.mkdir(parents=True, exist_ok=True)
    image.save(path, "PNG", optimize=True)
    print(f"  {name:44} {image.size[0]}x{image.size[1]} {image.mode}")


def main() -> None:
    OUT.mkdir(exist_ok=True)
    opaque = flatten(Image.open(SOURCE_OPAQUE))
    alpha = Image.open(SOURCE_ALPHA).convert("RGBA")

    print("iOS")
    # Xcode 14+ takes a single 1024 and derives the rest, but the marketing
    # icon is uploaded separately and is the one that must be alpha-free.
    write(opaque, "ios/AppIcon-1024.png")
    for size in (180, 167, 152, 120, 87, 80, 76, 60, 58, 40, 29, 20):
        write(resize(opaque, size), f"ios/AppIcon-{size}.png")

    print("Android")
    # Play Store listing icon: 512, alpha permitted here.
    write(resize(alpha, 512), "android/play-store-icon-512.png")
    # Adaptive icon: 108dp canvas, only the centre 72dp is safe from masking.
    for density, size in (("mdpi", 108), ("hdpi", 162), ("xhdpi", 216),
                          ("xxhdpi", 324), ("xxxhdpi", 432)):
        canvas = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        safe = int(size * 0.66)
        mark = alpha.resize((safe, safe), Image.LANCZOS)
        offset = (size - safe) // 2
        canvas.paste(mark, (offset, offset), mark)
        write(canvas, f"android/mipmap-{density}/ic_launcher_foreground.png")
        write(Image.new("RGB", (size, size), BACKGROUND),
              f"android/mipmap-{density}/ic_launcher_background.png")
    # Legacy square launcher icon for pre-adaptive devices.
    for density, size in (("mdpi", 48), ("hdpi", 72), ("xhdpi", 96),
                          ("xxhdpi", 144), ("xxxhdpi", 192)):
        write(resize(opaque, size), f"android/mipmap-{density}/ic_launcher.png")

    print("Splash")
    # One oversized square, letterboxed by the native splash plugin at every
    # aspect ratio. Sizing per-device is a losing game; a centred mark on a
    # flat background is not.
    for name, size in (("splash-2732.png", 2732), ("splash-1200.png", 1200)):
        canvas = Image.new("RGB", (size, size), BACKGROUND)
        mark_size = int(size * 0.28)
        mark = alpha.resize((mark_size, mark_size), Image.LANCZOS)
        pos = (size - mark_size) // 2
        canvas.paste(mark, (pos, pos), mark)
        write(canvas, f"splash/{name}")

    print("PWA")
    for size in (192, 512):
        write(resize(alpha, size), f"pwa/icon-{size}.png")
    # NOTE: no separate maskable PWA icon. The existing web icons already
    # leave the mark at ~40% of the canvas, comfortably inside the 66% safe
    # zone, so a circular mask never reaches it — rendering both under a mask
    # side by side shows the "fixed" version is simply smaller. The inset
    # below is for ANDROID ADAPTIVE icons, where the launcher scales the
    # foreground layer up and the safe zone is real.
    write(resize(opaque, 180), "pwa/apple-touch-icon.png")

    print(f"\nDone → {OUT.relative_to(BRAND.parent)}")


if __name__ == "__main__":
    main()
