# Caesar's Calendar Puzzle with DLX Auto-Solver (cleaned + no board outline shadow)
import datetime
import os
import random
import sys
import threading
import time

import pygame

pygame.init()

# ------------------ BOARD SIZE ------------------
GRID_W = 8
GRID_H = 8

# ------------------ THEMES ------------------
THEMES = [
    {
        "name": "Nord",
        "BG": (46, 52, 64),
        "BOARD_TILE": (67, 76, 94),
        "VOID_TILE": (59, 66, 82),
        "CELL_BORDER": (76, 86, 106),
        "TEXT_COL": (236, 239, 244),
        "PIECE_COLORS": [
            (129, 161, 193),
            (136, 192, 208),
            (163, 190, 140),
            (235, 203, 139),
            (208, 135, 112),
            (191, 97, 106),
            (180, 142, 173),
            (143, 188, 187),
            (94, 129, 172),
            (229, 233, 240),
        ],
        "font_main": "PressStart2P.ttf",
        "font_fallback": "Consolas",
        "BTN_BG": (67, 76, 94),
        "BTN_BORDER": (236, 239, 244),
        "BTN_TEXT": (236, 239, 244),
        "AUTOSOLVE_BG": (143, 188, 187),
        "AUTOSOLVE_BORDER": (236, 239, 244),
        "AUTOSOLVE_TEXT": (46, 52, 64),
    },
    {
        "name": "Wood",
        "BG": (210, 180, 140),
        "BOARD_TILE": (190, 155, 110),
        "VOID_TILE": (170, 135, 95),
        "CELL_BORDER": (95, 65, 35),
        "TEXT_COL": (20, 12, 6),
        "PIECE_COLORS": [
            (156, 102, 31),   # classic brown
            (184, 134, 11),   # golden brown
            (205, 133, 63),   # peru
            (139, 69, 19),    # saddle brown
            (210, 180, 140),  # tan
            (160, 82, 45),    # sienna
            (222, 184, 135),  # burlywood
            (191, 101, 46),   # medium wood
            (120, 80, 40),    # dark wood (for Г)
            (110, 60, 20),    # extra dark for straight line
        ],
        "font_main": None,
        "font_fallback": "Georgia",
        "BTN_BG": (190, 155, 110),
        "BTN_BORDER": (95, 65, 35),
        "BTN_TEXT": (20, 12, 6),
        "AUTOSOLVE_BG": (120, 80, 40),
        "AUTOSOLVE_BORDER": (95, 65, 35),
        "AUTOSOLVE_TEXT": (255, 255, 255),
    },
    {
        "name": "Solarized",
        "BG": (0, 43, 54),
        "BOARD_TILE": (7, 54, 66),
        "VOID_TILE": (88, 110, 117),
        "CELL_BORDER": (101, 123, 131),
        "TEXT_COL": (253, 246, 227),
        "PIECE_COLORS": [
            (38, 139, 210),
            (42, 161, 152),
            (133, 153, 0),
            (181, 137, 0),
            (203, 75, 22),
            (220, 50, 47),
            (211, 54, 130),
            (108, 113, 196),
            (147, 161, 161),
            (253, 246, 227),
        ],
        "font_main": None,
        "font_fallback": "Arial",
        "BTN_BG": (7, 54, 66),
        "BTN_BORDER": (253, 246, 227),
        "BTN_TEXT": (253, 246, 227),
        "AUTOSOLVE_BG": (42, 161, 152),
        "AUTOSOLVE_BORDER": (253, 246, 227),
        "AUTOSOLVE_TEXT": (0, 43, 54),
    },
]

# ------------------ PIECES ------------------
PIECES_BASE = [
    [(0, 0), (0, 1), (0, 2), (0, 3), (1, 3)],  # 1 Tall L
    [(0, 0), (0, 1), (0, 2), (1, 2)],  # 2 Short L
    [(0, 0), (1, 0), (2, 0), (0, 1), (2, 1)],  # 3 U-shape
    [(0, 0), (1, 0), (1, 1), (2, 1), (3, 1)],  # 4 long Z
    [(0, 0), (1, 0), (1, 1), (2, 1)],  # 5 short Z
    [(0, 0), (1, 0), (2, 0), (1, 1), (1, 2)],  # 6 T
    [(0, 0), (0, 1), (0, 2), (0, 3)],  # 7 line
    [(0, 0), (1, 0), (0, 1), (1, 1), (2, 1)],  # 8 2x2+tab
    [(0, 0), (0, 1), (0, 2), (1, 0), (2, 0)],  # 9 Г
    [(0, 0), (1, 0), (1, 1), (1, 2), (2, 2)],  # 10 custom S-like
]

# ------------------ WINDOW & LAYOUT HELPERS ------------------
def get_piece_dimensions(piece_collection=None):
    """
    Calculate max width and height across all pieces.
    
    Args:
        piece_collection: Optional list of pieces to measure. 
                         Uses PIECES_BASE if None.
    
    Returns:
        tuple: (max_width, max_height)
    """
    if piece_collection is None:
        piece_collection = PIECES_BASE
        
    wmax, hmax = 1, 1
    for p in piece_collection:
        if not p:
            continue
        # Handle both raw coordinate lists and piece dicts with 'cells' key
        cells = p.get("cells", p) if isinstance(p, dict) else p
        if not cells:
            continue
        w = max(x for x, _ in cells) + 1
        h = max(y for _, y in cells) + 1
        wmax = max(wmax, w)
        hmax = max(hmax, h)
    return wmax, hmax


