# How to Run: File Organizer Pro

Welcome to File Organizer Pro! This is a modern, locally hosted web application designed to help you quickly organize and clean up your computer's files.

Follow these simple steps to download and run the software on your machine:

## Step 1: Clone the Repository
First, you need to download the code to your local computer. Open your **Terminal** (Mac/Linux) or **Command Prompt** (Windows) and run the following command to securely clone the project from GitHub:

```bash
git clone https://github.com/SuyashParmar/RCBproject.git
```

## Step 2: Navigate into the Folder
Once the download is complete, use the `cd` (change directory) command to enter the project folder:

```bash
cd RCBproject
```

## Step 3: Install Required Dependencies
This application is powered by Python and the lightweight web framework **Flask**. You must ensure Flask is installed on your computer.

Run this simple pip command to install it:
```bash
pip install flask
```
*(Note: If you are using macOS or Linux, you may need to type `pip3 install flask` instead).*

## Step 4: Start the Server
Now that everything is installed, you can start the application! In your terminal, run the main Python script:

```bash
python3 app.py
```
*(Or `python app.py` on Windows).*

If successful, you will see output that looks like this:
> `* Serving Flask app 'app'`  
> `* Running on http://127.0.0.1:5001`

## Step 5: Open the Application
Leave the terminal window running in the background. Open any modern web browser (like Chrome, Safari, or Firefox) and navigate to the local web address provided by the terminal:

👉 **[http://127.0.0.1:5001](http://127.0.0.1:5001)**

You will immediately see the File Organizer Pro dashboard and can begin organizing your digital life!

---

### How to Stop the Application
When you are completely finished using the application and want to shut it down, simply go back to your Terminal window and press **`Ctrl + C`** on your keyboard to stop the Flask server.
