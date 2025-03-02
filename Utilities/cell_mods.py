import tkinter as tk, csv
from tkinter import messagebox
from Utilities.utils import adjust_column_widths
from Utilities.password_verification import verify_password_dialog


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


# Add a new row below the selected row
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


# Delete the selected row
def delete_selected_row(tree):
    selected = tree.selection()
    if selected:
        tree.delete(selected[0])
        # After deleting the row, adjust column widths
        adjust_column_widths(tree)
    else:
        messagebox.showerror("Error", "No row selected for deletion")
