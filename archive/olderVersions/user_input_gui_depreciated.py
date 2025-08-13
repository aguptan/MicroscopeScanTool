import tkinter as tk
from tkinter import messagebox
import time
import cv2

from SupportingFunctions import shared_state

def get_user_inputs(fields, defaults):
    """
    Opens a Tkinter GUI to collect user-defined coordinates and objective.
    Returns a dictionary of float values + selected objective label.
    """
    user_inputs = {}

    # ✅ Only allow 10x and 20x
    OBJECTIVE_MAP = {
        "4x": "Position-1",
        "20x": "Position-2"
    }

    def submit():
        nonlocal user_inputs
        try:
            for idx, entry in enumerate(entries):
                value = entry.get().strip()
                if value == "" or not value.replace(".", "", 1).isdigit():
                    raise ValueError(f"Invalid entry for {fields[idx]}: '{value}'. Please enter a number.")

                user_inputs[fields[idx]] = float(value)

            # ✅ Store internal turret label
            user_inputs["objective_label"] = selected_objective.get()  # ⬅️ just "4x" or "20x"

            shared_state.camera_running = False
            time.sleep(0.5)
            cv2.destroyAllWindows()
            window.destroy()

        except ValueError as e:
            messagebox.showerror("Input Error", f"{e}\n\nEnter numeric values only.")

    def on_close():
        shared_state.camera_running = False
        time.sleep(0.5)
        cv2.destroyAllWindows()
        window.destroy()

    window = tk.Tk()
    window.title("Enter Stage Coordinates")
    window.protocol("WM_DELETE_WINDOW", on_close)

    tk.Label(window, text="Scan Area Input", font=("Arial", 16, "bold")).grid(row=0, column=0, columnspan=3, pady=10)
    tk.Label(window, text="(Enter values in microns from Micro-Manager)", font=("Arial", 10, "italic"), fg="red").grid(row=1, column=0, columnspan=3, pady=5)

    # ✅ Objective dropdown (only 4x & 20x)
    tk.Label(window, text="Objective:").grid(row=2, column=0, padx=5, pady=5, sticky="e")
    selected_objective = tk.StringVar(window)
    selected_objective.set("4x")  # Default
    dropdown = tk.OptionMenu(window, selected_objective, *OBJECTIVE_MAP.keys())
    dropdown.grid(row=2, column=1, columnspan=2, padx=5, pady=5, sticky="w")

    # Coordinate fields (start from row 3)
    entries = []
    for idx, field in enumerate(fields):
        row_num = idx + 3
        tk.Label(window, text=f"{field}:").grid(row=row_num, column=0, padx=5, pady=5, sticky="e")
        entry = tk.Entry(window, width=10)
        entry.grid(row=row_num, column=1, padx=5, pady=5)
        entry.insert(0, defaults[idx])
        entries.append(entry)
        tk.Label(window, text="(µm)").grid(row=row_num, column=2, padx=5, pady=5, sticky="w")

    tk.Button(window, text='Submit', command=submit).grid(row=len(fields) + 3, column=0, columnspan=3, pady=10)

    window.mainloop()
    return user_inputs

