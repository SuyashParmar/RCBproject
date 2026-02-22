from flask import Flask, render_template, request, jsonify
import os

# Import our backend features
from organizer import organize_files
from features import remove_duplicates, remove_empty_folders, undo_last_organization
from logger import get_recent_logs, log_action

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")
    
@app.route("/cleanup")
def cleanup():
    return render_template("cleanup.html")

@app.route("/search")
def search_page():
    return render_template("search.html")

@app.route("/api/search", methods=["POST"])
def api_search():
    data = request.json
    base_path = data.get("path")
    query = data.get("query", "").lower()
    
    if not base_path or not os.path.exists(base_path) or not query:
        return jsonify({"success": False, "message": "Invalid path or empty query."}), 400
        
    results = []
    try:
        # Search recursively
        for root, _, files in os.walk(base_path):
            for file in files:
                if query in file.lower():
                    full_path = os.path.join(root, file)
                    # Get size safely
                    try:
                        size_bytes = os.path.getsize(full_path)
                        if size_bytes < 1024:
                            size_str = f"{size_bytes} B"
                        elif size_bytes < 1024 * 1024:
                            size_str = f"{size_bytes / 1024:.1f} KB"
                        elif size_bytes < 1024 * 1024 * 1024:
                            size_str = f"{size_bytes / (1024 * 1024):.1f} MB"
                        else:
                            size_str = f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"
                    except:
                        size_str = "Unknown"
                        
                    results.append({
                        "name": file,
                        "path": full_path,
                        "size": size_str
                    })
                    
                    # Hard limit returns to prevent overwhelming the browser
                    if len(results) > 1000:
                        break
            if len(results) > 1000:
                break
                
        return jsonify({"success": True, "results": results})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@app.route("/api/organize", methods=["POST"])
def api_organize():
    data = request.json
    path = data.get("path")
    method = data.get("method", "type")
    
    if not path or not os.path.exists(path):
        return jsonify({"success": False, "message": "Invalid directory path"}), 400
        
    log_action(f"\n--- Starting Organization (Method: {method}) ---")
    success = organize_files(path, method)
    
    if success:
        return jsonify({"success": True, "message": "Files organized successfully!"})
    else:
        return jsonify({"success": False, "message": "Failed to organize files."}), 500

@app.route("/api/clean/duplicates", methods=["POST"])
def api_remove_duplicates():
    data = request.json
    path = data.get("path")
    
    if not path or not os.path.exists(path):
        return jsonify({"success": False, "message": "Invalid directory path"}), 400
        
    log_action("\n--- Removing Duplicates ---")
    success = remove_duplicates(path)
    
    if success:
        return jsonify({"success": True, "message": "Duplicates checked and removed."})
    else:
        return jsonify({"success": False, "message": "Failed to remove duplicates."}), 500

@app.route("/api/clean/empty_folders", methods=["POST"])
def api_remove_empty_folders():
    data = request.json
    path = data.get("path")
    
    if not path or not os.path.exists(path):
        return jsonify({"success": False, "message": "Invalid directory path"}), 400
        
    log_action("\n--- Cleaning Empty Folders ---")
    success = remove_empty_folders(path)
    
    if success:
        return jsonify({"success": True, "message": "Empty folders cleaned."})
    else:
        return jsonify({"success": False, "message": "Failed to clean empty folders."}), 500

@app.route("/api/undo", methods=["POST"])
def api_undo():
    log_action("\n--- Executing Undo ---")
    success = undo_last_organization()
    
    if success:
        return jsonify({"success": True, "message": "Undo operation completed."})
    else:
        return jsonify({"success": False, "message": "Undo operation failed or nothing to undo."}), 500

@app.route("/api/browse", methods=["GET"])
def api_browse():
    import subprocess
    try:
        # On macOS, AppleScript provides a perfectly reliable native folder dialog
        # that doesn't suffer from Tkinter main-thread issues.
        result = subprocess.run([
            'osascript', '-e',
            'tell application "System Events"\n'
            '    activate\n'
            '    set folder_path to POSIX path of (choose folder with prompt "Select Folder to Organize")\n'
            '    return folder_path\n'
            'end tell'
        ], capture_output=True, text=True, check=True)
        
        path = result.stdout.strip()
        if path:
            return jsonify({"success": True, "path": path})
        else:
            return jsonify({"success": False, "message": "No folder selected."})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@app.route("/api/storage", methods=["POST"])
def api_storage():
    data = request.json
    path = data.get("path")
    
    if not path or not os.path.exists(path):
        return jsonify({"success": False, "size": "Unknown", "files": 0, "folders": 0})
        
    total_size = 0
    file_count = 0
    folder_count = 0
    
    try:
        if os.path.isfile(path):
            total_size = os.path.getsize(path)
            file_count = 1
        else:
            for dirpath, dirnames, filenames in os.walk(path):
                folder_count += len(dirnames)
                for f in filenames:
                    fp = os.path.join(dirpath, f)
                    if not os.path.islink(fp):
                        total_size += os.path.getsize(fp)
                        file_count += 1
                        
        # Format size
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if total_size < 1024.0:
                break
            total_size /= 1024.0
            
        formatted_size = f"{total_size:.2f} {unit}"
        return jsonify({
            "success": True, 
            "size": formatted_size,
            "files": file_count,
            "folders": folder_count
        })
    except Exception as e:
        return jsonify({"success": False, "size": "Error reading space", "files": 0, "folders": 0})

@app.route("/api/system_storage", methods=["GET"])
def api_system_storage():
    import shutil
    try:
        # Get usage of the root directory (Mac/Linux) or C:\ (Windows)
        # shutil.disk_usage returns named tuple with total, used, free
        root_path = '/' 
        if os.name == 'nt':
            root_path = 'C:\\'
            
        usage = shutil.disk_usage(root_path)
        
        # Convert to GB for frontend
        gb_convert = 1024 ** 3
        total_gb = usage.total / gb_convert
        used_gb = usage.used / gb_convert
        free_gb = usage.free / gb_convert
        
        # Calculate percentage for progress bar
        used_percent = (usage.used / usage.total) * 100
        
        return jsonify({
            "success": True,
            "total_gb": round(total_gb, 1),
            "used_gb": round(used_gb, 1),
            "free_gb": round(free_gb, 1),
            "used_percent": round(used_percent, 1)
        })
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@app.route("/api/logs", methods=["GET"])
def api_logs():
    return jsonify({"logs": get_recent_logs()})

if __name__ == "__main__":
    app.run(debug=True, port=5001, threaded=True)
