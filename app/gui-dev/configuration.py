import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import webbrowser
import subprocess
import threading
import time
import os
import queue
import google.generativeai as genai
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

import app.utils.utils as utils


def open_url(url):
    webbrowser.open(url, new=2)

def is_ollama_installed():
    try:
        result = subprocess.run(['ollama', '--version'], capture_output=True, text=True)
        return result.returncode == 0
    except FileNotFoundError:
        return False

def get_ollama_models():
    try:
        result = subprocess.run(['ollama', 'list'], capture_output=True, text=True)
        if result.returncode == 0:
            return result.stdout.strip().split('\n')
        else:
            return []
    except Exception as e:
        print(f"Error fetching Ollama models: {e}")
        return []

def install_ollama_model(model, progress_var, progress_label, callback):
    def run_install():
        try:
            process = subprocess.Popen(['ollama', 'pull', model],
                                       stdout=subprocess.PIPE,
                                       stderr=subprocess.STDOUT,
                                       text=True)
            for line in process.stdout:
                progress_var.set(progress_var.get() + 5)
                progress_label.config(text=f"Installing {model}: {progress_var.get()}%")
                if progress_var.get() >= 100:
                    break
            process.wait()
            if process.returncode == 0:
                messagebox.showinfo("Success", f"Model '{model}' installed successfully.")
            else:
                messagebox.showerror("Error", f"Failed to install model '{model}'.")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")
        finally:
            callback()
    
    threading.Thread(target=run_install).start()

