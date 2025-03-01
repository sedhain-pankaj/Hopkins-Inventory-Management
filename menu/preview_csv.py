# This file contains the code to preview a CSV file.

import tkinter as tk
import tkinter.ttk as ttk
import csv
from utils import create_button, clear_window


# Opens the cornice rates page with the back and save button
def preview_csv(window, FILEPATH, enable_edit):
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

    # If enable_edit is True, allow adding and deleting rows
    if enable_edit:
        create_button(
            "➕",
            lambda: add_row_below_selected(tree),
            "nw",
            2,
            5,
            5,
            10,
            10,
            button_frame,
            tk.RIGHT,
        )
        create_button(
            "🗑️",
            lambda: delete_selected_row(tree),
            "nw",
            2,
            5,
            5,
            10,
            10,
            button_frame,
            tk.RIGHT,
        )

        # Create and style the cornice rates tables from a CSV file
    style = ttk.Style()
    style.theme_use("clam")  # Set the style to "clam" for a cleaner look
    style.configure("Treeview", rowheight=25, font=("Arial", 14))
    style.configure("Treeview.Heading", rowheight=25, font=("Arial", 16, "bold"))

    # Create a frame to contain the Treeview and scrollbars
    tree_frame = tk.Frame(window)
    tree_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    # Create the Treeview
    tree = ttk.Treeview(tree_frame, show="headings")

    # Create vertical scrollbar
    vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
    vsb.grid(row=0, column=1, sticky="ns")

    # Create horizontal scrollbar
    hsb = ttk.Scrollbar(tree_frame, orient="horizontal", command=tree.xview)
    hsb.grid(row=1, column=0, sticky="ew")

    # Configure the Treeview to use scrollbars
    tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
    tree.grid(row=0, column=0, sticky="nsew")

    # Configure the grid weights to allow the Treeview to expand
    tree_frame.grid_rowconfigure(0, weight=1)
    tree_frame.grid_columnconfigure(0, weight=1)

    # Open and read the CSV file
    with open(FILEPATH, newline="", encoding="utf-8") as csvfile:
        csvreader = csv.reader(csvfile)
        headers = next(csvreader)  # Extract the first row as headers

        # Read all rows to determine column widths
        rows = list(csvreader)

        # Create unique column identifiers
        unique_ids = [f"col{i}" for i in range(len(headers))]

        # Configure the Treeview to display all columns using unique IDs
        tree["columns"] = unique_ids

        # Calculate the appropriate width for each column
        for idx, col_id in enumerate(unique_ids):
            # Set column heading
            tree.heading(col_id, text=headers[idx])

            # Calculate width for header (headers are bold and larger)
            header_width = (
                len(str(headers[idx])) * 12
            )  # Use higher multiplier for headers

            # Check width needed for data in this column
            data_width = 0
            for row in rows:
                if idx < len(row):
                    width = len(str(row[idx])) * 10
                    if width > data_width:
                        data_width = width

            # Take the larger of header width and data width
            max_width = max(header_width, data_width)

            # Add extra padding to ensure headers don't overlap
            max_width += 20

            # Set minimum width (don't let columns get too narrow)
            max_width = max(max_width, 80)  # Increased minimum width
            # Set maximum width (don't let columns get too wide)
            max_width = min(max_width, 300)

            # Set column width and alignment
            tree.column(col_id, width=max_width, anchor=tk.CENTER, stretch=False)

        # Insert rows into the Treeview
        for row in rows:
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
        # Retrieve the display headers from each column's heading
        headers = [tree.heading(col)["text"] for col in tree["columns"]]
        csvwriter.writerow(headers)
        # Write the updated rows
        for item in tree.get_children():
            csvwriter.writerow(tree.item(item)["values"])


def add_row_below_selected(tree):
    selected = tree.selection()
    if selected:
        selected_index = tree.index(selected[0])
        # Assuming you want to insert an empty row or predefined data
        # Adjust the row data as per your requirements
        tree.insert("", selected_index + 1, values=("New", "Row"))


def delete_selected_row(tree):
    selected = tree.selection()
    if selected:
        tree.delete(selected[0])
