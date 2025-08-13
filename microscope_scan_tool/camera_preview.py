import cv2
import numpy as np
from microscope_scan_tool import shared_state
from microscope_scan_tool.white_balance_utils import apply_white_balance_to_frame


def compute_patch_medians(frame, patch_coords):
    h_start, w_start, h_width, w_width = patch_coords
    patch = frame[h_start:h_start + h_width, w_start:w_start + w_width].astype(np.float32)
    if patch.size == 0:
        return None
    return np.median(patch, axis=(0, 1))


def live_camera_preview():
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    if not cap.isOpened():
        print("Camera not detected.")
        return

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 960)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 540)

    cv2.namedWindow("Live Camera Preview", cv2.WINDOW_NORMAL)
    cv2.setWindowProperty("Live Camera Preview", cv2.WND_PROP_TOPMOST, 1)

    def mouse_event(event, x, y, flags, param):
        if not shared_state.enable_patch_selection:
            return

        if shared_state.last_frame_snapshot is None:
            return

        # Unflip the coordinates (flip both horizontally and vertically)
        frame_height, frame_width = shared_state.last_frame_snapshot.shape[:2]
        x = frame_width - x
        y = frame_height - y

        if event == cv2.EVENT_LBUTTONDOWN:
            shared_state.selecting_box = True
            shared_state.box_start = (x, y)
            shared_state.box_end = None
            shared_state.white_balance_on = False  # Disable previous WB during new draw

        elif event == cv2.EVENT_MOUSEMOVE and shared_state.selecting_box:
            shared_state.box_end = (x, y)

        elif event == cv2.EVENT_LBUTTONUP and shared_state.selecting_box:
            shared_state.selecting_box = False
            shared_state.box_end = (x, y)

            # Compute white balance from the box
            start, end = shared_state.box_start, shared_state.box_end
            x1, y1 = min(start[0], end[0]), min(start[1], end[1])
            x2, y2 = max(start[0], end[0]), max(start[1], end[1])
            patch_coords = (y1, x1, y2 - y1, x2 - x1)

            frame = shared_state.last_frame_snapshot
            medians = compute_patch_medians(frame, patch_coords)

            if medians is not None:
                shared_state.white_balance_medians = medians
                shared_state.white_balance_on = True
                print(" White balance enabled with medians:", medians)
            else:
                print(" Empty patch selected.")
                shared_state.white_balance_on = False

            # Reset patch selection mode
            shared_state.enable_patch_selection = False
            shared_state.box_start = None
            shared_state.box_end = None

    cv2.setMouseCallback("Live Camera Preview", mouse_event)

    while shared_state.camera_running:
        ret, frame = cap.read()
        if not ret or frame is None:
            break

        shared_state.last_frame_snapshot = frame.copy()

        # Apply white balance if and only if it's active and valid
        if (
            shared_state.white_balance_on and
            shared_state.white_balance_medians is not None and
            shared_state.white_balance_scale is not None
        ):
            corrected = apply_white_balance_to_frame(frame)
            display_frame = corrected
        else:
            display_frame = frame

        # If drawing a box, show it on top of current frame
        if shared_state.selecting_box and shared_state.box_start and shared_state.box_end:
            box_frame = display_frame.copy()
            cv2.rectangle(box_frame, shared_state.box_start, shared_state.box_end, (0, 0, 255), 2)
            cv2.imshow("Live Camera Preview", cv2.flip(box_frame, -1))
        else:
            cv2.imshow("Live Camera Preview", cv2.flip(display_frame, -1))

        if cv2.getWindowProperty("Live Camera Preview", cv2.WND_PROP_VISIBLE) < 1:
            shared_state.camera_running = False
            break
        if cv2.waitKey(1) & 0xFF == ord('q'):
            shared_state.camera_running = False
            break

    cap.release()
    cv2.destroyAllWindows()