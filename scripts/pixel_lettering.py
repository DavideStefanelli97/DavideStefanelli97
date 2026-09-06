"""Repository-authored 5x7 lettering, emitted as crisp SVG geometry."""

GLYPHS = {
    'A': ('01110', '11011', '11011', '11111', '11011', '11011', '11011'),
    'D': ('11110', '11011', '11011', '11011', '11011', '11011', '11110'),
    'E': ('11111', '11000', '11000', '11110', '11000', '11000', '11111'),
    'F': ('11111', '11000', '11000', '11110', '11000', '11000', '11000'),
    'I': ('11111', '00100', '00100', '00100', '00100', '00100', '11111'),
    'L': ('11000', '11000', '11000', '11000', '11000', '11000', '11111'),
    'N': ('11001', '11101', '11101', '11111', '11011', '11011', '11001'),
    'S': ('01111', '11000', '11000', '01110', '00011', '00011', '11110'),
    'T': ('11111', '00100', '00100', '00100', '00100', '00100', '00100'),
    'V': ('11011', '11011', '11011', '11011', '11011', '01010', '00100'),
}


def lettering_paths():
    """Two aligned lines; no font loading, rasterization or hidden text."""
    body, highlights = [], []
    cell = 12
    for text, y in [('DAVIDE', 96), ('STEFANELLI', 210)]:
        for letter, char in enumerate(text):
            glyph = GLYPHS[char]
            for row, bits in enumerate(glyph):
                for col, bit in enumerate(bits):
                    if bit != '1':
                        continue
                    x = 60 + (letter*6+col)*cell
                    top = y + row*cell
                    body.append(f'M{x} {top}h{cell}v{cell}h-{cell}z')
                    if row == 0 or glyph[row-1][col] == '0':
                        highlights.append(f'M{x} {top}h{cell}v2h-{cell}z')
    return ''.join(body), ''.join(highlights)
