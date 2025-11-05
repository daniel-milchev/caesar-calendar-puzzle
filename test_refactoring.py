#!/usr/bin/env python3
"""
Simple tests to verify the refactored code maintains functionality.
"""
import sys
import pygame

# Initialize pygame before importing the module
pygame.init()

# Import after pygame.init()
import caldendar_puzzle as cp


def test_font_scale_constants():
    """Test that all font scale constants are defined."""
    constants = [
        'FONT_SCALE_CONTROLS',
        'FONT_SCALE_WEEKDAY', 
        'FONT_SCALE_MONTH',
        'FONT_SCALE_THEME_LABEL',
        'FONT_SCALE_DATE',
        'FONT_SCALE_BUTTON',
        'FONT_SCALE_SOLUTION_INDEX',
        'FONT_SCALE_WIN_SUBTITLE',
        'FONT_SCALE_TIMER',
        'FONT_SCALE_WIN_TIMER',
        'FONT_SCALE_SOLVING',
        'FONT_SCALE_WIN_TITLE',
    ]
    
    for const in constants:
        assert hasattr(cp, const), f"Missing constant: {const}"
        value = getattr(cp, const)
        assert isinstance(value, float), f"{const} should be a float"
        assert 0 < value <= 2.0, f"{const} should be between 0 and 2.0"
    
    print("✓ All font scale constants defined correctly")


def test_create_scaled_font():
    """Test the create_scaled_font helper function."""
    # Test with default CELL value
    font = cp.create_scaled_font(0.5)
    assert font is not None, "Should create a font"
    assert isinstance(font, pygame.font.Font), "Should return a Font object"
    
    # Test with bold
    bold_font = cp.create_scaled_font(0.5, bold=True)
    assert bold_font is not None, "Should create a bold font"
    
    print("✓ create_scaled_font() works correctly")


def test_get_piece_dimensions():
    """Test the get_piece_dimensions helper function."""
    # Test with PIECES_BASE
    wmax, hmax = cp.get_piece_dimensions(cp.PIECES_BASE)
    assert wmax >= 1, "Width should be at least 1"
    assert hmax >= 1, "Height should be at least 1"
    assert wmax <= 10, "Width should be reasonable"
    assert hmax <= 10, "Height should be reasonable"
    
    # Test with pieces
    wmax2, hmax2 = cp.get_piece_dimensions(cp.pieces)
    assert wmax2 >= 1, "Width should be at least 1"
    assert hmax2 >= 1, "Height should be at least 1"
    
    print(f"✓ get_piece_dimensions() works correctly (wmax={wmax}, hmax={hmax})")


def test_compute_best_cell_size():
    """Test the compute_best_cell_size helper function."""
    # Test with reasonable window dimensions
    cell_size = cp.compute_best_cell_size(1000, 600, 10, 4, 5)
    assert cell_size >= 16, "Cell size should be at least 16"
    assert cell_size <= 1000, "Cell size should be reasonable"
    
    # Test with small window
    cell_size_small = cp.compute_best_cell_size(400, 300, 10, 4, 5)
    assert cell_size_small >= 16, "Should have minimum cell size"
    assert cell_size_small <= cell_size, "Smaller window should have smaller cells"
    
    print(f"✓ compute_best_cell_size() works correctly (size={cell_size})")


def test_timer_helpers():
    """Test timer helper functions."""
    import time
    
    # Test calculate_elapsed_time with None start
    elapsed = cp.calculate_elapsed_time(None)
    assert elapsed == 0.0, "Should return 0.0 for None start time"
    
    # Test with start and end time
    start = time.time()
    time.sleep(0.1)
    end = time.time()
    elapsed = cp.calculate_elapsed_time(start, end)
    assert 0.09 <= elapsed <= 0.15, f"Should calculate elapsed time correctly: {elapsed}"
    
    # Test format_timer
    timer_str = cp.format_timer(125.5)
    assert "Time:" in timer_str, "Should contain 'Time:'"
    assert "2:" in timer_str, "Should show 2 minutes"
    assert "05.50" in timer_str, "Should show 5.50 seconds"
    
    print(f"✓ Timer helpers work correctly (format: {timer_str})")


