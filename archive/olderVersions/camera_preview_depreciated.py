import cv2
import time
from SupportingFunctions import shared_state
from SupportingFunctions.white_balance_utils import apply_white_balance_to_frame  # NEW IMPORT


def live_camera_preview():
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    if not cap.isOpened():
        print("❌ Camera not detected.")
        return

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 960)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 540)

    cv2.namedWindow("Live Camera Preview", cv2.WINDOW_NORMAL)
    cv2.setWindowProperty("Live Camera Preview", cv2.WND_PROP_TOPMOST, 1)

    while shared_state.camera_running:
        ret, frame = cap.read()
        if not ret:
            break

        # ✅ Conditionally apply white balance correction for preview only
        if (
            shared_state.white_balance_on and
            shared_state.white_balance_medians is not None and
            shared_state.white_balance_scale is not None
        ):
            corrected = apply_white_balance_to_frame(frame)
            display_frame = corrected
        else:
            display_frame = frame

        cv2.imshow("Live Camera Preview", cv2.flip(display_frame, -1))

        if cv2.getWindowProperty("Live Camera Preview", cv2.WND_PROP_VISIBLE) < 1:
            shared_state.camera_running = False
            break
        if cv2.waitKey(1) & 0xFF == ord('q'):
            shared_state.camera_running = False
            break

    cap.release()
    cv2.destroyAllWindows()
    print("✅ Live preview closed.")

