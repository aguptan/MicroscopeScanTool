import tkinter as tk
from tkinter import messagebox
import time
import cv2
from pycromanager import Core

from microscope_scan_tool import shared_state
from microscope_scan_tool.image_capture import initialize_camera

def get_user_inputs(fields, defaults):
    """
    Opens a Tkinter GUI to collect user-defined coordinates and objective.
    Returns a dictionary of float values + selected objective label.
    """
    user_inputs = {}

    OBJECTIVE_MAP = {
        "4x": "Position-1",
        "20x": "Position-2"
    }

    # === GUI Initialization ===
    window = tk.Tk()
    window.title("Enter Stage Coordinates")

    # === Initialize Micro-Manager Core ===
    core = Core()

    def on_objective_change(*args):
        selected = selected_objective.get()
        mm_position = OBJECTIVE_MAP.get(selected)

        if mm_position:
            try:
                core.set_property("Objective", "Label", mm_position)
                core.wait_for_device("Objective")
                print(f" Objective turret moved to {selected} ({mm_position})")
            except Exception as e:
                print(f" Failed to switch objective: {e}")

    def submit():
        nonlocal user_inputs
        try:
            for idx, entry in enumerate(entries):
                value = entry.get().strip()
                if value == "" or not value.replace(".", "", 1).isdigit():
                    raise ValueError(f"Invalid entry for {fields[idx]}: '{value}'. Please enter a number.")
                user_inputs[fields[idx]] = float(value)

            user_inputs["objective_label"] = selected_objective.get()

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

    # === Dynamic WB Slider & Button ===
    wb_gain_scale = None
    wb_select_button = None

    def handle_white_balance_patch():
        nonlocal wb_gain_scale, wb_select_button

        if wb_gain_scale is not None and wb_select_button is not None:
            return  # Already added

        row_index = len(fields) + 5

        # Gain Label and Scale
        tk.Label(window, text="WB Gain Factor (0.7–1.5):").grid(
            row=row_index, column=0, padx=5, pady=5, sticky="e"
        )
        wb_gain_scale = tk.Scale(window, from_=0.7, to=1.5, resolution=0.01,
                                 orient=tk.HORIZONTAL, length=150)
        wb_gain_scale.set(1.2)
        wb_gain_scale.grid(row=row_index, column=1, columnspan=2, padx=5, pady=5, sticky="w")

        # Select Button (to enable drawing)
        def confirm_gain_and_start_patch():
            shared_state.white_balance_scale = wb_gain_scale.get()

            # Clear old medians and disable WB until a new patch is drawn
            shared_state.white_balance_on = False
            shared_state.white_balance_medians = None
            shared_state.box_start = None
            shared_state.box_end = None

            shared_state.enable_patch_selection = True
            print(f" Patch selection mode enabled with scale factor: {shared_state.white_balance_scale}")

        wb_select_button = tk.Button(window, text="Select", command=confirm_gain_and_start_patch)
        wb_select_button.grid(row=row_index + 1, column=1, columnspan=2, pady=5, sticky="w")

    # === GUI Layout ===
    window.protocol("WM_DELETE_WINDOW", on_close)
    tk.Label(window, text="Scan Area Input", font=("Arial", 16, "bold")).grid(row=0, column=0, columnspan=3, pady=10)
    tk.Label(window, text="(Enter values in microns from Micro-Manager)", font=("Arial", 10, "italic"), fg="red").grid(row=1, column=0, columnspan=3, pady=5)

    # Objective Dropdown
    tk.Label(window, text="Objective:").grid(row=2, column=0, padx=5, pady=5, sticky="e")
    selected_objective = tk.StringVar(window)
    selected_objective.set("4x")
    selected_objective.trace_add("write", on_objective_change)  # Bind live switching
    dropdown = tk.OptionMenu(window, selected_objective, *OBJECTIVE_MAP.keys())
    dropdown.grid(row=2, column=1, columnspan=2, padx=5, pady=5, sticky="w")

    # Coordinate Entry Fields
    entries = []
    for idx, field in enumerate(fields):
        row_num = idx + 3
        tk.Label(window, text=f"{field}:").grid(row=row_num, column=0, padx=5, pady=5, sticky="e")
        entry = tk.Entry(window, width=10)
        entry.grid(row=row_num, column=1, padx=5, pady=5)
        entry.insert(0, defaults[idx])
        entries.append(entry)
        tk.Label(window, text="(µm)").grid(row=row_num, column=2, padx=5, pady=5, sticky="w")

    # Submit and WB Patch Select Buttons
    tk.Button(window, text='Submit', command=submit).grid(row=len(fields) + 3, column=0, columnspan=3, pady=10)
    tk.Button(window, text='White Balance Patch Select', command=handle_white_balance_patch).grid(
        row=len(fields) + 4, column=0, columnspan=3, pady=5
    )

    window.mainloop()
    return user_inputs
