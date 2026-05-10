import tkinter as tk
from datetime import date
from tkinter import ttk

from Utilities.fingerprint_service import format_seconds, summarize_hours
from Utilities.utils import clear_window, create_button


def open_hours_worked(window):
    clear_window(window)

    from pages.main_menu import open_menu_context

    button_frame = tk.Frame(window)
    button_frame.pack(side=tk.TOP, fill=tk.X, pady=10)
    create_button("⇦", lambda: open_menu_context(window), "nw", 2, 5, 5, 10, 10, button_frame, tk.LEFT)

    tk.Label(window, text="Hours Worked Today", font=("Arial", 32, "bold")).pack(pady=(20, 10))

    tree_frame = tk.Frame(window)
    tree_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=50, pady=20)

    tree = ttk.Treeview(
        tree_frame,
        columns=("employee_id", "name", "hours", "status"),
        show="headings",
    )
    tree.heading("employee_id", text="Employee ID")
    tree.heading("name", text="Name")
    tree.heading("hours", text="Hours")
    tree.heading("status", text="Status")
    tree.column("employee_id", width=180)
    tree.column("name", width=320)
    tree.column("hours", width=120)
    tree.column("status", width=160)

    scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)
    tree.grid(row=0, column=0, sticky="nsew")
    scrollbar.grid(row=0, column=1, sticky="ns")
    tree_frame.grid_rowconfigure(0, weight=1)
    tree_frame.grid_columnconfigure(0, weight=1)

    for row in summarize_hours(on_date=date.today()):
        tree.insert(
            "",
            "end",
            values=(row["employee_id"], row["name"], format_seconds(row["seconds"]), row["status"]),
        )
