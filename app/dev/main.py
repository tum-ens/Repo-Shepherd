import tkinter as tk
from tkinter import ttk
from tkinter import Menu
import sv_ttk

class ConfigTab(ttk.Frame):
    def __init__(self, parent, shared_vars):
        super().__init__(parent)
        self.shared_vars = shared_vars
        
        label = ttk.Label(self, text="Config Tab")
        label.pack(pady=10)
        
        # Entry to input api_key
        self.api_key_entry = ttk.Entry(self)
        self.api_key_entry.pack(pady=10)
        
        # Button to save api_key
        save_button = ttk.Button(self, text="Save API Key", command=self.save_api_key)
        save_button.pack(pady=10)
    
    def save_api_key(self):
        api_key = self.api_key_entry.get()
        self.shared_vars['api_key'].set(api_key)

class ReadmeTab(ttk.Frame):
    def __init__(self, parent, shared_vars):
        super().__init__(parent)
        self.shared_vars = shared_vars
        
        label = ttk.Label(self, text="Readme Tab")
        label.pack(pady=10)
        
        # Entry to display the saved api_key
        self.api_key_entry = ttk.Entry(self)
        self.api_key_entry.pack(pady=10)
        
        # Button to display api_key
        display_button = ttk.Button(self, text="Display API Key", command=self.display_api_key)
        display_button.pack(pady=10)
    
    def display_api_key(self):
        api_key = self.shared_vars['api_key'].get()
        self.api_key_entry.delete(0, tk.END)
        self.api_key_entry.insert(0, api_key)

class CommitAnalyzerTab(ttk.Frame):
    def __init__(self, parent, shared_vars):
        super().__init__(parent)
        self.shared_vars = shared_vars
        label = ttk.Label(self, text="Commit Analyzer Tab")
        label.pack(pady=10)

def show_frame(frame):
    frame.tkraise()

root = tk.Tk()
root.title("IDP")
root.geometry("800x600")  # Adjust the window size
# root.resizable(False, False) # Prevent the window from being resizable
# Applying the theme
sv_ttk.use_dark_theme()

# Shared variable objects
shared_vars = {
    'config': tk.StringVar(),
    'user': tk.StringVar(),
    'api_key': tk.StringVar()
}

# Configure the grid layout for the root window 
root.grid_rowconfigure(0, weight=1)
root.grid_columnconfigure(0, weight=1)

# Create a Notebook
notebook = ttk.Notebook(root)
notebook.grid(row=0, column=0, sticky='nsew')

# Create frames for tabs with the shared variable objects
frame_setup = ConfigTab(notebook, shared_vars)
frame_readme = ReadmeTab(notebook, shared_vars)
frame_commit = CommitAnalyzerTab(notebook, shared_vars)

# Add frames to Notebook
notebook.add(frame_setup, text='Setup')
notebook.add(frame_readme, text='Readme')
notebook.add(frame_commit, text='Commit Analyzer')

root.mainloop()