def compute_best_cell_size(win_w, win_h, num_pieces, wmax, hmax):
    """
    Compute optimal cell size for given window dimensions and piece constraints.
    
    Args:
        win_w: Window width in pixels
        win_h: Window height in pixels
        num_pieces: Number of pieces to fit in palette
        wmax: Maximum piece width in cells
        hmax: Maximum piece height in cells
    
    Returns:
        int: Optimal cell size in pixels
    """
    from math import ceil
    
    max_palette_rows = 2
    controls_rows = 2
    best = 16
    
    for palette_rows in range(1, max_palette_rows + 1):
        palette_cols = ceil(num_pieces / palette_rows)
        total_h_cells = GRID_H + palette_rows * hmax + controls_rows
        total_w_cells = max(GRID_W, palette_cols * wmax)
        cell_w = win_w // total_w_cells
        cell_h = win_h // total_h_cells
        cell = max(16, min(cell_w, cell_h))
        if cell > best:
            best = cell
    return best


def compute_initial_cell(win_w: int, win_h: int) -> int:
    """Compute initial cell size based on PIECES_BASE dimensions."""
    wmax, hmax = get_piece_dimensions(PIECES_BASE)
    return compute_best_cell_size(win_w, win_h, len(PIECES_BASE), wmax, hmax)


win_w, win_h = 1000, 600
screen = pygame.display.set_mode((win_w, win_h), pygame.RESIZABLE)
pygame.display.set_caption("Caesar's Calendar Puzzle")
clock = pygame.time.Clock()

# ------------------ BOARD LAYOUT ------------------
MONTHS = [
    "JAN",
    "FEB",
    "MAR",
    "APR",
    "MAY",
    "JUN",
    "JUL",
    "AUG",
    "SEP",
    "OCT",
    "NOV",
    "DEC",
]
WEEKROW1 = ["SUN", "MON", "TUE", "WED"]
WEEKROW2 = ["THU", "FRI", "SAT"]

board_mask = set()
void_cells = set()
cell_label = {}


def build_layout() -> None:
    board_mask.clear()
    void_cells.clear()
    cell_label.clear()
    mi = 0
    for ry in range(2):
        for cx in range(1, 7):
            pos = (cx, ry)
            board_mask.add(pos)
            cell_label[pos] = {"type": "month", "text": MONTHS[mi]}
            mi += 1
    void_cells.update({(7, 0), (7, 1)})

    dx0, dy0 = 1, 2
    day = 1
    for ry in range(5):
        for cx in range(7):
            x, y = dx0 + cx, dy0 + ry
            if day <= 31:
                board_mask.add((x, y))
                cell_label[(x, y)] = {"type": "date", "text": str(day)}
                day += 1
            else:
                void_cells.add((x, y))

    for i, wd in enumerate(WEEKROW1):
        x, y = 4 + i, 6
        board_mask.add((x, y))
        cell_label[(x, y)] = {"type": "weekday", "text": wd}

    for i, wd in enumerate(WEEKROW2):
        x, y = 5 + i, 7
        board_mask.add((x, y))
        cell_label[(x, y)] = {"type": "weekday", "text": wd}

    void_cells.update({(1, 7), (2, 7), (3, 7), (4, 7)})


build_layout()

# ------------------ PIECE ORIENTATION UTILS ------------------
def rotate_shape(s):
    return [(-y, x) for (x, y) in s]


def flip_shape(s):
    return [(-x, y) for (x, y) in s]


def normalize(s):
    minx = min(x for x, _ in s)
    miny = min(y for _, y in s)
    return [(x - minx, y - miny) for (x, y) in s]


def oriented_cells(base_cells, rot, flip):
    s = list(base_cells)
    if flip:
        s = flip_shape(s)
    for _ in range(rot % 4):
        s = rotate_shape(s)
    return normalize(s)


# ------------------ FONT SCALE CONSTANTS ------------------
FONT_SCALE_CONTROLS = 0.28
FONT_SCALE_WEEKDAY = 0.33
FONT_SCALE_MONTH = 0.35
FONT_SCALE_THEME_LABEL = 0.35
FONT_SCALE_DATE = 0.45
FONT_SCALE_BUTTON = 0.45
FONT_SCALE_SOLUTION_INDEX = 0.45
FONT_SCALE_WIN_SUBTITLE = 0.6
FONT_SCALE_TIMER = 0.7
FONT_SCALE_WIN_TIMER = 0.8
FONT_SCALE_SOLVING = 1.0
FONT_SCALE_WIN_TITLE = 1.2

# ------------------ THEME & FONTS ------------------
theme_idx = 0


def get_theme():
    return THEMES[theme_idx]


def get_font_path(font_name):
    if font_name and os.path.exists(font_name):
        return font_name
    return None


def choose_font(sz, bold=False):
    try:
        return pygame.font.SysFont("Consolas", sz, bold=bold)
    except Exception:
        return pygame.font.SysFont("Courier New", sz, bold=bold)


def create_scaled_font(scale_factor, bold=False):
    """Create a font scaled by CELL size with the given scale factor."""
    return choose_font(max(12, int(CELL * scale_factor)), bold=bold)


PIECE_COLORS = THEMES[0]["PIECE_COLORS"]


def apply_theme():
    global BG, BOARD_TILE, VOID_TILE, CELL_BORDER, TEXT_COL, PIECE_COLORS
    global BTN_BG, BTN_BORDER, BTN_TEXT, AUTOSOLVE_BG, AUTOSOLVE_BORDER, AUTOSOLVE_TEXT
    t = get_theme()
    BG = t.get("BG", (18, 32, 64))
    BOARD_TILE = t.get("BOARD_TILE", (44, 60, 120))
    VOID_TILE = t.get("VOID_TILE", (28, 44, 80))
    CELL_BORDER = t.get("CELL_BORDER", (80, 100, 160))
    TEXT_COL = t.get("TEXT_COL", (255, 255, 255))
    PIECE_COLORS = t.get("PIECE_COLORS", PIECE_COLORS)
    BTN_BG = t.get("BTN_BG", BOARD_TILE)
    BTN_BORDER = t.get("BTN_BORDER", CELL_BORDER)
    BTN_TEXT = t.get("BTN_TEXT", TEXT_COL)
    AUTOSOLVE_BG = t.get("AUTOSOLVE_BG", (80, 180, 80))
    AUTOSOLVE_BORDER = t.get("AUTOSOLVE_BORDER", (255, 255, 255))
    AUTOSOLVE_TEXT = t.get("AUTOSOLVE_TEXT", (255, 255, 255))


