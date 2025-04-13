# main.py
import tkinter as tk
from tkinter import ttk, messagebox
import sv_ttk
from getting_started import GettingStartedTab
from configuration import ConfigTab
from readme_automatic import ReadmeAutomaticTab
from readme_improvement import ReadmeImprovementTab
from commit_analyzer import CommitAnalyzerTab
from security_generator import SecurityGeneratorTab
from security_scanner_tab import SecurityScannerTab
from gemini_chat_tab import GeminiChatTab
from improve_structure_tab import ImproveStructureTab

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../gui-dev')))

def show_frame(frame):
    frame.tkraise()

root = tk.Tk()
root.title("repo Sheperd")
# root.geometry("800x600")  # Adjust the window size if needed
root.resizable(True, True)
sv_ttk.use_light_theme()

# Shared variable objects
shared_vars = {
    'api_gemini_key': tk.StringVar(),
    'repo_path_var': tk.StringVar(),           # Holds the local path or remote URL
    'repo_type_var': tk.StringVar(value='local'),  # Holds the repository type ('local' or 'remote')
    'default_gemini_model': tk.StringVar(value="auto")  # Default Gemini model selection
}

# Configure the grid layout for the root window
root.grid_rowconfigure(0, weight=1)
root.grid_columnconfigure(0, weight=1)

# Create a Notebook
notebook = ttk.Notebook(root)
notebook.grid(row=0, column=0, sticky='nsew')



# Create frames for tabs
frame_getting_started = GettingStartedTab(notebook, shared_vars)
frame_setup = ConfigTab(notebook, shared_vars)
frame_automatic_readme = ReadmeAutomaticTab(notebook, shared_vars)
frame_improvement_readme = ReadmeImprovementTab(notebook, shared_vars)
frame_commit = CommitAnalyzerTab(notebook, shared_vars)
frame_security_generator = SecurityGeneratorTab(notebook, shared_vars) 
frame_security_scanner = SecurityScannerTab(notebook, shared_vars)
frame_gemini_chat = GeminiChatTab(notebook, shared_vars)
frame_improve_structure = ImproveStructureTab(notebook, shared_vars)

# Add frames to Notebook
notebook.add(frame_getting_started, text='Getting Started')
notebook.add(frame_setup, text='Setup')
notebook.add(frame_automatic_readme, text='Readme Automatic')
notebook.add(frame_improvement_readme, text='Readme Improvement')
notebook.add(frame_commit, text='Commit Analyzer')
notebook.add(frame_security_generator, text='Security Generator')
notebook.add(frame_security_scanner, text='Security Scanner')
notebook.add(frame_gemini_chat, text='Gemini Chat')
notebook.add(frame_improve_structure, text='Improve Structure')

# Initially disable all tabs except Getting Started (index 0) and Setup (index 1)
for i in range(2, notebook.index("end")):  # Start at 2 to skip Getting Started and Setup
    notebook.tab(i, state="disabled")

# Function to enable/disable tabs based on API key and repo path values.
def check_enable_tabs(*args):
    api_key = shared_vars['api_gemini_key'].get().strip()
    repo_path = shared_vars['repo_path_var'].get().strip()
    if api_key and repo_path:
        for i in range(2, notebook.index("end")):  # Skip 0 and 1
            notebook.tab(i, state="normal")
    else:
        for i in range(2, notebook.index("end")):
            notebook.tab(i, state="disabled")

# Trace changes on both variables to update tab states.
shared_vars['api_gemini_key'].trace_add("write", check_enable_tabs)
shared_vars['repo_path_var'].trace_add("write", check_enable_tabs)

# Bind a click event on the Notebook to intercept clicks on disabled tabs.
def on_notebook_click(event):
    # Determine the tab index based on click coordinates.
    try:
        index = notebook.index(f"@{event.x},{event.y}")
    except tk.TclError:
        return
    # Check if the clicked tab is disabled.
    if notebook.tab(index, "state") == "disabled":
        messagebox.showinfo("Information", "Please add API key and repo first.")
        return "break"  # Prevent the default behavior.

# Bind the left mouse button click event to the Notebook.
notebook.bind("<Button-1>", on_notebook_click, add="+") 

# Function to adjust root size based on the current tab
def adjust_root_size(event=None):
    root.update_idletasks()
    req_width = notebook.winfo_reqwidth()
    req_height = notebook.winfo_reqheight()
    min_width, min_height = 800, 600
    max_width, max_height = root.winfo_screenwidth() * 0.8, root.winfo_screenheight() * 0.8
    width = min(max(req_width, min_width), max_width)
    height = min(max(req_height, min_height), max_height)
    root.geometry(f"{int(width)}x{int(height)}")
    root.minsize(min_width, min_height)

notebook.bind("<<NotebookTabChanged>>", adjust_root_size)
adjust_root_size()

root.mainloop()
