import os
import hashlib
import json
import shutil
from logger import log_action

HISTORY_FILE = "history.json"

def get_file_hash(filepath):
    """Calculates the MD5 hash of a file."""
    hasher = hashlib.md5()
    try:
        with open(filepath, 'rb') as f:
            buf = f.read(65536)
            while len(buf) > 0:
                hasher.update(buf)
                buf = f.read(65536)
        return hasher.hexdigest()
    except Exception as e:
        log_action(f"Error reading file {filepath}: {e}")
        return None

def remove_duplicates(path):
    """Finds and removes duplicate files in the given path based on content."""
    if not os.path.exists(path):
        log_action(f"❌ Path does not exist: {path}")
        return False
        
    hashes = {}
    duplicates_removed = 0
    
    for root, _, files in os.walk(path):
        for filename in files:
            filepath = os.path.join(root, filename)
            file_hash = get_file_hash(filepath)
            
            if file_hash:
                if file_hash in hashes:
                    log_action(f"Removing duplicate: {filepath} (Original: {hashes[file_hash]})")
                    try:
                        os.remove(filepath)
                        duplicates_removed += 1
                    except Exception as e:
                        log_action(f"Error removing {filepath}: {e}")
                else:
                    hashes[file_hash] = filepath
                    
    log_action(f"✅ Removed {duplicates_removed} duplicate files.")
    return True

def remove_empty_folders(path):
    """Recursively removes empty folders in the given path."""
    if not os.path.exists(path):
        log_action(f"❌ Path does not exist: {path}")
        return False
        
    empty_folders_removed = 0
    
    # Bottom-up approach ensures nested empty folders are removed
    for root, dirs, _ in os.walk(path, topdown=False):
        for dirname in dirs:
            dirpath = os.path.join(root, dirname)
            try:
                if not os.listdir(dirpath):
                    os.rmdir(dirpath)
                    log_action(f"Removed empty folder: {dirpath}")
                    empty_folders_removed += 1
            except Exception as e:
                log_action(f"Error removing folder {dirpath}: {e}")
                
    log_action(f"✅ Removed {empty_folders_removed} empty folders.")
    return True

def save_history(history_data):
    """Saves organization history to allow undo."""
    try:
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(history_data, f, indent=4)
        log_action("History saved for potential undo.")
    except Exception as e:
        log_action(f"Error saving history: {e}")

def load_history():
    """Loads organization history."""
    if not os.path.exists(HISTORY_FILE):
        return []
        
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        log_action(f"Error loading history: {e}")
        return []

def undo_last_organization():
    """Undoes the last file organization using history.json."""
    history = load_history()
    if not history:
        log_action("❌ No history available to undo.")
        return False
        
    log_action("Starting undo operation...")
    files_restored = 0
    errors = 0
    
    for entry in history:
        source = entry.get("source")
        destination = entry.get("destination")
        
        if source and destination and os.path.exists(destination):
            try:
                # Ensure original directory structure exists
                original_dir = os.path.dirname(source)
                os.makedirs(original_dir, exist_ok=True)
                
                shutil.move(destination, source)
                log_action(f"Restored: {os.path.basename(source)}")
                files_restored += 1
            except Exception as e:
                log_action(f"Error restoring {destination}: {e}")
                errors += 1
        elif not os.path.exists(destination):
            log_action(f"Warning: File not found at destination: {destination}")
            errors += 1
            
    # Clear history after undo
    if os.path.exists(HISTORY_FILE):
        os.remove(HISTORY_FILE)
        
    if errors == 0:
        log_action(f"✅ Undo completed successfully. Restored {files_restored} files.")
    else:
        log_action(f"⚠️ Undo completed with {errors} errors. Restored {files_restored} files.")
    return True
