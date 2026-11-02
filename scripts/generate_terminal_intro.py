"""Generate the profile's animated ASCII terminal introduction."""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "assets" / "terminal-intro.gif"
BG = (13, 17, 23)
MUTED = (139, 148, 158)
GREEN = (126, 231, 135)
GOLD = (255, 209, 102)
CORAL = (255, 123, 114)
VIOLET = (210, 168, 255)
FONT = ImageFont.truetype(r"C:\Windows\Fonts\consola.ttf", 19)
LINES = (
    ("davide@research:~$ cat profile.txt", GREEN),
    ("+ Computer Vision / ML Research Engineer", GOLD),
    ("+ Biomedical Engineer", CORAL),
    ("@ Cesena, Italy | M.Sc. candidate, University of Bologna", VIOLET),
)
SIZE = (850, 158)
FRAMES = 100
FRAME_MS = 80


def frame(phase):
    image = Image.new("RGB", SIZE, BG)
    draw = ImageDraw.Draw(image)
    draw.text((18, 4), "+" + "-" * 76 + "+", font=FONT, fill=MUTED)
    draw.text((18, 133), "+" + "-" * 76 + "+", font=FONT, fill=MUTED)
    if phase < 15 or phase >= 82:
        remaining = sum(len(line) for line, _ in LINES)
    elif phase < 21:
        remaining = 0
    else:
        remaining = min(sum(len(line) for line, _ in LINES), (phase - 21) * 3)
    last_position = (32, 32)
    for index, (line, color) in enumerate(LINES):
        visible = line[:remaining]
        remaining -= len(visible)
        y = 32 + index * 26
        draw.text((32, y), visible, font=FONT, fill=color)
        if visible:
            last_position = (32 + round(FONT.getlength(visible)), y)
        if remaining <= 0:
            break
    if phase % 10 < 6 and phase >= 21:
        draw.text(last_position, "_", font=FONT, fill=GREEN)
    return image


def main():
    images = [frame(i) for i in range(FRAMES)]
    palette = images[0].quantize(colors=256, method=Image.Quantize.FASTOCTREE)
    indexed = [image.quantize(palette=palette, dither=Image.Dither.NONE) for image in images]
    indexed[0].save(OUTPUT, save_all=True, append_images=indexed[1:], duration=FRAME_MS,
                    loop=0, optimize=True, disposal=2)
    print(OUTPUT)


if __name__ == "__main__":
    main()
