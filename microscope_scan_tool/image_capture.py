import os
from datetime import datetime
import uuid
import tifffile
import cv2
import numpy as np

from microscope_scan_tool.logger import log_error
from microscope_scan_tool import shared_state
from microscope_scan_tool.white_balance_utils import apply_white_balance_to_frame


def initialize_camera():
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    if not cap.isOpened():
        print("Camera not detected.")
        return None

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
    print("Camera resolution set to: 1920x1080")
    return cap

def capture_image(cap, save_dir, index, x, y):
    ret, frame = cap.read()
    if not ret:
        log_error(f"Failed to capture image at tile {index}.")
        return None

    # Apply white balance if enabled
    if (
        shared_state.white_balance_on and
        shared_state.white_balance_medians is not None and
        shared_state.white_balance_scale is not None
    ):
        frame = apply_white_balance_to_frame(frame)

    # Flip the frame before saving (same as preview)
    flipped_frame = cv2.cvtColor(cv2.flip(frame, -1), cv2.COLOR_BGR2RGB)

    # Construct metadata to embed in the TIFF
    metadata = {
        "TileX": x,
        "TileY": y,
        "TileZ": 0,
        "Channel": "Brightfield",
        "SizeX": flipped_frame.shape[1],
        "SizeY": flipped_frame.shape[0],
        "SizeZ": 1,
        "SizeT": 1,
        "SizeC": 1,
        "AcquisitionDate": datetime.now().isoformat(),
        "Objective": shared_state.objective_label,
        "GainFactor": shared_state.white_balance_scale,
        "ImageID": str(uuid.uuid4())
        # VoxelSizeX/Y intentionally omitted
    }

    # Convert metadata dict to string
    description = "\n".join([f"{k}={v}" for k, v in metadata.items()])

    # Create output path and filename
    filename = f"tile_{index:04d}.tif"
    path = os.path.join(save_dir, filename)

    # Save as TIFF with metadata
    tifffile.imwrite(
        path,
        flipped_frame,
        description=description,
        photometric='rgb' if flipped_frame.ndim == 3 else 'minisblack'
    )

    return filename
