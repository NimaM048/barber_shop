"""Build crisp logo-signature assets from generated sharp lockup."""
from pathlib import Path
import numpy as np
from PIL import Image, ImageFilter

SRC = Path(
    r"C:\Users\Admin\.cursor\projects\c-Users-Admin-Desktop-berber-shop\assets\logo-signature-sharp.png"
)
OUT = Path(r"C:\Users\Admin\Desktop\berber_shop\static\images\brand")


def to_transparent_ivory(im: Image.Image) -> Image.Image:
    arr = np.asarray(im.convert("RGBA"), dtype=np.float32)
    rgb = arr[..., :3]
    lum = 0.2126 * rgb[..., 0] + 0.7152 * rgb[..., 1] + 0.0722 * rgb[..., 2]

    alpha = np.zeros_like(lum)
    # Soft threshold for clean edges
    alpha = np.clip((lum - 40.0) / 55.0, 0.0, 1.0) * 255.0

    out = np.zeros_like(arr)
    out[..., 0] = 247
    out[..., 1] = 244
    out[..., 2] = 239
    out[..., 3] = alpha
    return Image.fromarray(out.astype(np.uint8), "RGBA")


def trim_pad(im: Image.Image, pad_ratio: float = 0.05) -> Image.Image:
    bbox = im.getbbox()
    if not bbox:
        return im
    im = im.crop(bbox)
    px = max(12, int(im.width * pad_ratio))
    py = max(12, int(im.height * pad_ratio))
    canvas = Image.new("RGBA", (im.width + px * 2, im.height + py * 2), (0, 0, 0, 0))
    canvas.paste(im, (px, py), im)
    return canvas


def main() -> None:
    raw = Image.open(SRC)
    print("source", raw.size)
    im = trim_pad(to_transparent_ivory(raw))
    # Mild sharpen on alpha edges without inventing pixels
    im = im.filter(ImageFilter.UnsharpMask(radius=1.2, percent=120, threshold=2))
    print("processed", im.size)

    # 2x retina master (~3k class) — avoid empty 4k upscale that softens strokes
    target_w = max(im.width, 2560)
    if im.width < target_w:
        scale = target_w / im.width
        im = im.resize((target_w, int(im.height * scale)), Image.Resampling.LANCZOS)
        im = im.filter(ImageFilter.UnsharpMask(radius=0.8, percent=90, threshold=2))
    print("master", im.size)

    png = OUT / "logo-signature.png"
    webp = OUT / "logo-signature.webp"
    webp4k = OUT / "logo-signature-4k.webp"

    im.save(png, optimize=True)
    im.save(webp4k, "WEBP", quality=96, method=6)

    hero_w = 1920
    hero = im.resize((hero_w, int(im.height * hero_w / im.width)), Image.Resampling.LANCZOS)
    hero = hero.filter(ImageFilter.UnsharpMask(radius=0.7, percent=85, threshold=2))
    hero.save(webp, "WEBP", quality=94, method=6)

    print("png", png.stat().st_size, Image.open(png).size)
    print("webp", webp.stat().st_size, hero.size)
    print("webp4k", webp4k.stat().st_size, im.size)


if __name__ == "__main__":
    main()