pieces = [
    {
        "name": f"P{i + 1}",
        "cells": normalize(base),
        "color": PIECE_COLORS[i % len(PIECE_COLORS)],
    }
    for i, base in enumerate(PIECES_BASE)
]


def update_piece_colors():
    for i, p in enumerate(pieces):
        p["color"] = PIECE_COLORS[i % len(PIECE_COLORS)]


apply_theme()
update_piece_colors()

# ------------------ PLACED STATE & LAYOUT ------------------
placed = []
CELL = compute_initial_cell(win_w, win_h)


def compute_best_layout(win_w_, win_h_):
    """
    Compute the best layout configuration for pieces palette.
    
    Args:
        win_w_: Window width in pixels
        win_h_: Window height in pixels
    
    Returns:
        dict: Layout configuration with cell size, rows, cols, dimensions
    """
    from math import ceil
    
    n = len(pieces)
    wmax, hmax = get_piece_dimensions(pieces)
    
    max_palette_rows = 2
    controls_rows = 2
    best_cell = compute_best_cell_size(win_w_, win_h_, n, wmax, hmax)
    
    # Find the palette configuration that produces this best cell size
    best = {
        "cell": best_cell,
        "palette_rows": 1,
        "palette_cols": n,
        "controls_rows": controls_rows,
        "wmax": wmax,
        "hmax": hmax,
    }
    
    for palette_rows in range(1, max_palette_rows + 1):
        palette_cols = ceil(n / palette_rows)
        total_h_cells = GRID_H + palette_rows * hmax + controls_rows
        total_w_cells = max(GRID_W, palette_cols * wmax)
        cell_w = win_w_ // total_w_cells
        cell_h = win_h_ // total_h_cells
        cell = max(16, min(cell_w, cell_h))
        if cell == best_cell:
            best = {
                "cell": cell,
                "palette_rows": palette_rows,
                "palette_cols": palette_cols,
                "controls_rows": controls_rows,
                "wmax": wmax,
                "hmax": hmax,
            }
            break
    
    return best


def recompute_palette_layout():
    n = len(pieces)
    win_w_, win_h_ = screen.get_size()
    layout = compute_best_layout(win_w_, win_h_)
    global CELL, PALETTE_ROWS, PALETTE_COLS, CONTROLS_ROWS, PALETTE_WMAX, PALETTE_HMAX
    CELL = layout["cell"]
    PALETTE_ROWS = layout["palette_rows"]
    PALETTE_COLS = layout["palette_cols"]
    CONTROLS_ROWS = layout["controls_rows"]
    PALETTE_WMAX = layout["wmax"]
    PALETTE_HMAX = layout["hmax"]
    palette_x0 = GRID_W + 1
    palette_y0 = 0
    homes = []
    for i in range(n):
        c = i % PALETTE_COLS
        r = i // PALETTE_COLS
        homex = palette_x0 + c * PALETTE_WMAX
        homey = r * PALETTE_HMAX
        homes.append((homex, homey))
    if not placed:
        for pid in range(n):
            placed.append(
                {
                    "pid": pid,
                    "pos": homes[pid],
                    "rot": 0,
                    "flip": False,
                    "cells": [],
                    "home": homes[pid],
                }
            )
    else:
        for i, h in enumerate(homes):
            was_at_home = placed[i]["pos"] == placed[i]["home"]
            placed[i]["home"] = h
            if was_at_home:
                placed[i]["pos"] = h
    update_piece_colors()
    update_placed_cells()


def update_placed_cells():
    for pl in placed:
        base = pieces[pl["pid"]]["cells"]
        oc = oriented_cells(base, pl["rot"], pl["flip"])
        pl["cells"] = [(pl["pos"][0] + x, pl["pos"][1] + y) for (x, y) in oc]


recompute_palette_layout()

# ------------------ DRAW HELPERS ------------------
def draw_button(surface, rect, text, bg_color, border_color, text_color, font_scale=FONT_SCALE_BUTTON):
    """
    Draw a button with text centered.
    
    Args:
        surface: Pygame surface to draw on
        rect: pygame.Rect for button position and size
        text: Button text string
        bg_color: Background color tuple (R, G, B)
        border_color: Border color tuple (R, G, B)
        text_color: Text color tuple (R, G, B)
        font_scale: Font scale factor (default: FONT_SCALE_BUTTON)
    """
    pygame.draw.rect(surface, bg_color, rect, border_radius=10)
    pygame.draw.rect(surface, border_color, rect, 2, border_radius=10)
    btn_font = create_scaled_font(font_scale, bold=True)
    btn_text = btn_font.render(text, True, text_color)
    btn_text_rect = btn_text.get_rect(center=rect.center)
    surface.blit(btn_text, btn_text_rect)


def get_button_theme_colors(button_type="normal"):
    """
    Get theme colors for a button.
    
    Args:
        button_type: "normal" or "autosolve"
    
    Returns:
        tuple: (bg_color, border_color, text_color)
    """
    if button_type == "autosolve":
        return AUTOSOLVE_BG, AUTOSOLVE_BORDER, AUTOSOLVE_TEXT
    return BTN_BG, BTN_BORDER, BTN_TEXT


# ------------------ DRAW ------------------
def get_board_y_offset():
    return int(CELL * 1.2)


