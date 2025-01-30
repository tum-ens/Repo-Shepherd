import tkinter as tk
from tkinter import ttk
from tkinter import Menu
import sv_ttk
from configuration import ConfigTab
from readme_test import ReadmeTab
from commit_analyzer import CommitAnalyzerTab

def show_frame(frame):
    frame.tkraise()

root = tk.Tk()
root.title("IDP")
root.geometry("800x600")  # Adjust the window size
# root.resizable(False, False) # Prevent the window from being resizable
# Applying the theme
# sv_ttk.use_dark_theme()
sv_ttk.use_light_theme()

# Shared variable objects
shared_vars = {
    'api_gemini_key': tk.StringVar()
}


# Configure the grid layout for the root window 
root.grid_rowconfigure(0, weight=1)
root.grid_columnconfigure(0, weight=1)

# Create a Notebook
notebook = ttk.Notebook(root)
notebook.grid(row=0, column=0, sticky='nsew')

# Create frames for tabs
frame_setup = ConfigTab(notebook, shared_vars)
frame_readme = ReadmeTab(notebook, shared_vars)
frame_commit = CommitAnalyzerTab(notebook, shared_vars)

# Add frames to Notebook
notebook.add(frame_setup, text='Setup')
notebook.add(frame_readme, text='Readme')
notebook.add(frame_commit, text='Commit Analyzer')

root.mainloop()
