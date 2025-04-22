import tkinter as tk
from tkinter import ttk
import webbrowser


class GettingStartedTab(ttk.Frame):
    def __init__(self, parent, shared_vars):
        super().__init__(parent)
        self.shared_vars = shared_vars
        self.notebook = parent  # Store notebook reference for tab switching
        self.grid(row=0, column=0, sticky='nsew')

        # Header Label
        header = ttk.Label(self, text="Welcome to Repo Shepherd!", font=("Helvetica", 16, "bold"))
        header.grid(row=0, column=0, padx=10, pady=(10, 5), sticky='ew')

        # Separator
        separator = ttk.Separator(self, orient='horizontal')
        separator.grid(row=1, column=0, padx=10, pady=5, sticky='ew')

        # Text Widget with styled content
        intro_text = tk.Text(self, wrap='word', height=20, width=80, font=("Helvetica", 10))
        intro_text.grid(row=2, column=0, padx=10, pady=5, sticky='nsew')

        # Configure tags for styling
        intro_text.tag_configure("bold", font=("Helvetica", 18, "bold"))
        intro_text.tag_configure("title", font=("Helvetica", 20, "bold"))
        intro_text.tag_configure("text", font=("Helvetica", 16))

        # Insert content
        intro_text.config(state='normal')
        self.insert_styled_content(intro_text)
        intro_text.config(state='disabled')

        # Frame to hold repository and documentation buttons
        button_frame = ttk.Frame(self)
        button_frame.grid(row=3, column=0, padx=10, pady=(5, 2), sticky='ew')

        # Buttons for repository and documentation links
        button_width = 30  # Standard width for all buttons

        repo_button = ttk.Button(button_frame, text="Project Repository", command=lambda: self.open_link("https://github.com/carloslme/tum-idp"), width=button_width)
        repo_button.grid(row=0, column=0, padx=(0, 5), pady=5, sticky='ew')

        docs_button = ttk.Button(button_frame, text="Read the Docs", command=lambda: self.open_link("https://tum-idp.readthedocs.io/en/latest/"), width=button_width)
        docs_button.grid(row=0, column=1, padx=(5, 0), pady=5, sticky='ew')

        # Button to switch to Setup tab
        setup_button = ttk.Button(self, text="Get Started - Go to Setup", command=self.switch_to_setup, width=button_width)
        setup_button.grid(row=4, column=0, padx=10, pady=10, sticky='s')

        # Configure grid weights
        self.grid_rowconfigure(2, weight=1)  # Text expands vertically
        self.grid_columnconfigure(0, weight=1)  # Everything expands horizontally
        button_frame.grid_columnconfigure((0, 1), weight=1)  # Buttons expand equally

    def insert_styled_content(self, text_widget):
        content = [
            ("Your Repository Professionalization Tool\n\n", "title"),
            ("What is Repo Shepherd?\n", "bold"),
            ("Repo Shepherd uses AI language models (LLMs) to analyze and enhance Python repositories. Whether you're a researcher or developer, Repo Shepherd simplifies improving your code projects.\n\n", "text"),
            ("What can you do with Repo Shepherd?\n", "bold"),
            ("- Generate READMEs automatically from your code.\n"
             "- Improve existing READMEs with better structure.\n"
             "- Analyze commit history and suggest messages.\n"
             "- Create a clean project structure.\n"
             "- Scan for security vulnerabilities and generate a SECURITY.md.\n"
             "- Chat with an AI assistant about your repo.\n\n", "text"),
            ("How to get started:\n", "bold"),
            ("1. Go to the 'Setup' tab.\n"
             "2. Enter your API key (e.g., Gemini) and repository path (local or remote).\n"
             "3. Once set up, all tabs unlock—explore and enhance your project!\n", "text"),
        ]
        for text, tag in content:
            text_widget.insert('end', text, tag if tag else ())

    def switch_to_setup(self):
        self.notebook.select(1)  # Switch to Setup tab (index 1)

    def open_link(self, url):
        webbrowser.open(url)  # Opens the given URL in the default web browser
