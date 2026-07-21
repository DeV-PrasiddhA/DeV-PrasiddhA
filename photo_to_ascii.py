from PIL import Image, ImageOps, ImageFilter

INPUT  = "pfp.jpeg"
WIDTH  = 50
RAMP   = " .,:-~=+*#%@"


def process(path):
    img = Image.open(path).convert("L")
    w, h = img.size

    # crop: focus on face region
    img = img.crop((0, int(h * 0.10), w, int(h * 0.90)))

    # denoise with gaussian blur
    img = img.filter(ImageFilter.GaussianBlur(radius=1.5))

    # gamma 0.25 to lift the extremely dark image
    table = [int(255 * (i / 255) ** 0.25) for i in range(256)]
    px = img.load()
    for y in range(img.height):
        for x in range(img.width):
            px[x, y] = table[px[x, y]]

    img = ImageOps.autocontrast(img, cutoff=2)

    # second light blur to smooth after contrast
    img = img.filter(ImageFilter.GaussianBlur(radius=0.8))

    # resize
    w, h = img.size
    new_h = max(1, int(h / w * WIDTH * 0.5))
    img = img.resize((WIDTH, new_h), Image.LANCZOS)
    return img


def to_ascii(gray):
    px = gray.load()
    w, h = gray.size
    n = len(RAMP) - 1
    lines = []
    for y in range(h):
        row = ""
        for x in range(w):
            v = px[x, y]
            idx = min(n, max(0, int(v / 255 * n + 0.5)))
            row += RAMP[idx]
        lines.append(row)
    return lines


def colorize(lines, fg="#00d4ff", bg="#0d1117"):
    out = []
    for ln in lines:
        e = ln.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        out.append(f'<span style="color:{fg}">{e}</span>')
    return (
        f'<pre style="background:{bg};padding:8px;border-radius:6px;text-align:center;line-height:1.1;font-size:11px">\n'
        + "\n".join(out)
        + "\n</pre>"
    )


def main():
    gray = process(INPUT)
    lines = to_ascii(gray)

    while lines and not lines[0].strip():
        lines.pop(0)
    while lines and not lines[-1].strip():
        lines.pop()

    plain = "<pre>\n" + "\n".join(lines) + "\n</pre>"
    with open("ascii_output.txt", "w", encoding="utf-8") as f:
        f.write(plain)

    colored = colorize(lines)
    with open("ascii_colored.html", "w", encoding="utf-8") as f:
        f.write(colored)

    print(f"Size: {WIDTH}x{len(lines)}")
    print(plain)


if __name__ == "__main__":
    main()