def test_button_theme_colors():
    """Test get_button_theme_colors helper function."""
    # Test normal button
    bg, border, text = cp.get_button_theme_colors("normal")
    assert bg is not None, "Should return bg color"
    assert border is not None, "Should return border color"
    assert text is not None, "Should return text color"
    assert len(bg) == 3, "Color should be RGB tuple"
    
    # Test autosolve button
    bg2, border2, text2 = cp.get_button_theme_colors("autosolve")
    assert bg2 is not None, "Should return bg color for autosolve"
    assert len(bg2) == 3, "Color should be RGB tuple"
    
    print("✓ get_button_theme_colors() works correctly")


def test_draw_button():
    """Test draw_button helper function."""
    # Create a test surface
    surface = pygame.Surface((200, 100))
    rect = pygame.Rect(10, 10, 180, 80)
    
    # Should not raise an exception
    cp.draw_button(
        surface, rect, "Test Button",
        (100, 100, 100), (200, 200, 200), (255, 255, 255)
    )
    
    print("✓ draw_button() works correctly")


def test_themes_exist():
    """Test that all three themes are properly defined."""
    assert len(cp.THEMES) == 3, "Should have 3 themes"
    
    theme_names = [t["name"] for t in cp.THEMES]
    assert "Nord" in theme_names, "Should have Nord theme"
    assert "Wood" in theme_names, "Should have Wood theme"
    assert "Solarized" in theme_names, "Should have Solarized theme"
    
    # Test that each theme has required keys
    required_keys = [
        "BG", "BOARD_TILE", "VOID_TILE", "CELL_BORDER", "TEXT_COL",
        "PIECE_COLORS", "BTN_BG", "BTN_BORDER", "BTN_TEXT",
        "AUTOSOLVE_BG", "AUTOSOLVE_BORDER", "AUTOSOLVE_TEXT"
    ]
    
    for theme in cp.THEMES:
        for key in required_keys:
            assert key in theme, f"Theme {theme['name']} missing key: {key}"
    
    print(f"✓ All 3 themes properly defined: {', '.join(theme_names)}")


def test_layout_computation():
    """Test that layout computation produces valid results."""
    layout = cp.compute_best_layout(1000, 600)
    
    assert "cell" in layout, "Layout should have cell size"
    assert "palette_rows" in layout, "Layout should have palette_rows"
    assert "palette_cols" in layout, "Layout should have palette_cols"
    assert "wmax" in layout, "Layout should have wmax"
    assert "hmax" in layout, "Layout should have hmax"
    
    assert layout["cell"] >= 16, "Cell should be at least 16"
    assert layout["palette_rows"] >= 1, "Should have at least 1 row"
    assert layout["palette_cols"] >= 1, "Should have at least 1 col"
    
    print(f"✓ Layout computation works (cell={layout['cell']}, rows={layout['palette_rows']}, cols={layout['palette_cols']})")


def run_all_tests():
    """Run all tests."""
    print("\n=== Running Refactoring Tests ===\n")
    
    try:
        test_font_scale_constants()
        test_create_scaled_font()
        test_get_piece_dimensions()
        test_compute_best_cell_size()
        test_timer_helpers()
        test_button_theme_colors()
        test_draw_button()
        test_themes_exist()
        test_layout_computation()
        
        print("\n=== ✅ All Tests Passed! ===\n")
        return 0
    except AssertionError as e:
        print(f"\n=== ❌ Test Failed: {e} ===\n")
        return 1
    except Exception as e:
        print(f"\n=== ❌ Unexpected Error: {e} ===\n")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(run_all_tests())
