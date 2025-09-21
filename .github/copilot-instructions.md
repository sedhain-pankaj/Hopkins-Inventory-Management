# Hopkins Plaster Studio - Inventory Management System

## Project Architecture

This is a fullscreen Tkinter desktop application for plaster cornice inventory management. Entry point is `index.py` (not `main.py` as mentioned in README).

### Module Structure

- **`index.py`**: Application entry point with icon loading
- **`pages/`**: UI screens (date_time, main_menu, preview_csv, hours_worked, todays_cornice_log)
- **`utilities/`**: Core functionality (constants, utils, password_verification, undo_history, cell_mods, column_width)
- **`assets/`**: CSV data files and logo

## Critical Patterns

### Navigation & Circular Imports

Always use local imports inside navigation functions to prevent circular imports:

```python
def back_to_root(window):
    from pages.date_time import root_window_components  # Import here, not at top
    clear_window(window)
    root_window_components(window)
```

### Window Management

- Use `clear_window(window)` before every screen transition
- All UI uses fullscreen mode: `window.attributes("-fullscreen", True)`
- Logo loading with exception handling in `index.py`

### Constants & File Paths

- `utilities/constants.py` uses `os.path.dirname(os.path.dirname(...))` to go up one level from utilities/
- `FONT_SIZE = 70 if os.name == "nt" else 128` (Windows vs others)
- Password protection with SHA-256 hash: `PASSWORD_HASH` constant

### CSV Table Management

The `preview_csv()` function implements sophisticated table editing:

- **Alternating row colors**: `tree.tag_configure("odd"/"even")`
- **Undo system**: `utilities/undo_history.py` with state stack
- **Cell editing**: Double-click cells, Entry widgets with focus binding
- **Password-protected saves**: Modal dialog with hash verification
- **Dynamic column widths**: `utilities/column_width.py`

### UI Component Pattern

Use `utilities/utils.create_button()` with specific parameter order:

```python
create_button(text, command, anchor, width, padx, pady, x, y, frame, side)
```

## Data Flow

1. **Stock Management**: `overall_stock.csv` (editable) vs `cornice_rate.csv` (read-only)
2. **State Management**: Undo history stack with max 20 states
3. **Authentication**: Save operations require password verification

## Key Files for Development

- **`utilities/cell_mods.py`**: Table cell editing logic
- **`utilities/password_verification.py`**: Modal password dialogs
- **`pages/preview_csv.py`**: Main table interface with scrollbars and styling
- **`utilities/undo_history.py`**: State management for table operations

## Unicode UI Elements

Uses emoji buttons: ⇦ (back), 💾 (save), ↩ (undo), ➕ (add), 🗑️ (delete)
