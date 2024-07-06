import tkinter as tk
from date_time import root_window_components


# Creates the root window using tkinter
def create_root_window():
    window = tk.Tk()
    window.title("Hopkins Plaster Studio - Inventory Management System")
    window.attributes("-fullscreen", True)
    return window


# Add the root window components
if __name__ == "__main__":
    window = create_root_window()
    root_window_components(window)
    window.mainloop()
