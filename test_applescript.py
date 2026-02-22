import subprocess
try:
    result = subprocess.run([
        'osascript', '-e',
        'tell application "System Events" to activate',
        '-e', 'tell application "System Events" to set folder_path to POSIX path of (choose folder with prompt "Select Folder to Organize")',
        '-e', 'return folder_path'
    ], capture_output=True, text=True, check=True)
    print("PATH:", result.stdout.strip())
except Exception as e:
    print("ERROR:", e)
