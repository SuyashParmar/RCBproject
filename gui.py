import os
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import threading

# Import backend modules
from organizer import organize_files
from features import remove_duplicates, remove_empty_folders, undo_last_organization
from logger import set_log_callback

class OrganizerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Advanced File Organizer")
        self.root.geometry("600x650")
        self.root.configure(padx=20, pady=20)
        
        self.target_path = tk.StringVar()
        self.org_method = tk.StringVar(value="type") # Default to type
        
        self.setup_ui()
        
        # Connect logger to our GUI text area
        set_log_callback(self.append_log)
        
    def setup_ui(self):
        # Header
        header = tk.Label(self.root, text="📂 File Organizer & Manager", font=("Helvetica", 16, "bold"))
        header.pack(pady=(0, 20))
        
        # Path Selection
        path_frame = tk.Frame(self.root)
        path_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(path_frame, text="Target Directory:", font=("Helvetica", 10)).pack(anchor=tk.W)
        
        path_input_frame = tk.Frame(path_frame)
        path_input_frame.pack(fill=tk.X, pady=5)
        
        path_entry = tk.Entry(path_input_frame, textvariable=self.target_path, font=("Helvetica", 10))
        path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        browse_btn = tk.Button(path_input_frame, text="Browse...", command=self.browse_folder, width=10)
        browse_btn.pack(side=tk.RIGHT)
        
        # Organization Options Frame
        options_frame = tk.LabelFrame(self.root, text="Organization Rules", font=("Helvetica", 10, "bold"), padx=10, pady=10)
        options_frame.pack(fill=tk.X, pady=15)
        
        tk.Radiobutton(options_frame, text="Group by File Type (Images, Docs, etc.)", 
                       variable=self.org_method, value="type").pack(anchor=tk.W, pady=2)
        tk.Radiobutton(options_frame, text="Group by Creation Date (YYYY-MM)", 
                       variable=self.org_method, value="date").pack(anchor=tk.W, pady=2)
                       
        # Action Buttons
        actions_frame = tk.Frame(self.root)
        actions_frame.pack(fill=tk.X, pady=10)
        
        tk.Button(actions_frame, text="Organize Files", bg="#4CAF50", fg="white", 
                  font=("Helvetica", 10, "bold"), command=self.run_organize).pack(fill=tk.X, pady=5)
                  
        tk.Button(actions_frame, text="Undo Last Organization", bg="#f44336", fg="white",
                  command=self.run_undo).pack(fill=tk.X, pady=5)
        
        # Advanced Features
        adv_frame = tk.LabelFrame(self.root, text="Clean-up Tools", font=("Helvetica", 10, "bold"), padx=10, pady=10)
        adv_frame.pack(fill=tk.X, pady=15)
        
        btn_frame = tk.Frame(adv_frame)
        btn_frame.pack(fill=tk.X)
        
        tk.Button(btn_frame, text="Remove Duplicates", command=self.run_remove_duplicates).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)
        tk.Button(btn_frame, text="Delete Empty Folders", command=self.run_remove_empty_folders).pack(side=tk.RIGHT, expand=True, fill=tk.X, padx=5)

        # Logs Console
        tk.Label(self.root, text="Activity Log:", font=("Helvetica", 10, "bold")).pack(anchor=tk.W, pady=(15, 5))
        
        self.log_area = scrolledtext.ScrolledText(self.root, height=10, font=("Consolas", 9), state='disabled', bg="#f5f5f5")
        self.log_area.pack(fill=tk.BOTH, expand=True)

    def browse_folder(self):
        folder = filedialog.askdirectory(title="Select Folder to Organize")
        if folder:
            self.target_path.set(folder)
            
    def append_log(self, text):
        self.log_area.config(state='normal')
        self.log_area.insert(tk.END, text + "\n")
        self.log_area.see(tk.END)
        self.log_area.config(state='disabled')
        # Use simple try-except in case app is closing
        try:
            self.root.update_idletasks() # Ensure GUI refreshes
        except:
            pass

    def get_path_or_warn(self):
        path = self.target_path.get()
        if not path or not os.path.exists(path):
            messagebox.showwarning("Invalid Path", "Please select a valid directory first.")
            return None
        return path

    def execute_task(self, task_func, *args):
        """Runs a task in a separate thread so GUI doesn't freeze."""
        def wrapper():
            task_func(*args)
        
        threading.Thread(target=wrapper, daemon=True).start()

    def run_organize(self):
        path = self.get_path_or_warn()
        if path:
            self.append_log(f"\n--- Starting Organization ({self.org_method.get()}) ---")
            self.execute_task(organize_files, path, self.org_method.get())
            
    def run_undo(self):
        if messagebox.askyesno("Confirm Undo", "Are you sure you want to undo the last file movement?"):
            self.append_log("\n--- Executing Undo ---")
            self.execute_task(undo_last_organization)
            
    def run_remove_duplicates(self):
        path = self.get_path_or_warn()
        if path:
            if messagebox.askyesno("Confirm Deletion", "Are you sure you want to delete exact duplicate files in this directory?"):
                self.append_log("\n--- Removing Duplicates ---")
                self.execute_task(remove_duplicates, path)
                
    def run_remove_empty_folders(self):
        path = self.get_path_or_warn()
        if path:
            self.append_log("\n--- Cleaning Empty Folders ---")
            self.execute_task(remove_empty_folders, path)

if __name__ == "__main__":
    root = tk.Tk()
    app = OrganizerApp(root)
    root.mainloop()
