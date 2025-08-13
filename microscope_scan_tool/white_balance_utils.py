import cv2
import numpy as np
from microscope_scan_tool import shared_state


def apply_white_balance_to_frame(frame):
    """
    Applies white balance correction to a given frame using stored medians and scale factor.
    Used for preview only.
    """
    medians = shared_state.white_balance_medians
    scale = shared_state.white_balance_scale

    if (
        medians is None or
        scale is None or
        np.any(medians == 0) or
        scale <= 0
    ):
        return frame

    target = medians * scale
    frame_float = frame.astype(np.float32)
    balanced = frame_float / target
    balanced = np.clip(balanced, 0, 1)
    return (balanced * 255).astype(np.uint8)


def compute_patch_medians(frame, patch_coords):
    """
    Given a patch region (y, x, height, width), compute the per-channel medians.
    """
    h_start, w_start, h_width, w_width = patch_coords
    patch = frame[h_start:h_start+h_width, w_start:w_start+w_width].astype(np.float32)

    if patch.size == 0:
        return None
    return np.median(patch, axis=(0, 1))


def select_white_patch_and_compute_medians(frame, scale_factor=1.0):
    """
    Displays a scaled frame, lets user draw a white patch,
    computes medians, updates shared_state, and shows corrected preview.
    """
    clone = frame.copy()
    preview_scale_w, preview_scale_h = 50, 50
    h, w = clone.shape[:2]
    resized = cv2.resize(clone, (int(w * preview_scale_w / 100), int(h * preview_scale_h / 100)))

    start_pt, end_pt = [None], [None]
    drawing = [False]

    def rescale_coords(p1, p2):
        x1, y1 = int(p1[0] / preview_scale_w * 100), int(p1[1] / preview_scale_h * 100)
        x2, y2 = int(p2[0] / preview_scale_w * 100), int(p2[1] / preview_scale_h * 100)
        return min(y1, y2), min(x1, x2), abs(y2 - y1), abs(x2 - x1)

    def click_event(event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            start_pt[0] = (x, y)
            drawing[0] = True
        elif event == cv2.EVENT_MOUSEMOVE and drawing[0]:
            temp = resized.copy()
            cv2.rectangle(temp, start_pt[0], (x, y), (0, 0, 255), 2)
            cv2.imshow('Select White Patch', temp)
        elif event == cv2.EVENT_LBUTTONUP:
            end_pt[0] = (x, y)
            drawing[0] = False

            # Show red box briefly
            preview_with_box = resized.copy()
            cv2.rectangle(preview_with_box, start_pt[0], end_pt[0], (0, 0, 255), 2)
            cv2.imshow('Select White Patch', preview_with_box)
            cv2.waitKey(500)

            patch_coords = rescale_coords(start_pt[0], end_pt[0])
            medians = compute_patch_medians(clone, patch_coords)

            if medians is not None:
                shared_state.white_balance_medians = medians
                shared_state.white_balance_scale = scale_factor
                shared_state.white_balance_on = True

                corrected = apply_white_balance_to_frame(clone)
                corrected_resized = cv2.resize(corrected, (resized.shape[1], resized.shape[0]))
                cv2.imshow('Select White Patch', corrected_resized)
            else:
                print("Empty patch selected.\n Failed to compute medians.")
                shared_state.white_balance_on = False

    cv2.namedWindow('Select White Patch', cv2.WINDOW_NORMAL)
    cv2.imshow('Select White Patch', resized)
    cv2.setMouseCallback('Select White Patch', click_event)
    cv2.waitKey(0)
    cv2.destroyWindow('Select White Patch')
