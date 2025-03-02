# This file contains the code to preview a CSV file.

import tkinter as tk
import tkinter.ttk as ttk
from tkinter import messagebox
import csv
from Utilities.utils import create_button, clear_window, adjust_column_widths
from Utilities.password_verification import verify_password_dialog


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
    def save_data():
        # This function will be called if password verification succeeds
        with open(filepath, "w", newline="", encoding="utf-8") as csvfile:
            csvwriter = csv.writer(csvfile)
            headers = [tree.heading(col)["text"] for col in tree["columns"]]
            csvwriter.writerow(headers)
            for item in tree.get_children():
                csvwriter.writerow(tree.item(item)["values"])
        messagebox.showinfo("Success", "Data saved successfully!")

    # Use the utility function to verify password before saving
    verify_password_dialog(tree.winfo_toplevel(), save_data)


def add_row_below_selected(tree):
    selected = tree.selection()

    # Get all column headers
    headers = [tree.heading(col)["text"] for col in tree["columns"]]

    # Create a new row with "New" prepended to each header
    new_row = [f"New {header}" for header in headers]

    if selected:
        selected_index = tree.index(selected[0])

        # Insert the new row below the selected one
        tree.insert(
            "",
            selected_index + 1,
            values=new_row,
            tags=("even" if (selected_index + 1) % 2 == 0 else "odd"),
        )
    else:
        # If no row is selected, add to the end
        count = len(tree.get_children())
        tree.insert(
            "", "end", values=new_row, tags=("even" if count % 2 == 0 else "odd")
        )

    # After adding the row, adjust column widths
    adjust_column_widths(tree)


def delete_selected_row(tree):
    selected = tree.selection()
    if selected:
        tree.delete(selected[0])
        # After deleting the row, adjust column widths
        adjust_column_widths(tree)
    else:
        messagebox.showerror("Error", "No row selected for deletion")
