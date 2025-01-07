import tkinter as tk
from tkinter import filedialog, ttk
import requests

def toggle_generate_button(state):
    generate_button.config(state=state)

def browse_repository():
    repo_path = filedialog.askdirectory()
    if repo_path:
        repo_path_entry.delete(0, tk.END)
        repo_path_entry.insert(0, repo_path)

def test_ollama_connection():
    try:
        response = requests.post('http://localhost:11434/api/generate', json={})
        response.raise_for_status()
        status_label.config(text="Ollama connection successful!", fg="green")
    except requests.exceptions.RequestException as e:
        status_label.config(text=f"Ollama connection failed: {e}", fg="red")

def setup_model():
    global model, api_key, model_name
    model = model_var.get()

    if model == "Ollama":
        test_ollama_connection()
    elif model == "Gemini":
        api_key = api_key_entry.get()
        model_name = model_name_entry.get()
        if not api_key or not model_name:
            status_label.config(text="Please enter API key and model name.", fg="red")
            return

    setup_window.destroy()
    open_readme_generator()

def analyse_repository():
    toggle_generate_button(tk.DISABLED)
    update_status("Starting analysis...")

    repo_path = repo_path_entry.get()

    if not repo_path:
        update_status("Please provide the repository path.")
        toggle_generate_button(tk.NORMAL)
        return

    try:
        data = {"repo_path": repo_path, "model": model}
        if model == "Gemini":
            data.update({"api_key": api_key, "model_name": model_name})
            response = requests.post('http://0.0.0.0:8000/generate-readme', json=data)
        else:
            data = {"repo_path": repo_path}
            response = requests.post('http://0.0.0.0:8000/analyze', json=data)

        response.raise_for_status()
        response_data = response.json()
        if response_data.get('status') == 'success':
            update_status(response_data.get('message'), success=True)
        else:
            update_status(f"Unexpected response: {response_data}")
    except requests.exceptions.RequestException as e:
        update_status(f"Error connecting to LLM Orchestrator: {e}")
    finally:
        toggle_generate_button(tk.NORMAL)

def update_status(message, success=False):
    status_label.config(text=message, fg="green" if success else "red")

def open_setup_window():
    global setup_window, model_var, api_key_entry, model_name_entry, status_label

    setup_window = tk.Tk()
    setup_window.title("Setup")

    model_label = tk.Label(setup_window, text="Select Model:")
    model_var = tk.StringVar(value="Ollama")
    ollama_radio = tk.Radiobutton(setup_window, text="Ollama", variable=model_var, value="Ollama")
    gemini_radio = tk.Radiobutton(setup_window, text="Gemini", variable=model_var, value="Gemini")

    api_key_label = tk.Label(setup_window, text="API Key:")
    api_key_entry = tk.Entry(setup_window, width=50)
    model_name_label = tk.Label(setup_window, text="Model Name:")
    model_name_entry = tk.Entry(setup_window, width=50)

    connect_button = tk.Button(setup_window, text="Setup Model", command=setup_model)
    status_label = tk.Label(setup_window, text="", fg="red")

    model_label.grid(row=0, column=0, padx=5, pady=5, sticky="W")
    ollama_radio.grid(row=1, column=0, padx=5, pady=5, sticky="W")
    gemini_radio.grid(row=1, column=1, padx=5, pady=5, sticky="W")
    api_key_label.grid(row=2, column=0, padx=5, pady=5, sticky="W")
    api_key_entry.grid(row=2, column=1, padx=5, pady=5, columnspan=2)
    model_name_label.grid(row=3, column=0, padx=5, pady=5, sticky="W")
    model_name_entry.grid(row=3, column=1, padx=5, pady=5, columnspan=2)
    connect_button.grid(row=4, column=0, columnspan=3, padx=5, pady=5, sticky="EW")
    status_label.grid(row=5, column=0, columnspan=3, padx=5, pady=5)

    setup_window.mainloop()

def open_readme_generator():
    global repo_path_entry, generate_button, status_label

    readme_window = tk.Tk()
    readme_window.title("README Generator")

    repo_path_label = tk.Label(readme_window, text="Repository Path:")
    repo_path_entry = tk.Entry(readme_window, width=50)
    repo_path_button = tk.Button(readme_window, text="Browse", command=browse_repository)
    generate_button = tk.Button(readme_window, text="Generate README", command=analyse_repository)
    status_label = tk.Label(readme_window, text="", fg="red")
    reset_button = tk.Button(readme_window, text="Reset", command=reset_fields)

    repo_path_label.grid(row=0, column=0, padx=5, pady=5, sticky="W")
    repo_path_entry.grid(row=0, column=1, padx=5, pady=5)
    repo_path_button.grid(row=0, column=2, padx=5, pady=5)
    generate_button.grid(row=1, column=0, columnspan=3, padx=5, pady=5, sticky="EW")
    status_label.grid(row=2, column=0, columnspan=3, padx=5, pady=5)
    reset_button.grid(row=3, column=0, columnspan=3, padx=5, pady=5, sticky="EW")

    progress = ttk.Progressbar(readme_window, orient="horizontal", length=300, mode="determinate")
    progress.grid(row=4, column=0, columnspan=3, padx=5, pady=5)

    readme_window.mainloop()

def reset_fields():
    repo_path_entry.delete(0, tk.END)
    status_label.config(text="")

# Initialize global variables
model = None
api_key = None
model_name = None

# Start the setup window
open_setup_window()
