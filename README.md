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
├── main.py                          # Entry point: launches live preview, GUI, and scanning logic
├── microscope_scan_tool/            # Core package with all supporting functions
│   ├── camera_preview.py             # Handles live camera feed display and white patch overlay
│   ├── user_input_gui.py             # GUI for entering coordinates and selecting objectives
│   ├── scan_logic.py                 # Controls snake-pattern scanning and image capture sequence
│   ├── white_balance_utils.py        # Performs frame white-balance correction and median 
│   ├── shared_state.py               # Stores global camera settings, patch info, and scan state
│   ├── stage_controller.py           # Controls XY stage movement and enforces position 
│   ├── logger.py                     # Handles scan folder creation and error logging
│   └── metadata_writer.py            # Writes FIJI-compatible tile metadata (positions, overlap, 
├── archive/                          # Deprecated/older versions of modules
│   ├── camera_preview_depreciated.py
│   ├── scan_logic_depreciated.py
│   ├── user_input_gui_depreciated.py
│   └── user_input_gui_depreciated2.py
├── environment.yml                   # Conda environment for minimal project dependencies
├── environment_full.yml              # Conda environment with full optional dependencies
└── README.md                         # Project description, setup instructions, and usage guide
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
Developed by Amal Guptan with the help of LLM for the Shoykhet Lab. Contributions and suggestions welcome.
