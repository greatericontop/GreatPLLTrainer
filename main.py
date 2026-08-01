
import random
import time
from dataclasses import dataclass

import pygame


STICKER_TO_INDEX = {'B': 0, 'O': 1, 'G': 2, 'R': 3}
INDEX_TO_STICKER = {v: k for k, v in STICKER_TO_INDEX.items()}
COLORS = {
    'Y': (0xee, 0xee, 0x55),
    'B': (0x44, 0x44, 0xee),
    'O': (0xff, 0xaa, 0x00),
    'G': (0x22, 0xdd, 0x22),
    'R': (0xff, 0x33, 0x33),
}
# 120 degree vectors for isometric projection
V1 = (-0.8660254037844386, -0.5)
V2 = (0.8660254037844386, -0.5)
V3 = (0.0, 1.0)
PX_SCALE = 60

WINDOW_SIZE = (1280, 720)
BG_COLOR = (0x30, 0x30, 0x30)
TEXT_COLOR = (0xee, 0xee, 0xee)
FONT = None
CUBE_BORDER_COLOR = (0, 0, 0)
CUBE_BORDER_THICKNESS = 2


@dataclass(slots=True, frozen=True)
class PLLCase:
    """Data structure for a PLL case."""
    name: str
    name_long: str
    stickers: str  # length-6 string of B, O, G, R

    def shuffle(self):
        """Randomly shuffle the stickers. Returns a new string of the stickers."""
        offset = random.randint(0, 3)
        indices = [(STICKER_TO_INDEX[s]+offset) % 4 for s in self.stickers]
        return ''.join([INDEX_TO_STICKER[i] for i in indices])

    @classmethod
    def from_line(cls, line: str):
        parts = [s.strip() for s in line.split('/')]
        assert len(parts) == 3, f'Line should have 3 parts separated by `/`: {line}'
        assert len(parts[2]) == 6, f'Stickers string should be exactly 6 characters: {parts[2]}'
        assert all(c in 'BOGR' for c in parts[2]), f'Stickers string should contain B, O, G, R: {parts[2]}'
        return cls(parts[0], parts[1], parts[2])

    @classmethod
    def load_all_from_file(cls, filename: str):
        with open(filename, 'r') as f:
            return [cls.from_line(line) for line in f if line.strip() and not line.startswith('#')]


def render_sticker(surface: pygame.Surface, color: str,
                   origin: tuple[float, float], v1: tuple[float, float], v2: tuple[float, float], i: int, j: int):
    """Render a single sticker, at location (i, j) relative to v1 and v2, on the canvas."""
    points = []
    for dx, dy in ((0, 0), (1, 0), (1, 1), (0, 1)):
            x = origin[0] + (i+dx)*v1[0]*PX_SCALE + (j+dy)*v2[0]*PX_SCALE
            y = origin[1] + (i+dx)*v1[1]*PX_SCALE + (j+dy)*v2[1]*PX_SCALE
            points.append((int(x), int(y)))
    pygame.draw.polygon(surface, COLORS[color], points, width=0)
    pygame.draw.polygon(surface, CUBE_BORDER_COLOR, points, width=CUBE_BORDER_THICKNESS)


def render_case(surface: pygame.Surface, case: PLLCase, origin: tuple[float, float]):
    """Render all stickers of the entire :case: on the canvas."""
    stickers = case.shuffle()
    cuberot = random.randint(0, 3)
    right_color, left_color = INDEX_TO_STICKER[cuberot], INDEX_TO_STICKER[(cuberot+1) % 4]
    # Draw yellow on top
    # Top is spanned by V1 and V2
    for i in (0, 1, 2):
        for j in (0, 1, 2):
            render_sticker(surface, 'Y', origin, V1, V2, i, j)
    # Draw 3 stickers on left, and :left_color: for bottom 2 layers
    # Left is spanned by V1 and V3 (V3 is downward)
    for i in (0, 1, 2):
        render_sticker(surface, stickers[2-i], origin, V1, V3, i, 0)  # stickers[0] is the leftmost (i=2)
    for i in (0, 1, 2):
        for j in (1, 2):
            render_sticker(surface, left_color, origin, V1, V3, i, j)
    # Right is spanned by V2 and V3
    for i in (0, 1, 2):
        render_sticker(surface, stickers[i+3], origin, V2, V3, i, 0)
    for i in (0, 1, 2):
        for j in (1, 2):
            render_sticker(surface, right_color, origin, V2, V3, i, j)


def main():
    cases = PLLCase.load_all_from_file('cases.txt')
    pygame.init()
    canvas = pygame.display.set_mode(WINDOW_SIZE)
    canvas.fill(BG_COLOR)
    render_case(canvas, random.choice(cases), (WINDOW_SIZE[0]/2, WINDOW_SIZE[1]/2))
    pygame.display.update()
    time.sleep(100000)


if __name__ == '__main__':
    main()
