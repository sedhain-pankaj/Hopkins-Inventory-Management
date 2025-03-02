import tkinter as tk


# Adjusts column widths in a Treeview based on content
def adjust_column_widths(tree):
    # Get all items in the tree
    all_items = tree.get_children()

    # For each column
    for idx, col_id in enumerate(tree["columns"]):
        header_text = tree.heading(col_id)["text"]

        # Calculate width for header (headers are bold and larger)
        header_width = len(str(header_text)) * 12

        # Check width needed for data in this column
        data_width = 0
        for item in all_items:
            values = tree.item(item, "values")
            if idx < len(values):
                width = len(str(values[idx])) * 10
                if width > data_width:
                    data_width = width

        # Take the larger of header width and data width
        max_width = max(header_width, data_width)

        # Add extra padding to ensure headers don't overlap
        max_width += 20

        # Set minimum width (don't let columns get too narrow)
        max_width = max(max_width, 80)
        # Set maximum width (don't let columns get too wide)
        max_width = min(max_width, 300)

        # Set column width and alignment
        tree.column(col_id, width=max_width, anchor=tk.CENTER, stretch=False)
