import tkinter as tk, datetime, csv, tkinter.ttk as ttk
from constants import FONT_SIZE, TIME_DELAY

# Global variables
window = None
time_label = None


# Function to update the time label with the current date and time
def show_date_time():
    current_time = datetime.datetime.now().strftime("%d %b %Y\n%I:%M:%S %p")
    time_label.config(text=current_time)
    time_label.after(TIME_DELAY, show_date_time)


# Function to create the root application window
def create_root_window():
    global window
    window = tk.Tk()
    window.title("Hopkins Plaster Studio - Inventory Management System")
    window.attributes("-fullscreen", True)


# Function to initialize and display UI components in the root window
def root_window_components():
    global time_label
    time_label = tk.Label(window, font=("Arial", FONT_SIZE), anchor="center")
    time_label.pack(expand=True)
    show_date_time()

    # Create and display the start button
    create_button("Start", open_menu_context, "center", 10, 25, 25, 100, 100)


# Function to open the menu context, replacing the root window's content
def open_menu_context():
    clear_window()

    # Create and display the back button and menu buttons
    create_button("⇦", back_to_root, "nw", 2, 5, 5, 10, 10)

    button_texts = {
        "Overall Stock": open_overall_stock,
        "Today's Cornice Log": open_todays_cornice_log,
        "Hours Worked": open_hours_worked,
        "Cornice Rates": open_cornice_rates,
    }

    for text in button_texts:
        create_button(text, button_texts[text], "center", 20, 20, 20, 5, 5)


# Function to open the overall stock
def open_overall_stock():
    pass


# Function to open today's cornice log
def open_todays_cornice_log():
    pass


# Function to open the hours worked
def open_hours_worked():
    pass


# Function to open the cornice rates
def open_cornice_rates():
    clear_window()

    # Create and display the back and save button
    button_frame = tk.Frame(window)
    button_frame.pack(side=tk.TOP, fill=tk.X, pady=10)

    create_button("⇦", open_menu_context, "nw", 2, 5, 5, 10, 10, button_frame, tk.LEFT)
    create_button(
        "💾",
        lambda: save_to_csv(tree, "assets/cornice_rate.csv"),
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
    with open("assets/cornice_rate.csv", newline="") as csvfile:
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


# Function to update the cell value in the Treeview
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


# Function to save the edited cell value back to the Treeview
def save_edit(tree, item, column_index, new_value):
    """Update the Treeview item with the new value and remove the entry widget."""
    values = list(tree.item(item, "values"))
    values[column_index] = new_value
    tree.item(item, values=values)
    for widget in tree.place_slaves():
        widget.destroy()  # Remove the entry widget


# Function to save the Treeview data to a CSV file
def save_to_csv(tree, filepath):
    with open(filepath, "w", newline="") as csvfile:
        csvwriter = csv.writer(csvfile)
        # Write the headers
        csvwriter.writerow(tree["columns"])
        # Write the updated rows
        for item in tree.get_children():
            csvwriter.writerow(tree.item(item)["values"])


# Function to create buttons
def create_button(
    text, command, anchor, width, padx, pady, x, y, frame=window, side=tk.TOP
):
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


# Function to clear the window and re-initialize the root window components
def back_to_root():
    clear_window()
    root_window_components()


# Function to remove all child widgets from the window
def clear_window():
    for widget in window.winfo_children():
        widget.destroy()


# Application setup
create_root_window()
root_window_components()
window.mainloop()
