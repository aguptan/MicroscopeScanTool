import threading
from microscope_scan_tool.camera_preview import live_camera_preview
from microscope_scan_tool.user_input_gui import get_user_inputs
from microscope_scan_tool.scan_logic import snake_like_scan


# ========== DEFAULTS ==========
fields = ["y_top", "y_bottom", "x_left", "x_right"]
default_values = ["377710", "370232", "35672", "42606"]

def main():
    # Start live camera in background thread
    camera_thread = threading.Thread(target=live_camera_preview, daemon=True)
    camera_thread.start()

    # Show GUI for user input
    user_inputs = get_user_inputs(fields, default_values)

    # Wait for the camera thread to close
    camera_thread.join()

    # If valid inputs were returned, begin scan
    if user_inputs:
        snake_like_scan(
            float(user_inputs["y_top"]),
            float(user_inputs["y_bottom"]),
            float(user_inputs["x_left"]),
            float(user_inputs["x_right"]),
            objective_label=user_inputs["objective_label"],
            dry_run= False
        )

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        import traceback
        traceback.print_exc()
        input("\nPress Enter to close...")
