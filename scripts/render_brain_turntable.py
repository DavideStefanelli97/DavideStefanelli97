"""Render a fixed fsaverage cortical mesh as a pixel-art turntable.

Dependencies: numpy, numba, Pillow.
python scripts/render_brain_turntable.py --subjects-dir PATH_TO_FSAVERAGE_PARENT

This is a scientific surface render, not a transformation of generated frames.
The camera, orthographic scale, 3D pivot, light, and pixel grid stay fixed.
"""
from argparse import ArgumentParser
from pathlib import Path
import json
import math
import struct

import numpy as np
from numba import njit
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
SIZE = 80
FRAMES = 120
COLS = 12
DURATION_MS = 40


def read_surface(path):
    with path.open('rb') as f:
        if f.read(3) != b'\xff\xff\xfe':
            raise ValueError(f'Expected a FreeSurfer triangle surface: {path}')
        f.readline()
        f.readline()
        nv, nf = struct.unpack('>ii', f.read(8))
        vertices = np.frombuffer(f.read(nv * 12), dtype='>f4').astype(np.float64).reshape(-1, 3)
        faces = np.frombuffer(f.read(nf * 12), dtype='>i4').astype(np.int32).reshape(-1, 3)
    return vertices, faces


def read_sulc(path, count):
    with path.open('rb') as f:
        if f.read(3) != b'\xff\xff\xff':
            raise ValueError(f'Expected a new-format FreeSurfer curvature file: {path}')
        nv, _, values = struct.unpack('>iii', f.read(12))
        assert nv == count and values == 1
        return np.frombuffer(f.read(nv * 4), dtype='>f4').astype(np.float64)


def load_mesh(subjects_dir):
    surfaces = subjects_dir / 'fsaverage' / 'surf'
    left, lf = read_surface(surfaces / 'lh.pial')
    right, rf = read_surface(surfaces / 'rh.pial')
    sulc = np.concatenate([read_sulc(surfaces / 'lh.sulc', len(left)),
                           read_sulc(surfaces / 'rh.sulc', len(right))])
    vertices = np.vstack([left, right])
    faces = np.vstack([lf, rf + len(left)])
    pivot = (vertices.min(axis=0) + vertices.max(axis=0)) / 2
    vertices -= pivot  # One pivot for all frames; never re-center a silhouette.
    edges1 = vertices[faces[:, 1]] - vertices[faces[:, 0]]
    edges2 = vertices[faces[:, 2]] - vertices[faces[:, 0]]
    fn = np.cross(edges1, edges2)
    normals = np.zeros_like(vertices)
    for corner in range(3):
        np.add.at(normals, faces[:, corner], fn)
    normals /= np.maximum(np.linalg.norm(normals, axis=1, keepdims=True), 1e-12)
    return vertices, faces, normals, sulc, pivot


@njit(cache=True)
def rasterize(points, faces, tones, size):
    zbuffer = np.full((size, size), -1e30)
    pixels = np.zeros((size, size), dtype=np.uint8)
    for face in faces:
        a, b, c = face
        ax, ay, az = points[a]
        bx, by, bz = points[b]
        cx, cy, cz = points[c]
        denom = (by-cy)*(ax-cx) + (cx-bx)*(ay-cy)
        if abs(denom) < 1e-12:
            continue
        x0 = max(0, int(math.ceil(min(ax, bx, cx) - .5)))
        x1 = min(size-1, int(math.floor(max(ax, bx, cx) - .5)))
        y0 = max(0, int(math.ceil(min(ay, by, cy) - .5)))
        y1 = min(size-1, int(math.floor(max(ay, by, cy) - .5)))
        for y in range(y0, y1+1):
            for x in range(x0, x1+1):
                px, py = x+.5, y+.5
                u = ((by-cy)*(px-cx)+(cx-bx)*(py-cy))/denom
                v = ((cy-ay)*(px-cx)+(ax-cx)*(py-cy))/denom
                w = 1-u-v
                if min(u, v, w) < -1e-7:
                    continue
                z = u*az+v*bz+w*cz
                if z > zbuffer[y, x]:
                    zbuffer[y, x] = z
                    tone = u*tones[a]+v*tones[b]+w*tones[c]
                    pixels[y, x] = 1 + min(30, max(0, int(tone*30)))
    return pixels


def palette():
    anchors = np.array([[13, 24, 49], [39, 58, 121], [59, 116, 172],
                        [88, 191, 207], [178, 243, 234]], dtype=float)
    colors = [[0, 0, 0]]
    for t in np.linspace(0, len(anchors)-1, 31):
        i = min(int(t), len(anchors)-2)
        colors.append(np.rint(anchors[i]*(1-(t-i))+anchors[i+1]*(t-i)).astype(int).tolist())
    return sum(colors, []) + [0] * (768-len(colors)*3)


