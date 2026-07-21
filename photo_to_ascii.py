from PIL import Image, ImageEnhance

# ── Config ──────────────────────────────────────────────────────────────────
INPUT_IMAGE = "pfp.jpeg"
OUTPUT_TXT = "ascii_output.txt"
OUTPUT_HTML = "ascii_colored.html"
COLUMNS = 80

# ASCII-only ramp (dark → light)
RAMP = " .:-=+*#%@"

# Aspect ratio correction
CHAR_ASPECT = 0.5

# Color theme for optional colorized output
COLORIZE = True
FG_COLOR = "#00d4ff"
BG_COLOR = "#0d1117"


def load_and_resize(path, columns):
    img = Image.open(path).convert("RGB")
    w, h = img.size
    new_w = columns
    new_h = int(h / w * new_w * CHAR_ASPECT)
    return img.resize((new_w, new_h), Image.LANCZOS)


def enhance_contrast(img, factor=1.5):
    return ImageEnhance.Contrast(img).enhance(factor)


def floyd_steinberg_dither(img, num_levels):
    gray = img.convert("L")
    w, h = gray.size
    pixels = gray.load()
    for y in range(h):
        for x in range(w):
            old = pixels[x, y]
            step = 255 / (num_levels - 1)
            new = round(old / step) * step
            new = max(0, min(255, new))
            pixels[x, y] = int(new)
            err = old - new
            if x + 1 < w:
                pixels[x + 1, y] = max(0, min(255, int(pixels[x + 1, y] + err * 7 / 16)))
            if x - 1 >= 0 and y + 1 < h:
                pixels[x - 1, y + 1] = max(0, min(255, int(pixels[x - 1, y + 1] + err * 3 / 16)))
            if y + 1 < h:
                pixels[x, y + 1] = max(0, min(255, int(pixels[x, y + 1] + err * 5 / 16)))
            if x + 1 < w and y + 1 < h:
                pixels[x + 1, y + 1] = max(0, min(255, int(pixels[x + 1, y + 1] + err * 1 / 16)))
    return gray


def pixels_to_ascii(img, ramp):
    pixels = img.load()
    w, h = img.size
    lines = []
    for y in range(h):
        line = ""
        for x in range(w):
            val = pixels[x, y]
            idx = int(val / 255 * (len(ramp) - 1))
            idx = max(0, min(len(ramp) - 1, idx))
            line += ramp[idx]
        lines.append(line)
    return lines


def wrap_pre(lines):
    return "<pre>\n" + "\n".join(lines) + "\n</pre>"


def wrap_colorized(lines, fg, bg):
    inner = []
    for line in lines:
        escaped = line.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        inner.append(f'<span style="color:{fg}">{escaped}</span>')
    return (
        f'<pre style="background:{bg};padding:10px;border-radius:8px;overflow-x:auto">\n'
        + "\n".join(inner)
        + "\n</pre>"
    )


def main():
    print(f"Loading {INPUT_IMAGE}...")
    img = load_and_resize(INPUT_IMAGE, COLUMNS)
    img = enhance_contrast(img, 1.5)
    print(f"Resized to {img.size[0]}x{img.size[1]} characters")

    num_levels = len(RAMP)
    print(f"Applying Floyd-Steinberg dithering ({num_levels} levels)...")
    dithered = floyd_steinberg_dither(img, num_levels)

    print(f"Mapping to ASCII ramp: {repr(RAMP)}")
    lines = pixels_to_ascii(dithered, RAMP)

    while lines and lines[0].strip() == "":
        lines.pop(0)
    while lines and lines[-1].strip() == "":
        lines.pop()

    plain = wrap_pre(lines)
    with open(OUTPUT_TXT, "w", encoding="utf-8") as f:
        f.write(plain)
    print(f"\nPlain ASCII saved to {OUTPUT_TXT}")

    if COLORIZE:
        colored = wrap_colorized(lines, FG_COLOR, BG_COLOR)
        with open(OUTPUT_HTML, "w", encoding="utf-8") as f:
            f.write(colored)
        print(f"Colorized HTML saved to {OUTPUT_HTML}")

    print("\n" + "=" * 60)
    print("PREVIEW:")
    print("=" * 60 + "\n")
    print(plain)


if __name__ == "__main__":
    main()
