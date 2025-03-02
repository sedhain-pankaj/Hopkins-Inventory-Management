import tkinter.messagebox as message_box

# History stack to store previous states
_history_stack = []
_max_history_size = 20  # Limit stack size to prevent memory issues


def save_table_state(tree):
    """Save the current state of the table to history stack"""
    # Create a snapshot of the current table state
    current_state = {
        "headers": [tree.heading(col)["text"] for col in tree["columns"]],
        "rows": [],
    }

    # Save all rows data
    for item in tree.get_children():
        current_state["rows"].append(
            {"values": tree.item(item)["values"], "tags": tree.item(item)["tags"]}
        )

    # Add to history stack (only if different from last state)
    if len(_history_stack) == 0 or current_state != _history_stack[-1]:
        _history_stack.append(current_state)
        # Keep history stack size manageable
        if len(_history_stack) > _max_history_size:
            _history_stack.pop(0)


def undo_last_action(tree):
    """Restore the previous state from history stack"""
    if not _history_stack or len(_history_stack) < 2:
        # Need at least 2 states: current and previous
        message_box.showinfo("Error", "No history available to undo.")
        return False

    # Remove current state
    _history_stack.pop()

    # Get previous state
    previous_state = _history_stack[-1]

    # Clear current table
    for item in tree.get_children():
        tree.delete(item)

    # Restore rows from previous state
    for i, row_data in enumerate(previous_state["rows"]):
        tree.insert("", "end", values=row_data["values"], tags=row_data["tags"])

    return True


def clear_history():
    """Clear the history stack (e.g., when loading a new file)"""
    global _history_stack
    _history_stack = []
