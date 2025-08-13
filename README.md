# Microscope Scan Tool

This project provides an interactive, GUI-based microscope scanning tool that works with Micro-Manager to capture tiled images using a motorized XY stage and live camera feed. It supports objective selection, white balance calibration, and automated metadata generation compatible with FIJI.

## Features

- Objective turret control and scan setup via GUI
- Snake-pattern tiling with user-defined scan bounds
- Live camera preview with flipped display
- White patch selection for white balance correction
- Adjustable scan step sizes per objective
- Automated folder creation and scan logging
- FIJI-compatible `TileConfiguration.txt` export

## Requirements

- Python 3.8+
- Micro-Manager (with `pycromanager` server running)
- Windows OS (default save directory is Windows-specific)
- Python packages:
  - `pycromanager`
  - `opencv-python`
  - `numpy`
  - `tkinter` (usually preinstalled)

Install dependencies:

```bash
pip install pycromanager opencv-python numpy
```

## File Structure

```
.
├── main.py                    # Entry point: preview + GUI + scan logic
├── camera_preview.py          # Live camera feed and white patch drawing
├── user_input_gui.py          # Coordinate input + objective dropdown
├── scan_logic.py              # Snake scan control + image capture
├── white_balance_utils.py     # Frame correction + median computation
├── shared_state.py            # Global camera state and patch info
├── stage_controller.py        # XY movement with position tolerance
├── logger.py                  # Scan folder and error logging
├── metadata_writer.py         # FIJI tile metadata writer
```
## Usage
1. Run `main.py`
2. A live preview window will open and a GUI will prompt you to enter:
   - Top/Bottom Y coordinates
   - Left/Right X coordinates
   - Objective selection (4x or 20x)
3. Optionally click "White Balance Patch Select" to draw a white patch on the preview.
4. Submit to begin scanning.
Captured tiles will be stored under:
```
C:\Users\admin\Desktop\TestCamera\Scan_YYYY-MM-DD_HH-MM-SS_Objective
```
Includes:
- All tile images
- A `TileConfiguration_*.txt` metadata file for FIJI
- A timestamped scan log

## Dry Run Mode
To test scan logic without hardware movement, set `dry_run=True` in the `snake_like_scan()` function in `main.py`.

## Notes
- Default scan bounds and step sizes are hardcoded; adjust `STEP_SIZES_BY_OBJECTIVE` and bounds in `scan_logic.py` as needed.
- This tool assumes the camera is at index 0 and that the microscope's stage is controllable via Micro-Manager.
- Supports only 4x and 20x objective labels by default.

## Author
Developed by Amal Guptan for the Shoykhet Lab. Contributions and suggestions welcome.
