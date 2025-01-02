import tkinter as tk
from tkinter import filedialog
import requests
import json

def toggle_generate_button(state):
    """
    Enables or disables the generate button.
    """
    generate_button.config(state=state)

def analyse_repository():
    """
    Fetches the repository URL and other parameters from the GUI and sends a request to the LLM Orchestrator.
    """
    toggle_generate_button(tk.DISABLED)
    
    repo_path = repo_path_entry.get()
    api_key = api_key_entry.get()
    model_name = model_name_entry.get()

    if not repo_path:
        error_label.config(text="Please enter a repository path.")
        toggle_generate_button(tk.NORMAL)
        return

    if not api_key:
        error_label.config(text="Please enter an API key.")
        toggle_generate_button(tk.NORMAL)
        return

    if not model_name:
        error_label.config(text="Please enter a model name.")
        toggle_generate_button(tk.NORMAL)
        return

    try:
        data = {
            "repo_path": repo_path,
            "api_key": api_key,
            "model_name": model_name
        }

        response = requests.post('http://0.0.0.0:8000/generate-readme', json=data)
        response.raise_for_status()

        # Handle the response from the LLM Orchestrator
        response_data = response.json()
        if response_data['status'] == 'success':
            success_label.config(text=response_data['message'])
            error_label.config(text="")  # Clear any previous error message
        else:
            error_label.config(text=f"Unexpected response: {response_data}")
    except requests.exceptions.RequestException as e:
        error_label.config(text=f"Error connecting to LLM Orchestrator: {e}")
    finally:
        toggle_generate_button(tk.NORMAL)


def reset_fields():
    """
    Resets the input fields and labels for a new analysis.
    """
    repo_path_entry.delete(0, tk.END)
    api_key_entry.delete(0, tk.END)
    model_name_entry.delete(0, tk.END)
    error_label.config(text="")
    success_label.config(text="")

# Create the main window
window = tk.Tk()
window.title("README Generator")

# Create widgets
repo_path_label = tk.Label(window, text="Repository Path:")
repo_path_entry = tk.Entry(window, width=50)
repo_path_entry.insert(0, "/Users/replace-the-path-here")  # Dummy repo path
api_key_label = tk.Label(window, text="API Key:")
api_key_entry = tk.Entry(window, width=50)
api_key_entry.insert(0, "your-key-here")  # Dummy API key
model_name_label = tk.Label(window, text="Model Name:")
model_name_entry = tk.Entry(window, width=50)
model_name_entry.insert(0, "gemini-1.5-flash")  # Dummy model name
generate_button = tk.Button(window, text="Generate README", command=analyse_repository)
error_label = tk.Label(window, text="", fg="red")
success_label = tk.Label(window, text="", fg="green")

# Layout the widgets using grid
repo_path_label.grid(row=0, column=0, padx=5, pady=5, sticky="W")
repo_path_entry.grid(row=0, column=1, padx=5, pady=5, sticky="EW")
api_key_label.grid(row=1, column=0, padx=5, pady=5, sticky="W")
api_key_entry.grid(row=1, column=1, padx=5, pady=5, sticky="EW")
model_name_label.grid(row=2, column=0, padx=5, pady=5, sticky="W")
model_name_entry.grid(row=2, column=1, padx=5, pady=5, sticky="EW")
generate_button.grid(row=3, column=0, columnspan=2, padx=5, pady=5, sticky="EW")
error_label.grid(row=4, column=0, columnspan=2, padx=5, pady=5)
success_label.grid(row=5, column=0, columnspan=2, padx=5, pady=5)

# Create the reset button
reset_button = tk.Button(window, text="Reset", command=reset_fields)

# Layout the reset button using grid
reset_button.grid(row=6, column=0, columnspan=2, padx=5, pady=5, sticky="EW")


# Start the GUI event loop
window.mainloop()