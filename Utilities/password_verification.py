import tkinter as tk
from tkinter import messagebox
import hashlib
from utilities.constants import PASSWORD_HASH


def verify_password_dialog(parent, callback_on_success):
    """
    Creates a password verification dialog.

    Args:
        parent: The parent window for the dialog
        callback_on_success: Function to call if password verification succeeds
    """

    # Create a password dialog
    password_dialog = tk.Toplevel(parent)
    password_dialog.title("Password Required")
    password_dialog.geometry("300x150")
    password_dialog.resizable(False, False)

    # Center the dialog
    password_dialog.geometry(
        "+{}+{}".format(
            int(password_dialog.winfo_screenwidth() / 2 - 150),
            int(password_dialog.winfo_screenheight() / 2 - 75),
        )
    )

    # Add password label and entry
    tk.Label(
        password_dialog, text="Please enter password to save:", font=("Arial", 12)
    ).pack(pady=10)
    password_entry = tk.Entry(password_dialog, show="*", width=20, font=("Arial", 12))
    password_entry.pack(pady=10)
    password_entry.focus()

    def verify():
        entered_password = password_entry.get()
        # Hash the entered password
        hashed_input = hashlib.sha256(entered_password.encode()).hexdigest()

        # Compare with stored hash
        if hashed_input == PASSWORD_HASH:
            password_dialog.destroy()
            # Password correct, call the success callback
            callback_on_success()
        else:
            messagebox.showerror("Error", "Incorrect password")

    # Add buttons
    button_frame = tk.Frame(password_dialog)
    button_frame.pack(fill=tk.X, pady=10)

    tk.Button(button_frame, text="Cancel", command=password_dialog.destroy).pack(
        side=tk.LEFT, padx=20
    )
    tk.Button(button_frame, text="Submit", command=verify).pack(side=tk.RIGHT, padx=20)

    # Bind Enter key to verify password
    password_entry.bind("<Return>", lambda event: verify())

    # Make dialog modal
    password_dialog.transient(parent)
    password_dialog.grab_set()
    parent.wait_window(password_dialog)
