import tkinter as tk
from tkinter import messagebox
import subprocess
import os
import sys

# --- 1. Setting the Base Path for the Launcher (Root directory) ---
if getattr(sys, 'frozen', False):
    # Packaged mode (EngineeringProject.exe is in ROOT)
    BASE_DIR = os.path.dirname(sys.executable)
else:
    # Developer mode (launcher.py is in ROOT)
    BASE_DIR = os.path.abspath(".")

# --- 2. PATH DEFINITIONS FOR MODULES ---
# Python (PogodaApp.exe is in the main directory)
python_path = os.path.join(BASE_DIR, "PogodaApp.exe")

# C++ (in cpp subdirectory)
cpp_path = os.path.join(BASE_DIR, "cpp", "EngineeringDataCpp.exe")

# Java (in java-stooq subdirectory)
java_path = os.path.join(BASE_DIR, "java-stooq", "analiza-gpw.exe")

def openWindow(path):
    """
    Launches an external process.
    Automatically sets the Current Working Directory (CWD) to the one where the .exe file resides.
    """
    target_cwd = os.path.dirname(path)
    try:
        # Popen starts the process. If it's a console program, Windows will open a new window.
        subprocess.Popen(path, cwd=target_cwd)
    except FileNotFoundError:
        messagebox.showerror("Error", f"File not found: {path}\nLooked in: {target_cwd}")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred during launch: {e}")

def run_python(): openWindow(python_path)
def run_cpp(): openWindow(cpp_path)
def run_java(): openWindow(java_path)

# --- Main GUI Window ---
root = tk.Tk()
root.title("Engineering Project Function Selector")
root.geometry("675x235")
root.resizable(False, False)

# Title
label = tk.Label(root, text="Select a module to run: ", font=("Arial", 14, "bold"))
label.pack(pady=15)

# Button frame
frame = tk.Frame(root)
frame.pack(pady=5)

# Button to run Python module
btn_python = tk.Button(frame, text="Weather Data (Python)", command=run_python, width=25, height=5, bg="#3A7CF7", fg='white', font=("Arial", 10, "bold"))
btn_python.pack(side=tk.LEFT, padx=10)

# Button to run C++ module
btn_cpp = tk.Button(frame, text="Eurostat Data (C++)", command=run_cpp, width=25, height=5, bg="#3A7CF7", fg='white', font=("Arial", 10, "bold"))
btn_cpp.pack(side=tk.LEFT, padx=10)

# Button to run Java module
btn_java = tk.Button(frame, text="Stock Market Data (Java)", command=run_java, width=25, height=5, bg="#3A7CF7", fg='white', font=("Arial", 10, "bold"))
btn_java.pack(side=tk.LEFT, padx=10)

# Warning label
warning_label = tk.Label(
    root, 
    text="WARNING: An active Internet connection is required for the modules to work correctly.",
    font=("Arial", 10, "bold"),
    fg="red"
)
warning_label.pack(pady=10)

root.mainloop()