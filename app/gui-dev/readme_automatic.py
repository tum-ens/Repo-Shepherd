import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
sys.path.insert(1, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../app')))
import tkinter as tk
from tkinter import ttk, messagebox
from app.utils.utils import configure_genai_api, get_local_repo_path, clone_remote_repo
from app.readme_automatic_generator import ReadmeAutomaticGenerator
import utils.llm_api as llm_api
from utils import toolkit
import sv_ttk
import yaml
import google.generativeai as genai
from pathlib import Path

class ReadmeAutomaticTab(tk.Frame):
    def __init__(self, root, shared_vars, *args, **kwargs):
        super().__init__(root)
        self.shared_vars = shared_vars

        self.grid(row=0, column=0, sticky='nsew')
        
        # Centering the grid content
        self.grid_columnconfigure(0, weight=1)
        
        label = ttk.Label(self, text="This is the Automatic Readme Generator. This will help you to generate your readme file automatically.")
        label.grid(row=0, column=0, pady=(10, 10))  

        # Entry to display the saved api_key
        # self.api_key_entry = ttk.Entry(self)
        # self.api_key_entry.grid(row=1, column=0, pady=(10, 10))  

        # Button to display api_key
        # display_button = ttk.Button(self, text="Display API Key", command=self.display_api_key)
        # display_button.grid(row=2, column=0, pady=(10, 10))  

        # Button to start the readme analysis
        display_button = ttk.Button(self, text="Start Automatic Readme Generation", command=self.run_readme_improvement)
        display_button.grid(row=3, column=0, pady=(10, 10))  

        # Button to simulate failure
        # fail_button = ttk.Button(self, text="Simulate Failure", command=self.simulate_failure)
        # fail_button.grid(row=4, column=0, pady=(10, 10))  
        
        # Label to display messages
        self.message_label = ttk.Label(self, text="", wraplength=500)
        self.message_label.grid(row=5, column=0, pady=(10, 10))  
    
    def display_api_key(self):
        api_key = self.shared_vars['api_gemini_key'].get()
        self.api_key_entry.delete(0, tk.END)
        self.api_key_entry.insert(0, api_key)

    def run_readme_improvement(self):
        try:
            readme = ReadmeAutomaticGenerator()

            # model initialization
            api_key = self.shared_vars.get("api_gemini_key").get().strip()
            model_name = self.shared_vars.get("default_gemini_model").get()
            configure_genai_api(api_key)
            self.model = genai.GenerativeModel(model_name)

            # repo initialzation
            repo_input = self.shared_vars.get("repo_path_var").get().strip()
            repo_type = self.shared_vars.get("repo_type_var").get()
            repo_path = ""
            if repo_type == "local":
                repo_path = str(get_local_repo_path(repo_input))
            else:
                repo_path = str(clone_remote_repo(repo_input))

            readme_files = [f for f in Path(repo_path).iterdir() if f.is_file() and f.name.lower() == "readme.md"]

            if readme_files:
                file = readme_files[0]  
                self.file = file
            else:
                messagebox.showwarning("Invalid File", "No valid Markdown file (.md or .markdown) found.")

            with open(self.file, 'r', encoding='utf-8') as f:
                markdown_content = f.read()

            with open("app/prompts/improvements_prompt.yaml", 'r') as file:
                prompts_repo = yaml.safe_load(file)

            prompt = prompts_repo["automatic"]

            input = prompt + "\n\n" + markdown_content

            messagebox.showinfo("Info", "Start to improve. Please wait for some seconds.")
            response = llm_api.gemini_api(input, self.model)

            result = toolkit.export_markdown(response)
            self.message_label.config(text=result, foreground="green")
        
        except Exception as e:
            self.message_label.config(text=f"Error: {e}", foreground="red")

    def simulate_failure(self):
        try:
            # Simulate an intentional failure
            raise ValueError("This is a simulated failure for testing purposes.")
        except Exception as e:
            self.message_label.config(text=f"Error: {e}", foreground="red")