def build(subjects_dir):
    vertices, faces, normals, sulc, pivot = load_mesh(subjects_dir)
    pitch = math.radians(18)
    cp, sp = math.cos(pitch), math.sin(pitch)
    # Bounding sphere establishes a constant orthographic scale for a full turn.
    radius = np.linalg.norm(vertices, axis=1).max()
    scale = (SIZE * .43) / radius
    light = np.array([-.4, -.6, .7])
    light /= np.linalg.norm(light)
    relief = .84 - .13*np.tanh(sulc/1.5)
    frames = []
    bounds = []
    for i in range(FRAMES):
        angle = 2*math.pi*i/FRAMES
        cs, sn = math.cos(angle), math.sin(angle)
        rotation = np.array([[cs, -sn, 0], [sn, cs, 0], [0, 0, 1]])
        camera = np.array([[1, 0, 0], [0, sp, -cp], [0, cp, sp]])
        transform = camera @ rotation
        view = vertices @ transform.T
        n = normals @ transform.T
        diffuse = np.maximum(n @ light, 0)
        # Smooth Lambert shading, with a restrained camera-space rim light.
        rim = (1-np.abs(n[:, 2]))**3
        tones = np.clip((.24+.71*diffuse+.13*rim)*relief, 0, 1)
        view[:, :2] = view[:, :2]*scale + SIZE/2
        frame = rasterize(view, faces, tones, SIZE)
        rows, cols = np.nonzero(frame)
        bounds.append([int(cols.min()), int(rows.min()), int(cols.max()), int(rows.max())])
        frames.append(frame)
    sheet = Image.new('P', (SIZE*COLS, SIZE*(FRAMES//COLS)), 0)
    sheet.putpalette(palette())
    for i, pixels in enumerate(frames):
        tile = Image.frombytes('P', (SIZE, SIZE), pixels.tobytes())
        tile.putpalette(palette())
        sheet.paste(tile, ((i%COLS)*SIZE, (i//COLS)*SIZE))
    sheet.save(ROOT/'assets/brain-turntable-stable.png', transparency=0, optimize=True)
    # The standalone GIF is a convenient review/export artifact of the same render.
    gif_frames = []
    for pixels in frames:
        im = Image.frombytes('P', (SIZE, SIZE), pixels.tobytes())
        im.putpalette(palette())
        im.info['transparency'] = 0
        gif_frames.append(im.resize((320, 320), Image.Resampling.NEAREST))
    gif_frames[0].save(ROOT/'assets/brain-turntable-stable.gif', save_all=True,
                       append_images=gif_frames[1:], duration=DURATION_MS,
                       loop=0, transparency=0, disposal=2, optimize=False)
    out = ROOT/'output'
    out.mkdir(exist_ok=True)
    grid = Image.new('RGB', (320*4, 320*2), '#0d1726')
    for j, index in enumerate(range(0, FRAMES, 15)):
        im = gif_frames[index].convert('RGBA')
        grid.paste(im, ((j%4)*320, (j//4)*320), im)
    grid.save(out/'brain-stable-contact-sheet.png')
    # Anatomical silhouettes naturally vary with yaw. Camera and pivot do not.
    assert all(min(b) > 0 and max(b) < SIZE-1 for b in bounds), 'Clipped frame'
    differences = [float(np.mean(np.abs(frames[i].astype(float)-frames[(i+1)%FRAMES])))
                   for i in range(FRAMES)]
    report = dict(frames=FRAMES, fps=1000/DURATION_MS, loop_seconds=FRAMES*DURATION_MS/1000,
                  grid=SIZE, pivot_mm=pivot.tolist(), scale=scale,
                  bounds=bounds, adjacent_frame_mean_difference=differences,
                  seam_difference=differences[-1], max_adjacent_difference=max(differences))
    (out/'brain-animation-qa.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    metadata = dict(frames=FRAMES, columns=COLS, rows=FRAMES//COLS,
                    frame_pixels=SIZE, duration_seconds=FRAMES*DURATION_MS/1000,
                    source='FreeSurfer fsaverage pial surfaces, distributed by MNE',
                    source_url='https://mne.tools/stable/generated/mne.datasets.fetch_fsaverage.html')
    (ROOT/'assets/brain-turntable-stable.json').write_text(json.dumps(metadata, indent=2)+'\n', encoding='utf-8')
    print(f'Rendered {FRAMES} frames at {SIZE}x{SIZE}, fixed pivot and scale; seam delta {differences[-1]:.3f}, max adjacent delta {max(differences):.3f}.')


if __name__ == '__main__':
    parser = ArgumentParser(description=__doc__)
    parser.add_argument('--subjects-dir', type=Path, required=True)
    build(parser.parse_args().subjects_dir)
