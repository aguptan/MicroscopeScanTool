import os
from datetime import datetime

BASE_SAVE_DIR = os.path.join(os.getcwd(), "ScanOutputs")
LOG_FILE = None  

def create_scan_folder(objective_name=None):
    timestamp = datetime.now().strftime("Scan_%Y-%m-%d_%H-%M-%S")
    
    if objective_name:
        folder_name = f"{timestamp}_{objective_name}"
    else:
        folder_name = timestamp

    folder_path = os.path.join(BASE_SAVE_DIR, folder_name)
    os.makedirs(folder_path, exist_ok=True)

    global LOG_FILE
    LOG_FILE = os.path.join(folder_path, f"{timestamp}_log.txt")
    return folder_path


def log_error(message):
    """
    Logs messages to both the terminal and the scan log file.
    """
    global LOG_FILE
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_line = f"[{timestamp}] {message}"

    # Save to file
    if LOG_FILE:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(log_line + "\n")

    print(log_line)
