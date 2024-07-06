# This file contains the code for the cornice and its per unit rate

import tkinter as tk
import tkinter.ttk as ttk
import csv
from utils import create_button, clear_window
from constants import FILEPATH


# Opens the cornice rates page with the back and save button
def open_cornice_rates(window):
    clear_window(window)

    # Import inside the function to avoid circular import
    # When going back to the previous window
    from menu.menu import open_menu_context

    # Create a frame to hold the back and save button in parallel alignment
    button_frame = tk.Frame(window)
    button_frame.pack(side=tk.TOP, fill=tk.X, pady=10)

    # Create and display the back and save button with button_frame as the parameter instead of window
    create_button(
        "⇦",
        lambda: open_menu_context(window),
        "nw",
        2,
        5,
        5,
        10,
        10,
        button_frame,
        tk.LEFT,
    )
    create_button(
        "💾",
        lambda: save_to_csv(tree, FILEPATH),
        "nw",
        2,
        5,
        5,
        10,
        10,
        button_frame,
        tk.RIGHT,
    )

    # Create and display the cornice rates table from a CSV file
    tree = ttk.Treeview(
        window, show="headings"
    )  # Set show to "headings" to remove the extra empty column
    tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    # Open and read the CSV file
    with open(FILEPATH, newline="", encoding="utf-8") as csvfile:
        csvreader = csv.reader(csvfile)
        headers = next(csvreader)  # Extract the first row as headers

        # Configure the Treeview to display all columns
        tree["columns"] = headers
        for col in headers:
            tree.heading(col, text=col)
            tree.column(col, anchor=tk.CENTER)

        # Insert rows into the Treeview, including all columns
        for row in csvreader:
            tree.insert("", "end", values=row)

    # Bind the double-click event to the Treeview
    tree.bind("<Double-1>", lambda event: update_cell(event, tree))


# Update the cell value when double-clicked
def update_cell(event, tree):
    item = tree.identify("item", event.x, event.y)
    column = tree.identify_column(event.x)

    if item and column:  # Ensure an item and column were clicked
        column_index = int(column.replace("#", "")) - 1  # Convert to 0-based index
        entry = tk.Entry(tree, fg="black", bg="white", selectbackground="#1c75bc")

        cell_value = tree.item(item, "values")[column_index]
        entry.insert(0, cell_value)
        entry.select_range(0, tk.END)
        entry.focus()

        # Calculate the cell's rectangle area
        cell_x, cell_y, cell_width, cell_height = tree.bbox(item, column)
        entry.place(x=cell_x, y=cell_y, width=cell_width, height=cell_height)

        # Bind Return key to save the new value and remove the entry widget
        entry.bind(
            "<Return>", lambda e: save_edit(tree, item, column_index, entry.get())
        )
        # Bind focus loss to save and remove the entry widget
        entry.bind(
            "<FocusOut>", lambda e: save_edit(tree, item, column_index, entry.get())
        )


# Update the Treeview item with the new value and remove the entry widget
def save_edit(tree, item, column_index, new_value):
    values = list(tree.item(item, "values"))
    values[column_index] = new_value
    tree.item(item, values=values)
    for widget in tree.place_slaves():
        widget.destroy()  # Remove the entry widget


# Save the Treeview data to a CSV file
def save_to_csv(tree, filepath):
    with open(filepath, "w", newline="", encoding="utf-8") as csvfile:
        csvwriter = csv.writer(csvfile)
        # Write the headers
        csvwriter.writerow(tree["columns"])
        # Write the updated rows
        for item in tree.get_children():
            csvwriter.writerow(tree.item(item)["values"])
