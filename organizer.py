import os
import shutil
import time
from config import FILE_TYPES
from logger import log_action
from features import save_history

def organize_files(path, method="type"):
    """
    method: "type" or "date"
    """
    if not os.path.exists(path):
        log_action("❌ Path does not exist")
        return False

    history = []

    for item in os.listdir(path):
        item_path = os.path.join(path, item)

        # Skip directories
        if os.path.isdir(item_path):
            continue

        moved = False
        destination_path = ""
        
        if method == "type":
            _, ext = os.path.splitext(item)
            ext = ext.lower()

            for folder, extensions in FILE_TYPES.items():
                if ext in extensions:
                    folder_path = os.path.join(path, folder)
                    os.makedirs(folder_path, exist_ok=True)
                    
                    destination_path = os.path.join(folder_path, item)
                    shutil.move(item_path, destination_path)
                    log_action(f"Moved {item} to {folder}")
                    moved = True
                    break

            if not moved:
                other_path = os.path.join(path, "Others")
                os.makedirs(other_path, exist_ok=True)
                destination_path = os.path.join(other_path, item)
                shutil.move(item_path, destination_path)
                log_action(f"Moved {item} to Others")
                moved = True
                
        elif method == "date":
            # Organize by creation/modification year and month
            stat = os.stat(item_path)
            # Use modification time (mtime) as it's more reliable across OSes
            file_time = time.localtime(stat.st_mtime)
            year_month = time.strftime("%Y-%m", file_time)
            
            folder_path = os.path.join(path, year_month)
            os.makedirs(folder_path, exist_ok=True)
            
            destination_path = os.path.join(folder_path, item)
            shutil.move(item_path, destination_path)
            log_action(f"Moved {item} to {year_month}")
            moved = True
            
        if moved:
            history.append({
                "source": item_path,
                "destination": destination_path
            })

    if history:
        save_history(history)
        
    log_action("✅ Files organized successfully!")
    return True

if __name__ == "__main__":
    print("📂 FILE ORGANIZER")
    target_path = input("Enter directory path: ")
    organize_files(target_path)
