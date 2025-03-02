import tkinter as tk
import datetime
from constants import FONT_SIZE, TIME_DELAY
from Utilities.utils import create_button
from menu.menu import open_menu_context

time_label = None  # Global variable to store the time label


# Shows the current date and time on the root window
def show_date_time(window):
    global time_label
    time_label = tk.Label(window, font=("Arial", FONT_SIZE), anchor="center")
    time_label.pack(expand=True)
    update_time()


# Formats the current date and time and updates the time label every TIME_DELAY milliseconds
def update_time():
    current_time = datetime.datetime.now().strftime("%d %b %Y\n%I:%M:%S %p")
    time_label.config(text=current_time)
    time_label.after(TIME_DELAY, update_time)


# Shows the datetime and start button on the root window
def root_window_components(window):
    show_date_time(window)

    # Create and display the start button
    create_button(
        "Start",
        lambda: open_menu_context(window),
        "center",
        10,
        25,
        25,
        100,
        100,
        window,
    )
