"""Generate animated ASCII contact cards for the GitHub profile README."""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets" / "ascii-links"
BG = (13, 17, 23)
PANEL = (19, 25, 34)
MUTED = (160, 170, 182)
GOLD = (255, 209, 102)
FONT = Path(r"C:\Windows\Fonts\consola.ttf")
BOLD = Path(r"C:\Windows\Fonts\consolab.ttf")
WIDTH, HEIGHT = 430, 106
FRAMES, DURATION_MS = 48, 100
CARDS = (
    ("linkedin", "LINKEDIN", "VISITA", "Profilo professionale", (126, 231, 135)),
    ("email", "EMAIL", "SCRIVI", "Proposte e collaborazioni", (255, 123, 114)),
    ("projects", "PROGETTI", "ESPLORA", "Ricerca e lavoro", (210, 168, 255)),
)


def font(size, bold=False):
    return ImageFont.truetype(str(BOLD if bold else FONT), size)


def dim(color, factor):
    return tuple(round(BG[i] * (1 - factor) + color[i] * factor) for i in range(3))


def draw_frame(label, action, detail, accent, index, phase):
    image = Image.new("RGB", (WIDTH, HEIGHT), BG)
    draw = ImageDraw.Draw(image)
    draw.rectangle((7, 8, WIDTH - 7, HEIGHT - 9), fill=PANEL)
    edge_font = font(17)
    cell = edge_font.getlength("=")
    count = int(WIDTH / cell) - 2
    right = round((count + 1) * cell)
    base = dim(accent, 0.72)
    for row in (0, HEIGHT - 17):
        draw.text((0, row), "+" + "=" * count + "+", font=edge_font, fill=base)
    for row in range(17, HEIGHT - 17, 17):
        draw.text((0, row), "|", font=edge_font, fill=base)
        draw.text((right, row), "|", font=edge_font, fill=base)
    # A small bright ASCII packet travels along the horizontal borders.
    packet = (phase * 2 + index * 13) % count
    for offset in range(4):
        col = (packet + offset) % count
        draw.text(((col + 1) * cell, 0), "=", font=edge_font, fill=accent)
        draw.text(((count - col) * cell, HEIGHT - 17), "=", font=edge_font, fill=accent)
    draw.text((23, 22), label, font=font(27, bold=True), fill=accent)
    action_text = f"[ {action} ]"
    action_color = GOLD if phase % 12 < 9 else dim(GOLD, 0.62)
    draw.text((WIDTH - 154, 27), action_text, font=font(16, bold=True), fill=action_color)
    draw.text((24, 63), detail, font=font(15), fill=MUTED)
    return image


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for index, (slug, label, action, detail, accent) in enumerate(CARDS):
        frames = [draw_frame(label, action, detail, accent, index, phase)
                  for phase in range(FRAMES)]
        palette = frames[0].quantize(colors=256, method=Image.Quantize.FASTOCTREE)
        indexed = [frame.quantize(palette=palette, dither=Image.Dither.NONE)
                   for frame in frames]
        destination = OUT / f"{slug}.gif"
        indexed[0].save(destination, save_all=True, append_images=indexed[1:],
                        duration=DURATION_MS, loop=0, optimize=True, disposal=2)
        print(destination)


if __name__ == "__main__":
    main()
