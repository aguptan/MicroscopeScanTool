import time
from microscope_scan_tool.logger import log_error

POSITION_TOLERANCE = 50  # microns
MOVE_TIMEOUT = 5.0       # seconds

def move_stage(core, x, y, tolerance=POSITION_TOLERANCE, timeout=MOVE_TIMEOUT):
    """
    Moves the stage to (x, y) and waits until the stage settles or timeout is hit.
    """
    core.set_xy_position(x, y)

    move_attempts = 0
    max_attempts = int(timeout / 0.1)

    while move_attempts < max_attempts:
        current_x, current_y = core.get_x_position(), core.get_y_position()
        dx = abs(current_x - x)
        dy = abs(current_y - y)

        if dx < tolerance and dy < tolerance:
            break

        time.sleep(0.1)
        move_attempts += 1

    if move_attempts >= max_attempts:
        log_error(f" Stage move timeout at ({x}, {y}) — proceeding anyway.")
    else:
        log_error(f" Stage reached ({x}, {y}) in {move_attempts * 0.1:.1f} sec.")
