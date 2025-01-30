import tkinter as tk
from tkinter import ttk

class CommitAnalyzerTab(tk.Frame):
    def __init__(self, master, shared_vars):
        super().__init__(master)
        self.shared_vars = shared_vars
        self.grid(row=0, column=0, sticky='nsew')
        label = ttk.Label(self, text="This is the Commit Analyzer page.")
        label.grid(pady=(10, 10))
