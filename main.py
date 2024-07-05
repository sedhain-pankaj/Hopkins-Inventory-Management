import tkinter as tk
import datetime
from constants import FONT_SIZE, TIME_DELAY

# Global variables
window = None
time_label = None

# Function to update the time label with the current date and time
def show_date_time():
    current_time = datetime.datetime.now().strftime("%d %b %Y\n%I:%M:%S %p")
    time_label.config(text=current_time)
    time_label.after(TIME_DELAY, show_date_time)

# Function to create the main application window
def create_main_window():
    global window
    window = tk.Tk()
    window.title("Hopkins Plaster Studio - Inventory Management System")
    # window.attributes("-fullscreen", True)
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    window.geometry(f"{screen_width}x{screen_height}+0+0")

# Function to initialize and display UI components in the main window
def initialize_ui_components():
    global time_label
    time_label = tk.Label(window, font=("Arial", FONT_SIZE), anchor="center")
    time_label.pack(expand=True)
    show_date_time()

    # Create and display the start button
    start_button = tk.Button(window, text="Start", font=("Arial", FONT_SIZE), command=open_entry_window)
    start_button.pack(pady=50, padx=50)

# Function to open the entry window, replacing the main window's content
def open_entry_window():
    clear_window()

    # Create and display the back button
    back_button = tk.Button(window, text="Back", command=back_to_main)
    back_button.pack(anchor="nw", padx=10, pady=10)

    # Create and display buttons for user selection
    button_texts = ["Overall Stock", "Today's Cornice Log", "Hours Worked", "Cornice Rates"]
    for text in button_texts:
        button = tk.Button(window, text=text)
        button.pack(pady=10)

# Function to clear the window and re-initialize the main UI components
def back_to_main():
    clear_window()
    initialize_ui_components()

# Function to remove all child widgets from the window
def clear_window():
    for widget in window.winfo_children():
        widget.destroy()

# Main application setup
create_main_window()
initialize_ui_components()
window.mainloop()