class ConfigTab(tk.Frame):
    def __init__(self, parent, shared_vars):        
        super().__init__(parent)
        self.shared_vars = shared_vars
        self.parent = parent
        self.grid(row=0, column=0, sticky="nsew")

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Top toggle frame for API vs. Local
        self.toggle_frame = ttk.Frame(self, height=10)
        self.toggle_frame.grid(row=0, column=0, pady=5, padx=10, sticky="ew")

        self.api_frame = ttk.Frame(self)
        self.local_frame = ttk.Frame(self)
        self.api_frame.grid(row=1, column=0, sticky="nsew")
        self.local_frame.grid(row=1, column=0, sticky="nsew")

        self.model_type = tk.StringVar(value="API")
        self.api_radio = ttk.Radiobutton(
            self.toggle_frame, text="API-Based Models (Recommended)",
            variable=self.model_type, value="API", command=self.switch_model
        )
        self.local_radio = ttk.Radiobutton(
            self.toggle_frame, text="Local-Based Models",
            variable=self.model_type, value="Local", command=self.switch_model
        )
        self.api_radio.grid(row=0, column=0, padx=5)
        self.local_radio.grid(row=0, column=1, padx=5)

        self.create_api_frame()
        self.create_local_frame()
        self.local_frame.grid_remove()  # Show API frame by default

        self.api_key_validated = False
        self.api_gemini_key = None
        
        # Queue for background tasks (used for both API key and repo path)
        self.data_queue = queue.Queue()
        self.after(100, self.process_queue)

        # --- Repository Selection Section ---
        self.repo_frame = ttk.LabelFrame(self, text="Repository Selection", padding=(10, 10))
        self.repo_frame.grid(row=2, column=0, padx=10, pady=10, sticky="ew")

        repo_path_label = ttk.Label(self.repo_frame, text="Repository Path/URL:")
        repo_path_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.repo_path_entry = ttk.Entry(
            self.repo_frame, textvariable=self.shared_vars['repo_path_var'], width=50
        )
        self.repo_path_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        self.browse_button = ttk.Button(self.repo_frame, text="Browse", command=self.browse_local_repo)
        self.browse_button.grid(row=0, column=2, padx=5, pady=5)

        # Status label for repo path check (like API key status)
        self.repo_path_status = ttk.Label(self.repo_frame, text="")
        self.repo_path_status.grid(row=1, column=0, sticky='w', padx=5, pady=5)

        # Button to save (check) the repo path
        self.save_repo_button = ttk.Button(
            self.repo_frame, text="Save Repo Selection", command=self.check_repo_path
        )
        self.save_repo_button.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

    # -----------------------------
    # Repository path logic (similar to API key logic)
    # -----------------------------
    def browse_local_repo(self):
        repo_path = filedialog.askdirectory()
        if repo_path:
            self.repo_path_entry.delete(0, tk.END)
            self.repo_path_entry.insert(0, repo_path)

    def check_repo_path(self):
        repo_input = self.repo_path_entry.get().strip()
        if not repo_input:
            messagebox.showerror("Error", "Repository path/URL is required.")
            return

        def validate_repo():
            self.data_queue.put(("repo_status", "Checking...", "blue"))
            self.data_queue.put(("repo_button", "disabled"))
            try:
                time.sleep(1)  # Simulate validation delay
                # If "github.com" appears anywhere in the repo input, consider it remote.
                if "github.com" in repo_input:
                    new_type = "remote"
                else:
                    new_type = "local"
                valid = True  # In a more complete implementation, add actual checks here.
                if valid:
                    self.data_queue.put(("repo_status", "✔️", "green"))
                    self.data_queue.put(("repo_path_var", repo_input))
                    self.data_queue.put(("repo_type_var", new_type))
                else:
                    self.data_queue.put(("repo_status", "✖️", "red"))
                    self.data_queue.put(("error", "Invalid repository path/URL."))
            except Exception as e:
                self.data_queue.put(("repo_status", "✖️", "red"))
                self.data_queue.put(("error", f"An error occurred: {e}"))
            self.data_queue.put(("repo_button", "normal"))
        threading.Thread(target=validate_repo).start()

    # -----------------------------
    # Switch between API/Local frames
    # -----------------------------
    def switch_model(self):
        if self.model_type.get() == "API":
            self.local_frame.grid_remove()
            self.api_frame.grid(row=1, column=0, sticky="nsew")
        else:
            self.api_frame.grid_remove()
            self.local_frame.grid(row=1, column=0, sticky="nsew")

    # -----------------------------
    # API frames logic
    # -----------------------------
    def create_api_frame(self):
        self.api_frame.grid_rowconfigure(0, weight=1)
        self.api_frame.grid_columnconfigure(0, weight=1)

        api_label = ttk.Label(
            self.api_frame, text="API-Based Models Configuration",
            font=("Helvetica", 14, "bold")
        )
        api_label.grid(row=0, column=0, columnspan=2, pady=10)

        api_model_label = ttk.Label(self.api_frame, text="Select API Model:")
        api_model_label.grid(row=1, column=0, sticky='w', padx=20, pady=(10, 0))
        api_model_tag = ttk.Label(self.api_frame, text="(API-Based: Recommended)", foreground="green")
        api_model_tag.grid(row=1, column=1, sticky='w', padx=20, pady=(10, 0))

        self.api_model = tk.StringVar()
        self.api_model_dropdown = ttk.Combobox(
            self.api_frame, textvariable=self.api_model, state="readonly"
        )
        self.api_model_dropdown['values'] = ["Gemini (Free with High Limits)"]
        self.api_model_dropdown.current(0)
        self.api_model_dropdown.grid(row=2, column=0, columnspan=2, sticky='ew', padx=20, pady=5)
        
        api_key_label = ttk.Label(self.api_frame, text="Gemini API Key:")
        api_key_label.grid(row=3, column=0, sticky='w', padx=20, pady=(10, 0))

        self.api_key_frame = ttk.Frame(self.api_frame)
        self.api_key_frame.grid(row=4, column=0, columnspan=2, sticky='ew', padx=20, pady=5)

        self.api_key_entry = ttk.Entry(self.api_key_frame, width=40)
        self.api_key_entry.grid(row=0, column=0, sticky='ew', padx=(0, 5))

        self.check_button = ttk.Button(
            self.api_key_frame, text="Check API Key", command=self.check_api_key
        )
        self.check_button.grid(row=0, column=1, padx=5)

        self.api_key_status = ttk.Label(self.api_key_frame, text="")
        self.api_key_status.grid(row=0, column=2, padx=5)
        
        api_key_help_button = ttk.Button(
            self.api_frame, text="How to Get API Key",
            command=lambda: open_url("https://ai.google.dev/gemini-api/docs/api-key")
        )
        api_key_help_button.grid(row=5, column=0, columnspan=2, sticky='w', padx=20, pady=5)
        
        # Gemini Model Selection
        gemini_model_label = ttk.Label(self.api_frame, text="Select Gemini Model:")
        gemini_model_label.grid(row=6, column=0, sticky='w', padx=20, pady=(10, 0))

        # Set the default value to "auto" and include "auto" in options
        self.gemini_model = tk.StringVar(value="auto")
        self.gemini_model_dropdown = ttk.Combobox(
            self.api_frame, textvariable=self.gemini_model, state="readonly"
        )
        self.gemini_model_dropdown['values'] = ["auto", "gemini-2.0-flash-lite","gemini-1.5-flash", "gemini-2.0-flash","gemini-2.0-flash-thinking-exp-01-21","gemini-1.5-pro","gemini-2.5-pro-exp-03-25"]
        self.gemini_model_dropdown.current(0)
        self.gemini_model_dropdown.grid(row=7, column=0, sticky='ew', padx=20, pady=5)
        # Bind the event so the StringVar is updated when a new option is selected
        self.gemini_model_dropdown.bind("<<ComboboxSelected>>", self.on_gemini_model_selected)
        
        # New "Save Model" button next to Gemini model dropdown
        self.save_model_button = ttk.Button(
            self.api_frame, text="Save Model", command=self.save_gemini_model
        )
        self.save_model_button.grid(row=7, column=1, sticky='w', padx=5, pady=5)
        
        self.api_save_button = ttk.Button(
            self.api_frame, text="Save", command=self.save_api_config
        )
        self.api_save_button.grid(row=8, column=1, sticky='se', padx=20, pady=20)

    def on_gemini_model_selected(self, event):
        # Update the StringVar explicitly from the combobox selection
        current_value = self.gemini_model_dropdown.get()
        self.gemini_model.set(current_value)
        print(f"DEBUG [ConfigTab]: Gemini model updated to -> {current_value}")

    def check_api_key(self):
        api_gemini_key = self.api_key_entry.get().strip()
        if not api_gemini_key:
            self.api_key_status.config(text="✖️", foreground="red")
            self.api_key_validated = False
            messagebox.showerror("Error", "Gemini API Key is required.")
            return

        # Retrieve the tkinter variable value in the main thread
        selected_model = self.gemini_model.get()

        def validate_key(model):
            self.data_queue.put(("status", "Checking...", "blue"))
            self.data_queue.put(("button", "disabled"))
            
            test_prompt = "Test"
            valid, error_message = utils.validate_gemini_api_key(api_gemini_key, test_prompt)

            if valid:
                self.data_queue.put(("status", "✔️", "green"))
                self.data_queue.put(("shared_var", api_gemini_key))
                self.api_key_validated = True
                self.api_gemini_key = api_gemini_key
                print(f"API Key validated: {self.api_gemini_key}")
            else:
                self.data_queue.put(("status", "✖️", "red"))
                self.api_key_validated = False
                self.data_queue.put(("error", f"Invalid Gemini API Key: {error_message}"))
                
            self.data_queue.put(("button", "normal"))
            
        threading.Thread(target=validate_key, args=(selected_model,)).start()

    def save_api_config(self):
        if not self.api_key_validated:
            self.check_api_key()
            self.after(2500, self.finalize_save_api_config)
        else:
            self.finalize_save_api_config()
    
    def finalize_save_api_config(self):
        if not self.api_key_validated:
            return
        self.api_gemini_key = self.api_key_entry.get().strip()
        self.shared_vars['api_gemini_key'].set(self.api_gemini_key)
        print(f"API Key saved: {self.api_gemini_key}")
        selected_model = self.gemini_model.get()
        messagebox.showinfo("Saved", f"API Configuration saved.\nModel: {selected_model}")

    def save_gemini_model(self):
        # For debugging, print both the StringVar value and the combobox's get() value.
        selected_model_var = self.gemini_model.get()
        selected_model_combo = self.gemini_model_dropdown.get()
        print(f"DEBUG [ConfigTab]: self.gemini_model.get() -> {selected_model_var}")
        print(f"DEBUG [ConfigTab]: combobox.get() -> {selected_model_combo}")
        self.shared_vars['default_gemini_model'].set(selected_model_var)
        print(f"DEBUG [ConfigTab]: self.shared_vars['default_gemini_model'] -> {selected_model_var}")

        messagebox.showinfo("Saved", f"Default Gemini Model saved: {selected_model_var}")

    # -----------------------------
    # Local frames logic
    # -----------------------------
    def create_local_frame(self):
        self.local_frame.grid_rowconfigure(0, weight=1)
        self.local_frame.grid_columnconfigure(0, weight=1)

        local_label = ttk.Label(
            self.local_frame, text="Local-Based Models Configuration",
            font=("Helvetica", 14, "bold")
        )
        local_label.grid(row=0, column=0, columnspan=2, pady=10)
        
        local_model_label = ttk.Label(self.local_frame, text="Select Local Model Framework:")
        local_model_label.grid(row=1, column=0, sticky='w', padx=20, pady=(10, 0))

        self.local_framework = tk.StringVar()
        self.local_framework_dropdown = ttk.Combobox(
            self.local_frame, textvariable=self.local_framework, state="readonly"
        )
        self.local_framework_dropdown['values'] = ["Ollama", "LMStudio", "Llama.cpp"]
        self.local_framework_dropdown.current(0)
        self.local_framework_dropdown.grid(row=2, column=0, columnspan=2, sticky='ew', padx=20, pady=5)
        self.local_framework_dropdown.bind("<<ComboboxSelected>>", self.on_local_framework_selected)
        
        self.ollama_frame = ttk.LabelFrame(self.local_frame, text="Ollama Configuration")
        self.ollama_frame.grid(row=3, column=0, columnspan=2, sticky='ew', padx=20, pady=10)
        
        self.ollama_status = tk.StringVar(value="Checking installation...")
        self.ollama_status_label = ttk.Label(self.ollama_frame, textvariable=self.ollama_status)
        self.ollama_status_label.grid(row=0, column=0, sticky='w', padx=10, pady=5)
        
        self.install_button = ttk.Button(
            self.ollama_frame, text="Install Ollama",
            command=lambda: open_url("https://ollama.com")
        )
        self.install_button.grid(row=1, column=0, sticky='w', padx=10, pady=5)
        
        self.ollama_models_label = ttk.Label(self.ollama_frame, text="Select Ollama Model:")
        self.ollama_models_label.grid(row=2, column=0, sticky='w', padx=10, pady=(10, 0))
        self.ollama_models = tk.StringVar()
        self.ollama_models_dropdown = ttk.Combobox(self.ollama_frame, textvariable=self.ollama_models, state="readonly")
        self.ollama_models_dropdown.grid(row=3, column=0, columnspan=2, sticky='ew', padx=10, pady=5)
        
        self.progress_var = tk.IntVar()
        self.progress_bar = ttk.Progressbar(
            self.ollama_frame, orient='horizontal', length=400,
            mode='determinate', variable=self.progress_var
        )
        self.progress_bar.grid(row=4, column=0, columnspan=2, sticky='ew', padx=10, pady=10)
        self.progress_label = ttk.Label(self.ollama_frame, text="")
        self.progress_label.grid(row=5, column=0, columnspan=2, sticky='ew', padx=10, pady=5)

    def on_local_framework_selected(self, event):
        selected = self.local_framework.get()
        if selected == "Ollama":
            self.ollama_frame.pack(fill='both', expand=True, padx=20, pady=10)
            self.check_ollama_installation()
        else:
            self.ollama_frame.pack_forget()
    
    def check_ollama_installation(self):
        if self.local_framework.get() != "Ollama":
            return
        installed = is_ollama_installed()
        if installed:
            self.ollama_status.set("Ollama is Installed.")
            self.install_button.pack_forget()
            models = get_ollama_models()
            predefined_models = [
                "llama3.1:8b (Not Installed) [Recommended for Most Systems]",
                "llama3.2:3b (Not Installed) [Recommended for Low-End Systems]"
            ]
            models_display = models + predefined_models
            self.ollama_models_dropdown['values'] = models_display
            if models_display:
                self.ollama_models_dropdown.current(0)
            self.ollama_models_dropdown.bind("<<ComboboxSelected>>", self.on_ollama_model_selected)
        else:
            self.ollama_status.set("Ollama is not installed.")
            self.install_button.pack(anchor='w', padx=10, pady=5)
            self.ollama_models_dropdown.set('')
            self.ollama_models_dropdown['values'] = []

    def on_ollama_model_selected(self, event):
        selected_model = self.ollama_models_dropdown.get()
        if "(Not Installed)" in selected_model:
            response = messagebox.askyesno(
                "Model Not Installed",
                f"The selected model '{selected_model}' is not installed. Do you want to install it?"
            )
            if response:
                model_name = selected_model.split(" ")[0]
                self.progress_var.set(0)
                self.progress_label.config(text=f"Installing {model_name}: 0%")
                self.progress_bar.pack(padx=10, pady=5)
                self.progress_label.pack(anchor='w', padx=10)
                install_ollama_model(model_name, self.progress_var, self.progress_label, self.on_install_complete)

    # -----------------------------
    # Background queue logic
    # -----------------------------
    def process_queue(self):
        try:
            while True:
                task = self.data_queue.get_nowait()
                if task[0] == "status":
                    self.api_key_status.config(text=task[1], foreground=task[2])
                elif task[0] == "button":
                    self.check_button.config(state=task[1])
                elif task[0] == "shared_var":
                    self.shared_vars['api_gemini_key'].set(task[1])
                elif task[0] == "error":
                    messagebox.showerror("Error", task[1])
                elif task[0] == "repo_status":
                    self.repo_path_status.config(text=task[1], foreground=task[2])
                elif task[0] == "repo_button":
                    self.save_repo_button.config(state=task[1])
                elif task[0] == "repo_path_var":
                    self.shared_vars['repo_path_var'].set(task[1])
                    print("DEBUG [ConfigTab]: final repo_path_var set to ->", task[1])
                    messagebox.showinfo("Saved", f"Repository selection saved: {task[1]}")
                elif task[0] == "repo_type_var":
                    self.shared_vars['repo_type_var'].set(task[1])
                    print("DEBUG [ConfigTab]: final repo_type_var set to ->", task[1])
        except queue.Empty:
            pass
        self.after(100, self.process_queue)

    def on_install_complete(self):
        self.progress_bar.pack_forget()
        self.progress_label.config(text="")
        self.check_ollama_installation()

if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("700x600")
    shared_vars_test = {
        'api_gemini_key': tk.StringVar(),
        'repo_path_var': tk.StringVar(),
        'repo_type_var': tk.StringVar(value='local'),
        'default_gemini_model': tk.StringVar(value="auto")
    }
    app = ConfigTab(root, shared_vars_test)
    app.pack(fill="both", expand=True)
    root.mainloop()
