import tkinter as tk
from utilities.constants import FONT_SIZE


# Creates a button with specified parameters
def create_button(
    text, command, anchor, width, padx, pady, x, y, frame=None, side=tk.TOP
):
    if frame is None:
        frame = tk.Tk()
    button = tk.Button(
        frame,
        text=text,
        font=("Arial", FONT_SIZE // 2),
        command=command,
        width=width,
        padx=padx,
        pady=pady,
    )
    button.pack(anchor=anchor, padx=x, pady=y, side=side)


# Clears all the widgets in the root window.
# Used when switching between different pages
def clear_window(window):
    for widget in window.winfo_children():
        widget.destroy()
