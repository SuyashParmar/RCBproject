# 📁 File Organizer Pro

**File Organizer Pro** is a modern, web-based intelligent file management system designed to automate the process of sorting, cleaning, and discovering files on your local machine.

Originally conceived as a Python Desktop application using Tkinter, it has been fully migrated into a sleek, premium web application. By bridging powerful backend Python scripts with an intuitive HTML/CSS/JavaScript interface, File Organizer Pro helps you effortlessly tidy up cluttered directories, remove duplicate files, delete empty folders, and perform blazing-fast local recursive searches.

---

## ✨ Features

- **Automated Organization Rules:** Instantly group chaotic folders by File Type (Documents, Images, Music, etc.) or by Modification Date (Year-Month structured folders).
- **Safe "Undo" Mechanism:** Accidentally moved something? The robust Undo function reverts the exact paths from the last action via an internal ledger (`history.json`).
- **Clean-up Tools:**
  - **Duplicate Removal:** Quickly find and delete exact duplicate files using SHA-256 cryptographic hashing.
  - **Empty Folder Deletion:** Recursively scans and cleans your system of empty, leftover directories.
- **Lightning-Fast Local Search:** Deeply scan your computer's storage using the `/search` page to find any file matching an exact sub-string name. It processes and returns up to 1,000 matches concurrently within a native data table.
- **Mac-Native Dialog Selection:** Click "Browse..." on a macOS machine, and a hidden backend AppleScript safely invokes an authentic operating system window, bypassing strict browser sandboxing policies.
- **Live Terminal Logging:** A terminal window built directly into the UI polls real-time status output logs, so you know exactly what the Python backend is doing under the hood.
- **Dynamic System Storage Widget:** View your total active Mac Disk Storage as a live, animated semi-circle donut chart built purely in SVG and dynamic CSS gradients.

---

## 🛠️ Technology Stack

1. **Backend (Python)**
   - **Flask:** Drives the core architecture, routing API requests, and serving static HTML endpoints to `localhost`.
   - **OS & Shutil modules:** Standard libraries used heavily for filesystem interactions, moving, iterating via `os.walk`, and collecting hard disk capacity analytics.
   - **Subprocess / AppleScript (`osascript`):** Utilized entirely to trigger a native Apple "Choose Folder" desktop gui widget.

2. **Frontend**
   - **HTML5:** Features a completely segmented, multi-page application structure leveraging fixed navigation bars and modular UI cards.
   - **CSS3:** Premium aesthetics combining glassmorphism (translucency and blur effects), absolute positioned animated background orbs, dark mode stylization, and SVG stroke manipulation.
   - **Vanilla ES6 JavaScript:** Heavy reliance on the exact `Fetch` API to dispatch asynchronous commands to Python API endpoints (`/api/organize`, `/api/search`, `/api/logs`) without ever reloading the browser state.

---

## 🚀 Installation & Running the Application

### Prerequisites
- You must have Python 3.7+ installed on your computer.
- You must have the `Flask` python package installed. If not, run: `pip install flask`.

### How to Run

1. Clone this repository to your local machine:
   ```bash
   git clone https://github.com/SuyashParmar/RCBproject.git
   ```
2. Navigate into the application folder:
   ```bash
   cd RCBproject
   ```
3. Start the Flask server environment:
   ```bash
   python3 app.py
   ```
4. Once the server registers successfully, you will see a message like `* Running on http://127.0.0.1:5001`.
5. Open any modern web browser and navigate directly to:
   **[http://127.0.0.1:5001](http://127.0.0.1:5001)**

---

## 📖 Application Map / Navigation

1. **Organization Rules (`/` Home):** Start here to select an absolute target directory and clean up a cluttered downloaded or messy desktop folder.
2. **Clean-up Tools (`/cleanup`):** Swap to this screen when you want to execute destructive functions, such as stripping out Exact File Duplicates and deleting unused Empty Folders.
3. **Find Files (`/search`):** Switch to this isolated, high-speed data table viewport to query local folders recursively for specific filenames or patterns.

---

## 🔒 Security Notice

This application executes OS-level scripts that manipulate the underlying host File System. As such, the underlying Flask architecture is designed exclusively to be run on `localhost` (127.0.0.1) as a personal desktop utility via a web interface, and **should not** be openly deployed to a cloud server or exposed on a public network without significant security authentication refactoring. 
