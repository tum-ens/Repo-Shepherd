import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
sys.path.insert(1, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../app')))
import tkinter as tk
from tkinter import ttk
from app.readme_automatic_generator import ReadmeAutomaticGenerator
from utils import toolkit
import sv_ttk

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
            file_path = readme.load_original_readme()
            sections = readme.split_sections(file_path)
            empty_list, suggestion_dict, ready_dict = readme.check_section_existence(sections)

            default_list = ['title&about', 'description', 'feature', 'requirement', 'installation', 'usage', 'contact', 'license']
            title = readme.improve_part(default_list[0], ready_dict[default_list[0]])
            description = readme.improve_part(default_list[1], ready_dict[default_list[1]])
            feature = readme.improve_part(default_list[2], ready_dict[default_list[2]])
            installation = readme.improve_part(default_list[4], ready_dict[default_list[4]])
            contact = readme.improve_part(default_list[6], ready_dict[default_list[6]])
            license = readme.improve_part(default_list[7], ready_dict[default_list[7]])
            content = title + description + feature + installation + contact + license

            response = toolkit.export_markdown(content)
            self.message_label.config(text=response, foreground="green")
        
        except Exception as e:
            self.message_label.config(text=f"Error: {e}", foreground="red")

    def simulate_failure(self):
        try:
            # Simulate an intentional failure
            raise ValueError("This is a simulated failure for testing purposes.")
        except Exception as e:
            self.message_label.config(text=f"Error: {e}", foreground="red")
