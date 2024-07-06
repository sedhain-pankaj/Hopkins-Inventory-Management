# This file contains the functions to open the menu context and the back button to return to the root window

from utils import create_button, clear_window
from menu.overall_stock import open_overall_stock
from menu.todays_cornice_log import open_todays_cornice_log
from menu.hours_worked import open_hours_worked
from menu.cornice_rate import open_cornice_rates


# Opens the menu context with the back button and menu buttons
def open_menu_context(window):
    clear_window(window)

    # Create and display the back button
    create_button("⇦", lambda: back_to_root(window), "nw", 2, 5, 5, 10, 10, window)

    # Dictionary containing the text and command for each button
    button_texts = {
        "Overall Stock": lambda: open_overall_stock(window),
        "Today's Cornice Log": lambda: open_todays_cornice_log(window),
        "Hours Worked": lambda: open_hours_worked(window),
        "Cornice Rates": lambda: open_cornice_rates(window),
    }

    # FOR loop to create and display the menu buttons
    for text, command in button_texts.items():
        create_button(text, command, "center", 20, 20, 20, 5, 5, window)


# Clears the window and displays the root window components
def back_to_root(window):
    # Use import statement inside the function to avoid circular import
    # When going back to the previous window
    from date_time import (
        root_window_components,
    )

    clear_window(window)
    root_window_components(window)
