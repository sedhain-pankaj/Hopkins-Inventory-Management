# This file contains the code to preview a CSV file.

import tkinter as tk, tkinter.ttk as ttk, csv
from utilities.cell_mods import (
    update_cell,
    save_to_csv,
    add_row_below_selected,
    delete_selected_row,
)
from utilities.utils import create_button, clear_window, adjust_column_widths


# Opens the cornice rates page with the back and save button
def preview_csv(window, FILEPATH, enable_edit):
    clear_window(window)

    # Import inside the function to avoid circular import
    # When going back to the previous window
    from pages.main_menu import open_menu_context

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

    # Configure alternating row colors
    style.map("Treeview", background=[("selected", "#1c75bc")])  # Keep selection color
    tree_frame = tk.Frame(window)
    tree_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    # Create the Treeview
    tree = ttk.Treeview(tree_frame, show="headings")

    # Configure the tag colors for alternating rows
    tree.tag_configure("odd", background="#f0f0f0")  # Light gray for odd rows
    tree.tag_configure("even", background="#ffffff")  # White for even rows

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

        # Set column headings
        for idx, col_id in enumerate(unique_ids):
            tree.heading(col_id, text=headers[idx])

        # Use the utility function to adjust all column widths
        adjust_column_widths(tree)

        # Insert rows into the Treeview with alternating colors
        for i, row in enumerate(rows):
            tag = "even" if i % 2 == 0 else "odd"
            tree.insert("", "end", values=row, tags=(tag,))

    # Bind the double-click event to the Treeview
    tree.bind("<Double-1>", lambda event: update_cell(event, tree))
