import tkinter as tk
from tkinter import ttk


class GettingStartedTab(ttk.Frame):
    def __init__(self, parent, shared_vars):
        super().__init__(parent)
        self.shared_vars = shared_vars
        self.grid(row=0, column=0, sticky='nsew')  # Make it fill the tab
        
        # Create a Text widget for the content
        intro_text = tk.Text(self, wrap='word', height=20, width=80)
        intro_text.grid(row=0, column=0, padx=10, pady=10, sticky='nsew')
        
        # Make it read-only
        intro_text.config(state='normal')
        intro_text.insert('1.0', self.get_intro_content())
        intro_text.config(state='disabled')
        
        # Configure grid to expand
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

    def get_intro_content(self):
        return """Welcome to IDP(?) {We need a name xD}!

    What is IDP?
    IDP uses AI language models (LLMs) to analyze and enhance Python repositories. Whether you're a researcher or developer, IDP simplifies improving your code projects.

    How can IDP help you?
    - Generate READMEs automatically from your code.
    - Improve existing READMEs with better structure.
    - Analyze commit history and suggest messages.
    - Create a clean project structure.
    - Scan for security vulnerabilities and generate a SECURITY.md.
    - Chat with an AI assistant about your repo.

    How to Get Started:
    1. Go to the 'Setup' tab.
    2. Enter your API key (e.g., Gemini) and repository path (local or remote).
    3. Once set up, all tabs unlock—explore and enhance your project!"""