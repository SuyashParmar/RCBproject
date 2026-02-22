import datetime
from collections import deque

# Keep the last 100 log messages in memory for the web UI
log_buffer = deque(maxlen=100)

def log_action(message):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    formatted_msg = f"{timestamp} - {message}"
    
    # Save to file
    with open("file_organizer.log", "a", encoding="utf-8") as log:
        log.write(f"{formatted_msg}\n")
    
    # Save to memory buffer for frontend
    log_buffer.append(formatted_msg)
    
    print(formatted_msg)

def get_recent_logs():
    return list(log_buffer)