def cell_to_screen(x, y):
    return x * CELL, get_board_y_offset() + y * CELL


def screen_to_cell(sx, sy):
    oy = get_board_y_offset()
    return int(sx // CELL), int((sy - oy) // CELL)


def draw_board(surface, y_offset=0):
    for x in range(GRID_W):
        for y in range(GRID_H):
            rect = (x * CELL, y_offset + y * CELL, CELL, CELL)
            if (x, y) in board_mask:
                pygame.draw.rect(surface, BOARD_TILE, rect, border_radius=8)
                pygame.draw.rect(surface, CELL_BORDER, rect, 2, border_radius=8)
            elif (x, y) in void_cells:
                pygame.draw.rect(surface, VOID_TILE, rect, border_radius=8)
                pygame.draw.rect(surface, CELL_BORDER, rect, 2, border_radius=8)

    month_font = create_scaled_font(FONT_SCALE_MONTH)
    date_font = create_scaled_font(FONT_SCALE_DATE)
    weekday_font = create_scaled_font(FONT_SCALE_WEEKDAY)
    for (x, y), info in cell_label.items():
        sx, sy = x * CELL, y_offset + y * CELL
        t = info["text"]
        if info["type"] == "month":
            surf = month_font.render(t, True, TEXT_COL)
        elif info["type"] == "weekday":
            surf = weekday_font.render(t, True, TEXT_COL)
        else:
            surf = date_font.render(t, True, TEXT_COL)
        surface.blit(surf, surf.get_rect(center=(sx + CELL / 2, sy + CELL / 2)))


def draw_pieces(surface, highlight_idx=None):
    theme = get_theme()["name"]
    for i, pl in enumerate(placed):
        col = pieces[pl["pid"]]["color"]
        for cell in pl["cells"]:
            sx, sy = cell_to_screen(*cell)
            r = pygame.Rect(sx + 4, sy + 4, CELL - 8, CELL - 8)
            if theme == "Nord":
                shadow = pygame.Surface((CELL - 8, CELL - 8), pygame.SRCALPHA)
                pygame.draw.rect(
                    shadow, (0, 0, 0, 120), shadow.get_rect(), border_radius=2
                )
                surface.blit(shadow, (sx + 6, sy + 6))
                pygame.draw.rect(surface, col, r, border_radius=2)
                pygame.draw.rect(surface, (0, 0, 0), r, 3, border_radius=2)
                inner = r.inflate(-CELL // 6, -CELL // 6)
                pygame.draw.rect(surface, (255, 255, 255), inner, 1, border_radius=2)
            elif theme == "Wood":
                # Shadow
                shadow = pygame.Surface((CELL - 8, CELL - 8), pygame.SRCALPHA)
                pygame.draw.rect(
                    shadow, (80, 60, 30, 100), shadow.get_rect(), border_radius=10
                )
                surface.blit(shadow, (sx + 6, sy + 8))
                # Main fill
                pygame.draw.rect(surface, col, r, border_radius=10)
                # Wood grain texturing: draw a few random arcs/lines
                grain_col = tuple(min(255, int(c * 1.15)) for c in col)
                for offset in range(4, CELL-12, 7):
                    pygame.draw.arc(surface, grain_col, r.move(0, offset//2), 0.2, 2.7, 1)
                for offset in range(8, CELL-12, 11):
                    pygame.draw.line(surface, grain_col, (r.left+4, r.top+offset), (r.right-4, r.top+offset), 1)
                # Strong black outline
                pygame.draw.rect(surface, (0, 0, 0), r, 4, border_radius=10)
                # Highlight
                highlight = pygame.Surface((CELL - 8, CELL - 8), pygame.SRCALPHA)
                pygame.draw.rect(
                    highlight,
                    (255, 255, 220, 80),
                    (0, 0, CELL - 8, CELL // 3),
                    border_radius=10,
                )
                surface.blit(highlight, (sx + 4, sy + 4))
            elif theme == "Solarized":
                shadow = pygame.Surface((CELL - 8, CELL - 8), pygame.SRCALPHA)
                pygame.draw.rect(
                    shadow, (0, 43, 54, 120), shadow.get_rect(), border_radius=6
                )
                surface.blit(shadow, (sx + 5, sy + 7))
                pygame.draw.rect(surface, col, r, border_radius=6)
                pygame.draw.rect(surface, (253, 246, 227), r, 3, border_radius=6)
        if i == highlight_idx:
            for cell in pl["cells"]:
                sx, sy = cell_to_screen(*cell)
                pygame.draw.rect(
                    surface, (255, 230, 60), (sx + 3, sy + 3, CELL - 6, CELL - 6), 3
                )


# ------------------ INTERACTION + WIN ------------------
selected_idx = None
mouse_offset = (0, 0)
mouse_dragging = False
pre_drag_pos = None
today = datetime.date.today()


def get_today_labels():
    month_str = today.strftime("%b").upper()
    weekday_str = today.strftime("%a").upper()
    month_cell = None
    date_cell = None
    weekday_cell = None
    for pos, info in cell_label.items():
        if info.get("type") == "month" and info.get("text") == month_str:
            month_cell = pos
        elif info.get("type") == "date" and info.get("text") == str(today.day):
            date_cell = pos
        elif info.get("type") == "weekday" and info.get("text") == weekday_str:
            weekday_cell = pos
    return month_cell, date_cell, weekday_cell


def is_only_today_visible():
    month_cell, date_cell, weekday_cell = get_today_labels()
    if not (month_cell and date_cell and weekday_cell):
        return False
    uncovered = {month_cell, date_cell, weekday_cell}
    covered = set()
    for pl in placed:
        covered.update(pl["cells"])
    for cell in board_mask:
        if cell in uncovered:
            if cell in covered:
                return False
        else:
            if cell not in covered:
                return False
    return True


# ------------------ TIMER HELPERS ------------------
def calculate_elapsed_time(start_time, end_time=None):
    """
    Calculate elapsed time in seconds.
    
    Args:
        start_time: Start timestamp
        end_time: Optional end timestamp. If None, uses current time.
    
    Returns:
        float: Elapsed time in seconds
    """
    if start_time is None:
        return 0.0
    if end_time is not None:
        return end_time - start_time
    return time.time() - start_time


def format_timer(elapsed):
    """
    Format elapsed time as MM:SS.SS string.
    
    Args:
        elapsed: Time in seconds
    
    Returns:
        str: Formatted time string
    """
    mins = int(elapsed // 60)
    secs = elapsed % 60
    return f"Time: {mins}:{secs:05.2f}"


# Confetti
confetti_particles = []


def spawn_confetti(surface, n=120):
    confetti_particles.clear()
    w, h = surface.get_size()
    for _ in range(n):
        x = random.randint(0, w)
        y = random.randint(-h // 2, 0)
        dx = random.uniform(-1, 1)
        dy = random.uniform(2, 5)
        color = random.choice(
            [
                (255, 200, 80),
                (255, 120, 120),
                (120, 200, 255),
                (180, 255, 120),
                (255, 180, 255),
                (255, 255, 255),
            ]
        )
        size = random.randint(4, 10)
        confetti_particles.append(
            {"x": x, "y": y, "dx": dx, "dy": dy, "color": color, "size": size, "ttl": random.randint(30, 80)}  # noqa: E501
        )


def update_confetti(surface):
    w, h = surface.get_size()
    for p in confetti_particles:
        p["x"] += p["dx"]
        p["y"] += p["dy"]
        p["ttl"] -= 1
        if p["y"] > h or p["ttl"] <= 0:
            p["x"] = random.randint(0, w)
            p["y"] = random.randint(-h // 2, 0)
            p["dx"] = random.uniform(-1, 1)
            p["dy"] = random.uniform(2, 5)
            p["ttl"] = random.randint(30, 80)
    for p in confetti_particles:
        pygame.draw.rect(
            surface, p["color"], (int(p["x"]), int(p["y"]), p["size"], p["size"])
        )


def draw_win_screen(surface):
    overlay = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    surface.blit(overlay, (0, 0))
    update_confetti(surface)
    font = create_scaled_font(FONT_SCALE_WIN_TITLE)
    msg = f"You solved it! {today.strftime('%B %d')} is visible!"
    text_surf = font.render(msg, True, (255, 255, 200))
    rect = text_surf.get_rect(
        center=(surface.get_width() // 2, surface.get_height() // 2)
    )
    surface.blit(text_surf, rect)
    font2 = create_scaled_font(FONT_SCALE_WIN_SUBTITLE)
    msg2 = "Press ESC to continue"
    text2 = font2.render(msg2, True, (255, 255, 200))
    rect2 = text2.get_rect(
        center=(surface.get_width() // 2, surface.get_height() // 2 + int(CELL * 1.2))
    )
    surface.blit(text2, rect2)
    if timer_started and timer_start_time is not None and timer_end_time is not None:
        elapsed = calculate_elapsed_time(timer_start_time, timer_end_time)
        timer_msg = format_timer(elapsed)
        font_timer = create_scaled_font(FONT_SCALE_WIN_TIMER)
        timer_surf = font_timer.render(timer_msg, True, (255, 255, 200))
        esc_y = surface.get_height() // 2 + int(CELL * 1.2)
        timer_rect = timer_surf.get_rect(
            center=(surface.get_width() // 2, esc_y + 30 + timer_surf.get_height() // 2)
        )
        surface.blit(timer_surf, timer_rect)


win_mode = False
win_delay_frames = 0
WIN_DELAY = 30
timer_started = False
timer_start_time = None
timer_end_time = None

# ------------------ DLX (Algorithm X) ------------------
class DLXNode:
    __slots__ = ("L", "R", "U", "D", "C", "row_id")

    def __init__(self):
        self.L = self.R = self.U = self.D = self
        self.C = None
        self.row_id = None


class DLXColumn(DLXNode):
    __slots__ = ("name", "size")

    def __init__(self, name):
        super().__init__()
        self.name = name
        self.size = 0


class DLX:
    def __init__(self):
        self.header = DLXColumn("header")
        self.columns = []
        self.solution = []
        self.time_limit = None
        self.start_time = None
        self.solutions = []
        self.max_solutions = None

    def add_column(self, name):
        c = DLXColumn(name)
        c.R = self.header
        c.L = self.header.L
        self.header.L.R = c
        self.header.L = c
        self.columns.append(c)
        return c

    def add_row(self, row_id, col_objs):
        first = None
        for c in col_objs:
            n = DLXNode()
            n.C = c
            n.row_id = row_id
            n.U = c.U
            n.D = c
            c.U.D = n
            c.U = n
            c.size += 1
            if first is None:
                first = n
                n.R = n.L = n
            else:
                n.R = first
                n.L = first.L
                first.L.R = n
                first.L = n

    def cover(self, c):
        c.R.L = c.L
        c.L.R = c.R
        i = c.D
        while i != c:
            j = i.R
            while j != i:
                j.D.U = j.U
                j.U.D = j.D
                j.C.size -= 1
                j = j.R
            i = i.D

    def uncover(self, c):
        i = c.U
        while i != c:
            j = i.L
            while j != i:
                j.C.size += 1
                j.D.U = j
                j.U.D = j
                j = j.L
            i = i.U
        c.R.L = c
        c.L.R = c

    def choose_column(self):
        c = self.header.R
        best = c
        while c != self.header:
            if c.size < best.size:
                best = c
            c = c.R
        return best

    def search(self):
        if self.time_limit is not None and (time.time() - self.start_time) > self.time_limit:  # noqa: E501
            return None
        if self.header.R == self.header:
            return list(self.solution)
        c = self.choose_column()
        if c.size == 0:
            return None
        self.cover(c)
        r = c.D
        while r != c:
            self.solution.append(r)
            j = r.R
            while j != r:
                self.cover(j.C)
                j = j.R
            out = self.search()
            if out is not None:
                return out
            j = r.L
            while j != r:
                self.uncover(j.C)
                j = j.L
            self.solution.pop()
            r = r.D
            if self.time_limit is not None and (time.time() - self.start_time) > self.time_limit:  # noqa: E501
                return None
        self.uncover(c)
        return None

    def solve(self, time_limit=None):
        self.time_limit = time_limit
        self.start_time = time.time()
        return self.search()

    def _search_all(self):
        if self.time_limit is not None and (time.time() - self.start_time) > self.time_limit:  # noqa: E501
            return
        if self.max_solutions is not None and len(self.solutions) >= self.max_solutions:
            return
        if self.header.R == self.header:
            self.solutions.append(list(self.solution))
            return
        c = self.choose_column()
        if c.size == 0:
            return
        self.cover(c)
        r = c.D
        while r != c:
            if self.time_limit is not None and (time.time() - self.start_time) > self.time_limit:  # noqa: E501
                break
            if self.max_solutions is not None and len(self.solutions) >= self.max_solutions:  # noqa: E501
                break
            self.solution.append(r)
            j = r.R
            while j != r:
                self.cover(j.C)
                j = j.R
            self._search_all()
            j = r.L
            while j != r:
                self.uncover(j.C)
                j = j.L
            self.solution.pop()
            r = r.D
        self.uncover(c)

    def solve_all(self, time_limit=None, max_solutions=None):
        self.time_limit = time_limit
        self.max_solutions = max_solutions
        self.start_time = time.time()
        self.solutions = []
        self.solution = []
        self._search_all()
        return self.solutions


# ------------------ Solver: Build Exact Cover ------------------
def all_piece_orientations(base_cells):
    seen = set()
    for flip in [False, True]:
        for rot in range(4):
            oc = tuple(sorted(normalize(oriented_cells(base_cells, rot, flip))))
            if oc not in seen:
                seen.add(oc)
                yield (rot, flip, [c for c in oc])


def generate_placements(forbidden):
    n = len(pieces)
    per_piece = []
    for pid in range(n):
        base = pieces[pid]["cells"]
        piece_list = []
        ori_list = list(all_piece_orientations(base))
        for rot, flip, shape in ori_list:
            maxx = max(x for x, y in shape)
            maxy = max(y for x, y in shape)
            for x0 in range(GRID_W - maxx):
                for y0 in range(GRID_H - maxy):
                    abs_cells = [(x0 + x, y0 + y) for (x, y) in shape]
                    if any(c not in board_mask for c in abs_cells):
                        continue
                    if any(c in forbidden for c in abs_cells):
                        continue
                    piece_list.append((pid, rot, flip, x0, y0, tuple(abs_cells)))
        per_piece.append(piece_list)
    return per_piece


def dlx_build_and_solve_all(forbidden, time_limit=10.0, max_solutions=200):
    to_cover = sorted(set(board_mask) - set(forbidden))
    dlx = DLX()
    cell_col = {}
    for cell in to_cover:
        cell_col[cell] = dlx.add_column(("C", cell))
    piece_col = {}
    for pid in range(len(pieces)):
        piece_col[pid] = dlx.add_column(("P", pid))

    placements = generate_placements(forbidden)

    row_map = []
    for pid, plist in enumerate(placements):
        for (pid, rot, flip, x0, y0, abs_cells) in plist:
            cols = [piece_col[pid]] + [cell_col[c] for c in abs_cells if c in cell_col]
            if len(cols) == 1 + len(abs_cells):
                row_id = len(row_map)
                dlx.add_row(row_id, cols)
                row_map.append((pid, rot, flip, x0, y0, abs_cells))

    sols_nodes = dlx.solve_all(time_limit=time_limit, max_solutions=max_solutions)
    if not sols_nodes:
        return []

    results = []
    for sol_nodes in sols_nodes:
        chosen_rows = []
        for node in sol_nodes:
            chosen_rows.append(row_map[node.row_id])
        chosen_rows.sort(key=lambda t: t[0])
        out = []
        for (pid, rot, flip, x0, y0, abs_cells) in chosen_rows:
            out.append((x0, y0, rot, flip, list(abs_cells)))
        results.append(out)
    return results


# ------------------ Threaded Auto-Solver using DLX ------------------
solving = False
solver_thread = None

solver_solutions = []
solver_index = 0
auto_solve_active = False


def threaded_auto_solve():
    global solving, solver_solutions, solver_index
    month_cell, date_cell, weekday_cell = get_today_labels()
    forbidden = {month_cell, date_cell, weekday_cell}
    if None in forbidden:
        solver_solutions = []
        solving = False
        return
    results = dlx_build_and_solve_all(forbidden, time_limit=10.0, max_solutions=500)
    if not results:
        solver_solutions = []
    else:
        solver_solutions = results
        solver_index = 0
    solving = False


def auto_solve_today():
    global solving, solver_thread, solver_solutions, auto_solve_active
    if solving:
        return
    solving = True
    solver_solutions = []
    auto_solve_active = False
    solver_thread = threading.Thread(target=threaded_auto_solve, daemon=True)
    solver_thread.start()


# ------------------ PLACEMENT VALIDATION ------------------
def placement_valid_for_cells(cells, ignore_idx=None):
    for c in cells:
        if c not in board_mask:
            return False
    for i, pl in enumerate(placed):
        if ignore_idx is not None and i == ignore_idx:
            continue
        for c in pl["cells"]:
            if c in cells:
                return False
    return True


def apply_solution(sol):
    """Place a single solution onto the board (no overlay, no confetti)."""
    n = len(sol)
    if len(placed) < n:
        placed.clear()
        for pid in range(n):
            placed.append(
                {"pid": pid, "pos": (0, 0), "rot": 0, "flip": False, "cells": [], "home": (0, 0)}  # noqa: E501
            )
    for i, (x0, y0, rot, flip, abs_cells) in enumerate(sol):
        placed[i]["pos"] = (x0, y0)
        placed[i]["rot"] = rot
        placed[i]["flip"] = flip
        placed[i]["cells"] = abs_cells
    update_placed_cells()


# ------------------ MAIN LOOP ------------------
running = True
win_mode = False
win_delay_frames = 0
timer_started = False
timer_start_time = None
timer_end_time = None

while running:
    dt = clock.tick(60)
    events = pygame.event.get()
    for ev in events:
        if ev.type == pygame.QUIT:
            running = False

        elif ev.type == pygame.VIDEORESIZE:
            new_w, new_h = ev.w, ev.h
            screen = pygame.display.set_mode((new_w, new_h), pygame.RESIZABLE)
            recompute_palette_layout()

        elif ev.type == pygame.KEYDOWN:
            if win_mode:
                if ev.key == pygame.K_ESCAPE:
                    for pl in placed:
                        pl["pos"] = pl["home"]
                        pl["rot"] = 0
                        pl["flip"] = False
                    update_placed_cells()
                    win_mode = False
                    win_delay_frames = 0
                    timer_started = False
                    timer_start_time = None
                    timer_end_time = None
            else:
                # Theme switching
                if ev.key == pygame.K_t:
                    theme_idx = (theme_idx + 1) % len(THEMES)
                    apply_theme()
                    update_piece_colors()
                    recompute_palette_layout()
                # Auto-solve navigation
                elif auto_solve_active and solver_solutions:
                    if ev.key == pygame.K_LEFT:
                        solver_index = (solver_index - 1) % len(solver_solutions)
                        apply_solution(solver_solutions[solver_index])
                    elif ev.key == pygame.K_RIGHT:
                        solver_index = (solver_index + 1) % len(solver_solutions)
                        apply_solution(solver_solutions[solver_index])
                # Deselect and piece manipulation
                if ev.key == pygame.K_ESCAPE:
                    selected_idx = None
                elif selected_idx is not None:
                    if ev.key == pygame.K_r:
                        placed[selected_idx]["rot"] = (placed[selected_idx]["rot"] + 1) % 4
                        update_placed_cells()
                    elif ev.key == pygame.K_f:
                        placed[selected_idx]["flip"] = not placed[selected_idx]["flip"]
                        update_placed_cells()

        elif not win_mode and ev.type == pygame.MOUSEBUTTONDOWN:
            if ev.button == 3:
                gx, gy = screen_to_cell(*ev.pos)
                found = None
                for i in range(len(placed) - 1, -1, -1):
                    if (gx, gy) in placed[i]["cells"]:
                        found = i
                        break
                if found is not None:
                    placed[found]["pos"] = placed[found]["home"]
                    placed[found]["rot"] = 0
                    placed[found]["flip"] = False
                    update_placed_cells()
                    selected_idx = None
                    mouse_dragging = False
                    pre_drag_pos = None
                continue

            if ev.button == 1:
                try:
                    if button_rect.collidepoint(ev.pos):
                        for pl in placed:
                            pl["pos"] = pl["home"]
                            pl["rot"] = 0
                            pl["flip"] = False
                        update_placed_cells()
                        selected_idx = None
                        mouse_dragging = False
                        pre_drag_pos = None
                        timer_started = False
                        timer_start_time = None
                        timer_end_time = None
                        solver_solutions = []
                        auto_solve_active = False
                        continue
                    if autosolve_button_rect.collidepoint(ev.pos):
                        timer_started = False
                        timer_start_time = None
                        timer_end_time = None
                        auto_solve_today()
                        selected_idx = None
                        mouse_dragging = False
                        pre_drag_pos = None
                        continue
                except NameError:
                    pass

                gx, gy = screen_to_cell(*ev.pos)
                found = None
                for i in range(len(placed) - 1, -1, -1):
                    if (gx, gy) in placed[i]["cells"]:
                        found = i
                        break
                if found is not None:
                    selected_idx = found
                    mouse_dragging = True
                    pre_drag_pos = placed[selected_idx]["pos"]
                    mouse_offset = (
                        gx - placed[selected_idx]["pos"][0],
                        gy - placed[selected_idx]["pos"][1],
                    )
                    auto_solve_active = False
                    if not timer_started:
                        timer_started = True
                        timer_start_time = time.time()
                        timer_end_time = None
                else:
                    selected_idx = None

        elif not win_mode and ev.type == pygame.MOUSEBUTTONUP and ev.button == 1:
            if mouse_dragging and selected_idx is not None:
                gx, gy = screen_to_cell(*ev.pos)
                new_pos = (gx - mouse_offset[0], gy - mouse_offset[1])
                pid = placed[selected_idx]["pid"]
                oc = oriented_cells(
                    pieces[pid]["cells"],
                    placed[selected_idx]["rot"],
                    placed[selected_idx]["flip"],
                )
                candidate = [(new_pos[0] + x, new_pos[1] + y) for (x, y) in oc]
                if placement_valid_for_cells(candidate, selected_idx):
                    placed[selected_idx]["pos"] = new_pos
                    placed[selected_idx]["cells"] = candidate
                else:
                    placed[selected_idx]["pos"] = pre_drag_pos
                    update_placed_cells()
            mouse_dragging = False

        elif (
            not win_mode
            and ev.type == pygame.MOUSEMOTION
            and mouse_dragging
            and selected_idx is not None
        ):
            gx, gy = screen_to_cell(*ev.pos)
            new_pos = (gx - mouse_offset[0], gy - mouse_offset[1])
            pid = placed[selected_idx]["pid"]
            oc = oriented_cells(
                pieces[pid]["cells"],
                placed[selected_idx]["rot"],
                placed[selected_idx]["flip"],
            )
            placed[selected_idx]["pos"] = new_pos
            placed[selected_idx]["cells"] = [
                (new_pos[0] + x, new_pos[1] + y) for (x, y) in oc
            ]

    # Draw
    screen.fill(BG)
    board_y_offset = get_board_y_offset()
    board_surf = pygame.Surface((GRID_W * CELL, GRID_H * CELL), pygame.SRCALPHA)
    draw_board(board_surf, y_offset=0)

    # Removed the board shadow that caused the darker outline around the grid.
    # (We only blit the board itself.)
    screen.blit(board_surf, (0, board_y_offset))

    # Dark area and labels (kept; constrained to the board width)
    dark_area_height = int(CELL * 1.3)
    dark_area_y = board_y_offset + GRID_H * CELL + 8 + int(CELL * 0.2)
    pygame.draw.rect(
        screen, BG, (0, dark_area_y, GRID_W * CELL, dark_area_height), border_radius=12
    )
    theme_label_font = create_scaled_font(FONT_SCALE_THEME_LABEL, bold=True)
    theme_name = get_theme()["name"]
    label_surf = theme_label_font.render(
        f"Theme: {theme_name} (T to change)", True, TEXT_COL
    )
    controls_font = create_scaled_font(FONT_SCALE_CONTROLS)
    controls_text = (
        "R: Rotate   F: Flip   ESC: Deselect/Reset   \nRight mouse click: Reset singular piece   ←/→: Browse Auto-Solve"
    )
    text_y = dark_area_y + 10
    screen.blit(label_surf, (12, text_y))
    # Render controls text on two lines
    controls_lines = controls_text.split("\n")
    y_offset = text_y + label_surf.get_height() + 4
    for line in controls_lines:
        controls_surf = controls_font.render(line, True, TEXT_COL)
        screen.blit(controls_surf, (12, y_offset))
        y_offset += controls_surf.get_height() + 2

    # Buttons
    button_w = int(CELL * 4.5)
    button_h = int(CELL * 0.9)
    button_x = (GRID_W * CELL - button_w) // 2
    button_y = text_y + label_surf.get_height() + 4 + controls_surf.get_height() + int(
        CELL * 0.5
    )
    button_rect = pygame.Rect(button_x, button_y, button_w, button_h)
    btn_bg, btn_border, btn_text_col = get_button_theme_colors("normal")
    draw_button(screen, button_rect, "Reset Board", btn_bg, btn_border, btn_text_col)

    autosolve_button_y = button_y + button_h + int(CELL * 0.3)
    autosolve_button_rect = pygame.Rect(
        button_x, autosolve_button_y, button_w, button_h
    )
    auto_bg, auto_border, auto_text_col = get_button_theme_colors("autosolve")
    draw_button(screen, autosolve_button_rect, "Auto-Solve", auto_bg, auto_border, auto_text_col)

    draw_pieces(screen, selected_idx)

    # Solving overlay
    if solving:
        overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 120))
        font = create_scaled_font(FONT_SCALE_SOLVING, bold=True)
        text_surf = font.render("Solving...", True, (255, 255, 80))
        rect = text_surf.get_rect(
            center=(screen.get_width() // 2, screen.get_height() // 2)
        )
        overlay.blit(text_surf, rect)
        screen.blit(overlay, (0, 0))

    # Apply first solver result once ready (no winner screen)
    if not solving and solver_solutions and not auto_solve_active:
        apply_solution(solver_solutions[solver_index])
        auto_solve_active = True
        timer_started = False
        timer_start_time = None
        timer_end_time = None

    # Win / timer
    if not win_mode:
        if not auto_solve_active and is_only_today_visible():
            if win_delay_frames == 0:
                win_delay_frames = WIN_DELAY
        else:
            win_delay_frames = 0 if auto_solve_active else win_delay_frames
        if win_delay_frames > 0:
            win_delay_frames -= 1
            if win_delay_frames == 0 and not auto_solve_active:
                win_mode = True
                spawn_confetti(screen)
                if timer_started and timer_end_time is None:
                    timer_end_time = time.time()

    if win_mode:
        draw_win_screen(screen)
    else:
        # Display timer
        if timer_started:
            elapsed = calculate_elapsed_time(timer_start_time, timer_end_time)
        else:
            elapsed = 0.0
        timer_msg = format_timer(elapsed)
        font_timer = create_scaled_font(FONT_SCALE_TIMER)
        timer_surf = font_timer.render(timer_msg, True, (255, 255, 200))
        pad = int(CELL * 0.3)
        timer_rect = timer_surf.get_rect(topright=(screen.get_width() - pad, pad))
        screen.blit(timer_surf, timer_rect)

        # Display solution index when auto-solving
        if auto_solve_active and solver_solutions:
            idx_font = create_scaled_font(FONT_SCALE_SOLUTION_INDEX, bold=True)
            s = f"Solution {solver_index + 1}/{len(solver_solutions)}  (← / →)"
            idx_surf = idx_font.render(s, True, (255, 255, 255))
            idx_rect = idx_surf.get_rect(
                center=(
                    GRID_W * CELL // 2,
                    autosolve_button_y + button_h + int(CELL * 0.9),
                )
            )
            screen.blit(idx_surf, idx_rect)

    pygame.display.flip()

pygame.quit()
sys.exit()
