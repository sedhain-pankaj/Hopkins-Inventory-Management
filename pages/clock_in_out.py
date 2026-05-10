import queue
import threading
import tkinter as tk
from datetime import date
from tkinter import messagebox, ttk

from Utilities.constants import FONT_SIZE
from Utilities.fingerprint_service import (
    HelperNotFoundError,
    NoMatchError,
    format_action,
    identify_employee,
    recent_clock_events,
    record_clock_event,
)
from Utilities.utils import clear_window, create_button


def open_clock_in_out(window):
    clear_window(window)

    from pages.main_menu import open_menu_context

    result_queue = queue.Queue()
    scan_button = None

    top_frame = tk.Frame(window)
    top_frame.pack(side=tk.TOP, fill=tk.X, pady=10)
    create_button("⇦", lambda: open_menu_context(window), "nw", 2, 5, 5, 10, 10, top_frame, tk.LEFT)

    title = tk.Label(window, text="Clock In / Out", font=("Arial", max(FONT_SIZE // 3, 28), "bold"))
    title.pack(pady=(20, 5))

    status_text = tk.StringVar(value="Ready for fingerprint scan.")
    detail_text = tk.StringVar(value="Press scan, then place the enrolled finger on the WA28 reader.")

    status_label = tk.Label(window, textvariable=status_text, font=("Arial", max(FONT_SIZE // 5, 22)))
    status_label.pack(pady=(20, 5))
    detail_label = tk.Label(window, textvariable=detail_text, font=("Arial", max(FONT_SIZE // 8, 16)))
    detail_label.pack(pady=(0, 20))

    def start_scan():
        nonlocal scan_button
        if scan_button:
            scan_button.config(state=tk.DISABLED)
        status_text.set("Waiting for fingerprint...")
        detail_text.set("Keep the finger steady until the reader finishes.")

        def worker():
            def on_event(line):
                result_queue.put(("event", line))

            try:
                employee = identify_employee(on_event=on_event)
                event = record_clock_event(employee)
                result_queue.put(("success", employee, event))
            except HelperNotFoundError as exc:
                result_queue.put(("helper_missing", str(exc)))
            except NoMatchError as exc:
                result_queue.put(("no_match", str(exc)))
            except Exception as exc:
                result_queue.put(("error", str(exc)))

        threading.Thread(target=worker, daemon=True).start()
        window.after(100, poll_scan_result)

    def poll_scan_result():
        nonlocal scan_button
        try:
            while True:
                message = result_queue.get_nowait()
                kind = message[0]
                if kind == "event":
                    _update_scan_status(message[1], status_text, detail_text)
                elif kind == "success":
                    employee, event = message[1], message[2]
                    status_text.set(f"{format_action(event.action)}: {employee.name}")
                    detail_text.set(f"Employee {employee.employee_id} at {event.timestamp.replace('T', ' ')}")
                    if scan_button:
                        scan_button.config(state=tk.NORMAL)
                    refresh_recent_events()
                    return
                elif kind == "helper_missing":
                    status_text.set("Fingerprint helper is not built yet.")
                    detail_text.set("Build the helper before using the WA28 reader.")
                    messagebox.showerror("Fingerprint helper missing", message[1])
                    if scan_button:
                        scan_button.config(state=tk.NORMAL)
                    return
                elif kind == "no_match":
                    status_text.set("Fingerprint not recognized.")
                    detail_text.set(message[1])
                    if scan_button:
                        scan_button.config(state=tk.NORMAL)
                    return
                elif kind == "error":
                    status_text.set("Fingerprint scan failed.")
                    detail_text.set(message[1])
                    if scan_button:
                        scan_button.config(state=tk.NORMAL)
                    return
        except queue.Empty:
            pass

        window.after(100, poll_scan_result)

    scan_button = tk.Button(
        window,
        text="Scan Fingerprint",
        font=("Arial", max(FONT_SIZE // 5, 22), "bold"),
        command=start_scan,
        padx=30,
        pady=15,
    )
    scan_button.pack(pady=(10, 30))

    table_frame = tk.Frame(window)
    table_frame.pack(fill=tk.BOTH, expand=True, padx=60, pady=(0, 40))

    tk.Label(table_frame, text="Today's Clock Events", font=("Arial", 18, "bold")).pack(anchor="w")

    tree = ttk.Treeview(table_frame, columns=("time", "employee", "action"), show="headings", height=10)
    tree.heading("time", text="Time")
    tree.heading("employee", text="Employee")
    tree.heading("action", text="Action")
    tree.column("time", width=180, anchor="w")
    tree.column("employee", width=360, anchor="w")
    tree.column("action", width=160, anchor="w")
    tree.pack(fill=tk.BOTH, expand=True, pady=(8, 0))

    def refresh_recent_events():
        for item in tree.get_children():
            tree.delete(item)
        for event in recent_clock_events(on_date=date.today()):
            time_text = event.timestamp.replace("T", " ")[11:19] if event.timestamp else ""
            employee_text = f"{event.employee_name} ({event.employee_id})"
            tree.insert("", "end", values=(time_text, employee_text, format_action(event.action)))

    refresh_recent_events()
    window.after(500, start_scan)


def _update_scan_status(line, status_text, detail_text):
    if line.startswith("DEVICE|"):
        parts = line.split("|")
        if len(parts) >= 4:
            status_text.set("Fingerprint reader ready.")
            detail_text.set(f"{parts[1]} using {parts[2]} driver.")
    elif line.startswith("READY|identify"):
        status_text.set("Scan now.")
        detail_text.set("Place the enrolled finger on the reader.")
    elif line.startswith("PROGRESS|"):
        parts = line.split("|")
        if len(parts) >= 3:
            status_text.set(f"Enrollment progress {parts[1]} of {parts[2]}")
    elif line.startswith("RETRY|"):
        detail_text.set(line.split("|", 1)[1])
