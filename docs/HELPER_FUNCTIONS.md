# Helper Functions Documentation

This document provides detailed explanations of the helper functions in `caldendar_puzzle.py`.

## Window & Layout Helpers

### `get_piece_dimensions(piece_collection=None)`

Calculate the maximum width and height across all pieces in a collection.

**Parameters:**
- `piece_collection`: Optional list of pieces to measure. If None, uses `PIECES_BASE` by default.

**Returns:**
- `tuple`: (max_width, max_height) - The maximum dimensions needed to fit any piece.

**Usage:**
```python
wmax, hmax = get_piece_dimensions(pieces)
wmax, hmax = get_piece_dimensions(PIECES_BASE)
```

**How it works:**
- Iterates through all pieces in the collection
- Handles both raw coordinate lists and piece dictionaries with 'cells' key
- Returns the largest width and height found, with a minimum of 1

---

### `compute_best_cell_size(win_w, win_h, num_pieces, wmax, hmax)`

Compute the optimal cell size for given window dimensions and piece constraints.

**Parameters:**
- `win_w`: Window width in pixels
- `win_h`: Window height in pixels
- `num_pieces`: Number of pieces to fit in the palette
- `wmax`: Maximum piece width in cells
- `hmax`: Maximum piece height in cells

**Returns:**
- `int`: Optimal cell size in pixels (minimum 16)

**Usage:**
```python
cell_size = compute_best_cell_size(1000, 600, 10, 4, 5)
```

**How it works:**
- Tests different palette row configurations (1 to 2 rows)
- Calculates total cells needed for board, palette, and controls
- Finds the configuration that yields the largest possible cell size
- Ensures minimum cell size of 16 pixels

---

### `compute_initial_cell(win_w, win_h)`

Compute initial cell size based on PIECES_BASE dimensions.

**Parameters:**
- `win_w`: Window width in pixels
- `win_h`: Window height in pixels

**Returns:**
- `int`: Initial cell size in pixels

**Usage:**
```python
CELL = compute_initial_cell(1000, 600)
```

**How it works:**
- Gets piece dimensions from PIECES_BASE
- Calls `compute_best_cell_size()` with these dimensions

---

### `compute_best_layout(win_w_, win_h_)`

Compute the best layout configuration for the pieces palette.

**Parameters:**
- `win_w_`: Window width in pixels
- `win_h_`: Window height in pixels

**Returns:**
- `dict`: Layout configuration containing:
  - `cell`: Cell size in pixels
  - `palette_rows`: Number of rows in palette
  - `palette_cols`: Number of columns in palette
  - `controls_rows`: Number of rows for controls
  - `wmax`: Maximum piece width
  - `hmax`: Maximum piece height

**Usage:**
```python
layout = compute_best_layout(1000, 600)
CELL = layout["cell"]
```

**How it works:**
- Gets current piece dimensions
- Tests different palette configurations
- Returns the configuration with the largest cell size
- Used by `recompute_palette_layout()` to update layout on window resize

---

## Font Helpers

### `create_scaled_font(scale_factor, bold=False)`

Create a font scaled by the current CELL size.

**Parameters:**
- `scale_factor`: Multiplier for CELL size (e.g., 0.5 for half CELL size)
- `bold`: Whether to use bold font (default: False)

**Returns:**
- `pygame.font.Font`: Font object scaled to `max(12, int(CELL * scale_factor))`

**Usage:**
```python
month_font = create_scaled_font(FONT_SCALE_MONTH)
title_font = create_scaled_font(FONT_SCALE_WIN_TITLE, bold=True)
```

**How it works:**
- Multiplies CELL by scale_factor
- Ensures minimum font size of 12 pixels
- Delegates to `choose_font()` for actual font creation

**Related constants:**
- `FONT_SCALE_CONTROLS = 0.28`
- `FONT_SCALE_WEEKDAY = 0.33`
- `FONT_SCALE_MONTH = 0.35`
- `FONT_SCALE_THEME_LABEL = 0.35`
- `FONT_SCALE_DATE = 0.45`
- `FONT_SCALE_BUTTON = 0.45`
- `FONT_SCALE_SOLUTION_INDEX = 0.45`
- `FONT_SCALE_WIN_SUBTITLE = 0.6`
- `FONT_SCALE_TIMER = 0.7`
- `FONT_SCALE_WIN_TIMER = 0.8`
- `FONT_SCALE_SOLVING = 1.0`
- `FONT_SCALE_WIN_TITLE = 1.2`

