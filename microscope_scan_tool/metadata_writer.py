import os
from datetime import datetime
from pycromanager import Core

def save_fiji_metadata(save_dir, positions):
    """
    Saves stage coordinates in FIJI-compatible TileConfiguration format.
    
    Args:
        save_dir (str): Directory to save the .txt file.
        positions (list of tuples): (filename, x, y)
    """
    os.makedirs(save_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    output_file = os.path.join(save_dir, f"TileConfiguration_{timestamp}.txt")

    with open(output_file, "w") as f:
        f.write("\n")  # Required blank first line for FIJI
        f.write("dim = 2\n")
        for filename, x, y in positions:
            f.write(f"{filename}; ; ({int(x)}, {int(y)})\n")

    print(f"FIJI metadata saved to: {output_file}")
    return output_file
