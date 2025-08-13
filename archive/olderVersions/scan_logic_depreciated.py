import time
import os
from datetime import datetime
from pycromanager import Core
import cv2

from SupportingFunctions.image_capture import initialize_camera, capture_image
from SupportingFunctions.stage_controller import move_stage
from SupportingFunctions.logger import create_scan_folder, log_error
from SupportingFunctions.metadata_writer import save_fiji_metadata
from SupportingFunctions import shared_state

# Constants
MM_PORT = 4827
HARD_BOUNDARY_CORNERS = [(98097, 391023), (25848, 386490), (26968, 359167), (98097, 365572)]
HARD_X_MIN, HARD_X_MAX = min(p[0] for p in HARD_BOUNDARY_CORNERS), max(p[0] for p in HARD_BOUNDARY_CORNERS)
HARD_Y_MIN, HARD_Y_MAX = min(p[1] for p in HARD_BOUNDARY_CORNERS), max(p[1] for p in HARD_BOUNDARY_CORNERS)

# Step size map for objectives
STEP_SIZES_BY_OBJECTIVE = {
    "4x": (1800, 1000),
    "20x": (200, 200),
}

def calc_positions(y_top, y_bottom, x_left, x_right, x_step, y_step):
    if (
        x_left < HARD_X_MIN or x_right > HARD_X_MAX or
        y_bottom < HARD_Y_MIN or y_top > HARD_Y_MAX
    ):
        print("❌ ERROR: User-defined scan area is outside the allowed boundaries.")
        print(f"Allowed X: {HARD_X_MIN}–{HARD_X_MAX}, Got: {x_left}–{x_right}")
        print(f"Allowed Y: {HARD_Y_MIN}–{HARD_Y_MAX}, Got: {y_bottom}–{y_top}")
        return None

    positions = []
    y = int(y_top)
    move_right = True

    while y >= int(y_bottom):
        x_positions = (
            list(range(int(x_left), int(x_right) + x_step, x_step))
            if move_right else
            list(range(int(x_right), int(x_left) - x_step, -x_step))
        )
        positions.extend([(x, y) for x in x_positions])
        y -= y_step
        move_right = not move_right

    return positions

def snake_like_scan(y_top, y_bottom, x_left, x_right, objective_label="4x", dry_run=False):
    from SupportingFunctions import shared_state
    shared_state.objective_label = objective_label
    x_step, y_step = STEP_SIZES_BY_OBJECTIVE.get(objective_label, (1800, 1000))
    print(f"🔧 Using step size for {objective_label}: X_STEP={x_step}, Y_STEP={y_step}")

    positions = calc_positions(y_top, y_bottom, x_left, x_right, x_step, y_step)
    if positions is None:
        log_error("❌ Scan aborted: user-defined scan area was outside the allowed boundaries.")
        return

    core = Core(port=MM_PORT)

    try:
        core.set_property("OlympusHub", "Control", "Manual + Computer")
        print("OlympusHub Control set to 'Manual + Computer'.")
    except Exception as e:
        print(f"⚠️ Could not set OlympusHub Control: {e}")
        return

    OBJECTIVE_TO_POSITION = {
        "4x": "Position-1",
        "20x": "Position-2"
    }

    try:
        mm_label = OBJECTIVE_TO_POSITION[objective_label]
        core.set_property("Objective", "Label", mm_label)
        core.wait_for_device("Objective")
        print(f"✅ Objective set to {objective_label} ({mm_label})")
    except Exception as e:
        print(f"❌ Failed to switch objective: {e}")
        return

    if dry_run:
        print("🧪 DRY RUN: Skipping stage movement and image capture.")
        print(f"Would scan {len(positions)} tiles from ({x_left}, {y_top}) to ({x_right}, {y_bottom})")
        for i, (x, y) in enumerate(positions, start=1):
            print(f"Tile {i:03d}: X={x}, Y={y}")
        return

    cap = initialize_camera()
    if cap is None:
        return

    scan_dir = create_scan_folder(objective_label)
    fiji_positions = []

    for i, (x, y) in enumerate(positions, start=1):
        move_stage(core, x, y)

        if i == 1:
            time.sleep(2)

        filename = capture_image(cap, scan_dir, i, x, y)
        if filename:
            fiji_positions.append((filename, x, y))

    save_fiji_metadata(scan_dir, fiji_positions)
    log_error(f"✅ Scan complete. Images and logs saved in: {scan_dir}")
    cap.release()
    print("✅ Scan safely stopped.")