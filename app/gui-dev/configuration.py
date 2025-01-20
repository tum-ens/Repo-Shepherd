import tkinter as tk
from tkinter import ttk, messagebox
import webbrowser
import subprocess
import threading
import google.generativeai as genai
import time
import os

# Function to open URLs in the default browser
def open_url(url):
    webbrowser.open(url, new=2)  # new=2 opens in a new tab

# Function to check if Ollama is installed
def is_ollama_installed():
    try:
        # Attempt to run 'ollama --version' to check installation
        result = subprocess.run(['ollama', '--version'], capture_output=True, text=True)
        return result.returncode == 0
    except FileNotFoundError:
        return False

# Function to get list of installed Ollama models
def get_ollama_models():
    try:
        result = subprocess.run(['ollama', 'list'], capture_output=True, text=True)
        if result.returncode == 0:
            # Assuming the output is one model per line
            models = result.stdout.strip().split('\n')
            return models
        else:
            return []
    except Exception as e:
        print(f"Error fetching Ollama models: {e}")
        return []

# Function to install an Ollama model
def install_ollama_model(model, progress_var, progress_label, callback):
    def run_install():
        try:
            process = subprocess.Popen(['ollama', 'pull', model], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
            for line in process.stdout:
                # Update progress (simple simulation)
                # In real scenario, parse the output to get actual progress
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

        # Configure the grid layout for the frame
        self.grid_rowconfigure(0, weight=1)        
        self.grid_columnconfigure(0, weight=1)

        # Main containers
        self.toggle_frame = ttk.Frame(self, height=10)
        self.toggle_frame.grid(row=0, column=0, pady=5, padx=10, sticky="ew")

        self.api_frame = ttk.Frame(self)
        self.local_frame = ttk.Frame(self)
        self.api_frame.grid(row=1, column=0, sticky="nsew")
        self.local_frame.grid(row=1, column=0, sticky="nsew")

        # Toggle between API-Based and Local-Based Models
        self.model_type = tk.StringVar(value="API")
        self.api_radio = ttk.Radiobutton(self.toggle_frame, text="API-Based Models (Recommended)", variable=self.model_type, value="API", command=self.switch_model)
        self.local_radio = ttk.Radiobutton(self.toggle_frame, text="Local-Based Models", variable=self.model_type, value="Local", command=self.switch_model)
        self.api_radio.grid(row=0, column=0, padx=5)
        self.local_radio.grid(row=0, column=1, padx=5)

        # API-Based Models Configuration
        self.create_api_frame()

        # Local-Based Models Configuration
        self.create_local_frame()

        # By default, show API frame
        self.local_frame.grid_remove()

        self.api_gemini_key = None
    
    def switch_model(self):
        if self.model_type.get() == "API":
            self.local_frame.grid_remove()
            self.api_frame.grid(row=1, column=0, sticky="nsew")
        else:
            self.api_frame.grid_remove()
            self.local_frame.grid(row=1, column=0, sticky="nsew")
    
    def create_api_frame(self):
        # Configure the grid layout for the frame
        self.api_frame.grid_rowconfigure(0, weight=1)
        self.api_frame.grid_columnconfigure(0, weight=1)

        # API-Based Models Configuration
        api_label = ttk.Label(self.api_frame, text="API-Based Models Configuration", font=("Helvetica", 14, "bold"))
        api_label.grid(row=0, column=0, columnspan=2, pady=10)

        # Select API Model with Tag
        api_model_label = ttk.Label(self.api_frame, text="Select API Model:")
        api_model_label.grid(row=1, column=0, sticky='w', padx=20, pady=(10, 0))
        api_model_tag = ttk.Label(self.api_frame, text="(API-Based: Recommended)", foreground="green")
        api_model_tag.grid(row=1, column=1, sticky='w', padx=20, pady=(10, 0))
        self.api_model = tk.StringVar()
        self.api_model_dropdown = ttk.Combobox(self.api_frame, textvariable=self.api_model, state="readonly")
        self.api_model_dropdown['values'] = ["Gemini (Free with High Limits)"]
        self.api_model_dropdown.current(0)
        self.api_model_dropdown.grid(row=2, column=0, columnspan=2, sticky='ew', padx=20, pady=5)
        
        # Gemini API Key with Tag and Check Button
        api_key_label = ttk.Label(self.api_frame, text="Gemini API Key:")
        api_key_label.grid(row=3, column=0, sticky='w', padx=20, pady=(10, 0))
        self.api_key_frame = ttk.Frame(self.api_frame)
        self.api_key_frame.grid(row=4, column=0, columnspan=2, sticky='ew', padx=20, pady=5)
        self.api_key_entry = ttk.Entry(self.api_key_frame, width=40)
        self.api_key_entry.grid(row=0, column=0, sticky='ew', padx=(0, 5))
        
        # Check API Key Button
        self.check_button = ttk.Button(self.api_key_frame, text="Check API Key", command=self.check_api_key)
        self.check_button.grid(row=0, column=1, padx=5)
        
        # API Key Validation Status
        self.api_key_status = ttk.Label(self.api_key_frame, text="")
        self.api_key_status.grid(row=0, column=2, padx=5)
        
        # How to Get API Key Button
        api_key_help_button = ttk.Button(self.api_frame, text="How to Get API Key", command=lambda: open_url("https://ai.google.dev/gemini-api/docs/api-key"))
        api_key_help_button.grid(row=5, column=0, columnspan=2, sticky='w', padx=20, pady=5)
        
        # Gemini Model Selection with Tag
        gemini_model_label = ttk.Label(self.api_frame, text="Select Gemini Model:")
        gemini_model_label.grid(row=6, column=0, sticky='w', padx=20, pady=(10, 0))
        self.gemini_model = tk.StringVar()
        self.gemini_model_dropdown = ttk.Combobox(self.api_frame, textvariable=self.gemini_model, state="readonly")
        self.gemini_model_dropdown['values'] = ["Flash 1.5 (Recommended)", "Flash 2.0 EXP (Experimental)"]
        self.gemini_model_dropdown.current(0)
        self.gemini_model_dropdown.grid(row=7, column=0, columnspan=2, sticky='ew', padx=20, pady=5)
        
        # Save Button at Bottom Right
        self.api_save_button = ttk.Button(self.api_frame, text="Save", command=self.save_api_config)
        self.api_save_button.grid(row=8, column=1, sticky='se', padx=20, pady=20)
        
        # Variable to track API key validation
        self.api_key_validated = False

    def create_local_frame(self):
        # Configure the grid layout for the frame
        self.local_frame.grid_rowconfigure(0, weight=1)
        self.local_frame.grid_columnconfigure(0, weight=1)

        # Local-Based Models Configuration
        local_label = ttk.Label(self.local_frame, text="Local-Based Models Configuration", font=("Helvetica", 14, "bold"))
        local_label.grid(row=0, column=0, columnspan=2, pady=10)
        
        # Select Local Model Framework
        local_model_label = ttk.Label(self.local_frame, text="Select Local Model Framework:")
        local_model_label.grid(row=1, column=0, sticky='w', padx=20, pady=(10, 0))
        self.local_framework = tk.StringVar()
        self.local_framework_dropdown = ttk.Combobox(self.local_frame, textvariable=self.local_framework, state="readonly")
        self.local_framework_dropdown['values'] = ["Ollama", "LMStudio", "Llama.cpp"]
        self.local_framework_dropdown.current(0)
        self.local_framework_dropdown.grid(row=2, column=0, columnspan=2, sticky='ew', padx=20, pady=5)
        self.local_framework_dropdown.bind("<<ComboboxSelected>>", self.on_local_framework_selected)
        
        # Ollama Configuration Section
        self.ollama_frame = ttk.LabelFrame(self.local_frame, text="Ollama Configuration")
        self.ollama_frame.grid(row=3, column=0, columnspan=2, sticky='ew', padx=20, pady=10)
        
        self.ollama_status = tk.StringVar(value="Checking installation...")
        self.ollama_status_label = ttk.Label(self.ollama_frame, textvariable=self.ollama_status)
        self.ollama_status_label.grid(row=0, column=0, sticky='w', padx=10, pady=5)
        
        self.install_button = ttk.Button(self.ollama_frame, text="Install Ollama", command=lambda: open_url("https://ollama.com"))
        self.install_button.grid(row=1, column=0, sticky='w', padx=10, pady=5)
        
        # Ollama Models with Tags
        self.ollama_models_label = ttk.Label(self.ollama_frame, text="Select Ollama Model:")
        self.ollama_models_label.grid(row=2, column=0, sticky='w', padx=10, pady=(10, 0))
        self.ollama_models = tk.StringVar()
        self.ollama_models_dropdown = ttk.Combobox(self.ollama_frame, textvariable=self.ollama_models, state="readonly")
        self.ollama_models_dropdown.grid(row=3, column=0, columnspan=2, sticky='ew', padx=10, pady=5)
        
        # Progress Bar for Installation
        self.progress_var = tk.IntVar()
        self.progress_bar = ttk.Progressbar(self.ollama_frame, orient='horizontal', length=400, mode='determinate', variable=self.progress_var)
        self.progress_bar.grid(row=4, column=0, columnspan=2, sticky='ew', padx=10, pady=10)
        self.progress_label = ttk.Label(self.ollama_frame, text="")
        self.progress_label.grid(row=5, column=0, columnspan=2, sticky='ew', padx=10, pady=5)

    def get_api_key(self): 
        return self.api_gemini_key

    def check_api_key(self):
        api_gemini_key = self.api_key_entry.get().strip()
        if not api_gemini_key:
            self.api_key_status.config(text="✖️", foreground="red")
            self.api_key_validated = False
            messagebox.showerror("Error", "Gemini API Key is required.")
            return
        
        # Replace this with actual API key validation logic
        def validate_key():
            # Simulating a delay for validation
            self.check_button.config(state='disabled')
            self.api_key_status.config(text="Checking...", foreground="blue")
            self.update_idletasks()
            
            # Validate the API key
            try:
                genai.configure(api_key=api_gemini_key)
                model = genai.GenerativeModel("gemini-1.5-flash") 
                response = model.generate_content("Hello, world!") 
                print(response.text)
                valid = True  # Connection successful
            except Exception as e:
                print(f"Error connecting to Gemini API: {e}")
                if "API key not valid" not in str(e):
                    messagebox.showerror("Error", f"An error occurred: {e}")
                valid = False
            
            # Here you would implement actual validation, e.g., API call
            time.sleep(1)  # Simulate network delay
            if valid:
                self.api_key_status.config(text="✔️", foreground="green")
                self.api_key_validated = True
                self.api_gemini_key = self.api_key_entry.get().strip()
                self.shared_vars['api_gemini_key'].set(self.api_gemini_key)
                print(f"API Key validated: {self.api_gemini_key}")
            else:
                self.api_key_status.config(text="✖️", foreground="red")
                self.api_key_validated = False
                messagebox.showerror("Error", "Invalid Gemini API Key.")
            self.check_button.config(state='normal')
        
        threading.Thread(target=validate_key).start()
    
    def save_api_config(self):
        if not self.api_key_validated:
            self.check_api_key()
            # Wait briefly to allow the validation thread to start
            self.after(2500, self.finalize_save_api_config)
        else:
            self.finalize_save_api_config()
    
    def finalize_save_api_config(self):
        if not self.api_key_validated:
            # Validation failed or not completed yet
            return
        self.api_gemini_key = self.api_key_entry.get().strip()
        self.shared_vars['api_gemini_key'].set(self.api_gemini_key)
        print(f"API Key saved: {self.api_gemini_key}")
        selected_model = self.gemini_model.get()
        # Implement actual save functionality as needed
        messagebox.showinfo("Saved", f"API Configuration saved.\nModel: {selected_model}")
    
    def save_local_config(self):
        selected_framework = self.local_framework.get()
        if selected_framework == "Ollama":
            if not is_ollama_installed():
                messagebox.showerror("Error", "Ollama is not installed.")
                return
            selected_model = self.ollama_models_dropdown.get()
            if not selected_model:
                messagebox.showerror("Error", "Please select an Ollama model.")
                return
            if "(Not Installed)" in selected_model:
                model_name = selected_model.split(" ")[0]
                self.progress_var.set(0)
                self.progress_label.config(text=f"Installing {model_name}: 0%")
                self.progress_bar.pack(padx=10, pady=5)
                self.progress_label.pack(anchor='w', padx=10)
                install_ollama_model(model_name, self.progress_var, self.progress_label, self.on_install_complete)
            else:
                messagebox.showinfo("Saved", f"Local Configuration saved.\nFramework: {selected_framework}\nModel: {selected_model}")
        else:
            # Handle other local frameworks if added
            selected_framework = self.local_framework.get()
            messagebox.showinfo("Saved", f"Local Configuration saved.\nFramework: {selected_framework}")
        # Implement actual save functionality as needed
    
    def on_install_complete(self):
        self.progress_bar.pack_forget()
        self.progress_label.config(text="")
        self.check_ollama_installation()
    
    def on_local_framework_selected(self, event):
        selected = self.local_framework.get()
        if selected == "Ollama":
            self.ollama_frame.pack(fill='both', expand=True, padx=20, pady=10)
            self.check_ollama_installation()
        else:
            # Hide Ollama configuration if other frameworks are selected
            self.ollama_frame.pack_forget()
    
    def check_ollama_installation(self):
        if self.local_framework.get() != "Ollama":
            return
        installed = is_ollama_installed()
        if installed:
            self.ollama_status.set("Ollama is Installed.")
            self.install_button.pack_forget()
            # Fetch and populate models
            models = get_ollama_models()
            # Add predefined models that might not be installed
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
            # Inform user that the model is not installed
            response = messagebox.askyesno("Model Not Installed", f"The selected model '{selected_model}' is not installed. Do you want to install it?")
            if response:
                model_name = selected_model.split(" ")[0]
                self.progress_var.set(0)
                self.progress_label.config(text=f"Installing {model_name}: 0%")
                self.progress_bar.pack(padx=10, pady=5)
                self.progress_label.pack(anchor='w', padx=10)
                install_ollama_model(model_name, self.progress_var, self.progress_label, self.on_install_complete)

if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("500x600")
    app = ConfigTab(root)
    app.pack(fill="both", expand=True)
    root.mainloop()
