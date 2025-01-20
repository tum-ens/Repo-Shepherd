import tkinter as tk
from tkinter import ttk
import os

class ReadmeTab(tk.Frame):
    def __init__(self, master, shared_vars, *args, **kwargs):
        super().__init__(master)
        self.shared_vars = shared_vars
        self.grid(row=0, column=0, sticky='nsew')
        label = ttk.Label(self, text="This is the Readme page.")
        label.grid(pady=(10, 10))

        # Entry to display the saved api_key
        self.api_key_entry = ttk.Entry(self)
        self.api_key_entry.grid(pady=(10, 10))

        # Button to display api_key
        display_button = ttk.Button(self, text="Display API Key", command=self.display_api_key)
        display_button.grid(pady=(10, 10))
    
    def display_api_key(self):
        api_key = self.shared_vars['api_gemini_key'].get()
        self.api_key_entry.delete(0, tk.END)
        self.api_key_entry.insert(0, api_key)