---

## Timer Helpers

### `calculate_elapsed_time(start_time, end_time=None)`

Calculate elapsed time in seconds.

**Parameters:**
- `start_time`: Start timestamp (from `time.time()`)
- `end_time`: Optional end timestamp. If None, uses current time.

**Returns:**
- `float`: Elapsed time in seconds, or 0.0 if start_time is None

**Usage:**
```python
elapsed = calculate_elapsed_time(timer_start_time, timer_end_time)
elapsed = calculate_elapsed_time(timer_start_time)  # ongoing timer
```

**How it works:**
- Returns 0.0 if start_time is None
- Returns difference between end_time and start_time if both provided
- Returns difference between current time and start_time if end_time is None

---

### `format_timer(elapsed)`

Format elapsed time as a MM:SS.SS string.

**Parameters:**
- `elapsed`: Time in seconds (float)

**Returns:**
- `str`: Formatted string like "Time: 2:05.50"

**Usage:**
```python
elapsed = calculate_elapsed_time(start, end)
display_text = format_timer(elapsed)
```

**How it works:**
- Divides elapsed time into minutes and seconds
- Formats seconds with 2 decimal places, zero-padded to 5 total characters

---

## Draw Helpers

### `draw_button(surface, rect, text, bg_color, border_color, text_color, font_scale=FONT_SCALE_BUTTON)`

Draw a button with text centered on it.

**Parameters:**
- `surface`: Pygame surface to draw on
- `rect`: pygame.Rect for button position and size
- `text`: Button text string
- `bg_color`: Background color tuple (R, G, B)
- `border_color`: Border color tuple (R, G, B)
- `text_color`: Text color tuple (R, G, B)
- `font_scale`: Font scale factor (default: FONT_SCALE_BUTTON)

**Returns:**
- None (draws directly on surface)

**Usage:**
```python
btn_bg, btn_border, btn_text = get_button_theme_colors("normal")
draw_button(screen, button_rect, "Reset Board", btn_bg, btn_border, btn_text)
```

**How it works:**
- Draws filled rectangle with rounded corners (radius 10)
- Draws border with 2-pixel width
- Renders text with scaled font (bold by default)
- Centers text on button

---

### `get_button_theme_colors(button_type="normal")`

Get theme colors for a button.

**Parameters:**
- `button_type`: Either "normal" or "autosolve"

**Returns:**
- `tuple`: (bg_color, border_color, text_color)

**Usage:**
```python
bg, border, text = get_button_theme_colors("normal")
auto_bg, auto_border, auto_text = get_button_theme_colors("autosolve")
```

**How it works:**
- Returns `(AUTOSOLVE_BG, AUTOSOLVE_BORDER, AUTOSOLVE_TEXT)` for "autosolve"
- Returns `(BTN_BG, BTN_BORDER, BTN_TEXT)` for "normal" or any other value
- Colors are automatically updated when theme changes via `apply_theme()`

---

## Best Practices

### When to use each helper:

1. **Layout changes**: Use `compute_best_layout()` when window resizes
2. **Font creation**: Always use `create_scaled_font()` with appropriate constant
3. **Button drawing**: Use `draw_button()` for all button UI elements
4. **Timer display**: Use `calculate_elapsed_time()` + `format_timer()` for consistency
5. **Piece operations**: Use `get_piece_dimensions()` instead of inline calculations

### Example patterns:

**Before refactoring:**
```python
month_font = choose_font(max(12, int(CELL * 0.35)))
pygame.draw.rect(screen, BTN_BG, button_rect, border_radius=10)
pygame.draw.rect(screen, BTN_BORDER, button_rect, 2, border_radius=10)
btn_font = choose_font(int(CELL * 0.45), bold=True)
btn_text = btn_font.render("Reset", True, BTN_TEXT)
```

**After refactoring:**
```python
month_font = create_scaled_font(FONT_SCALE_MONTH)
bg, border, text = get_button_theme_colors("normal")
draw_button(screen, button_rect, "Reset", bg, border, text)
```
