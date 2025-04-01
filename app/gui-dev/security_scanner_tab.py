import tkinter as tk
from tkinter import ttk, messagebox
import threading
import json
import math
from pathlib import Path
import os
import git
import google.generativeai as genai

# Import functions and constants from your scanner module.
# Make sure your scanner module (security_scanner_gemini_all_code_withsecondpass.py)
# exports these functions.
import app.security_scanner_gemini_all_code_withsecondpass as scanner
from app.security_scanner_gemini_all_code_withsecondpass import (
    extract_code_files,
    generate_security_report,
    get_relative_path,
    refine_vulnerability_report_gemini_batch,
    load_repo_content_to_text,
    save_json,
    get_local_repo_path,
    clone_remote_repo,
    initialize_local_repo,
    configure_genai_api,
    SECURITY_OUTPUT_FILE,
    IMPROVED_SECURITY_OUTPUT_FILE,
    REPO_CONTENT_FILE,
    MODEL_NAME,
    SECOND_PASS_MODEL,
    upload_file_to_gemini,
    BATCH_SIZE,
)

class SecurityScannerTab(ttk.Frame):
    def __init__(self, parent, shared_vars):
        super().__init__(parent)
        self.shared_vars = shared_vars
        self.create_widgets()

    def create_widgets(self):
        # Title label
        title_label = ttk.Label(self, text="Security Scanner", font=("Helvetica", 16, "bold"))
        title_label.pack(pady=10)

        # Buttons for first and second pass
        self.first_pass_button = ttk.Button(self, text="Run First Pass", command=self.run_first_pass)
        self.first_pass_button.pack(pady=5)

        self.second_pass_button = ttk.Button(self, text="Run Second Pass", command=self.run_second_pass)
        self.second_pass_button.pack(pady=5)

        # Determinate progress bar (max=100)
        self.progress = ttk.Progressbar(self, mode="determinate", maximum=100, value=0)
        self.progress.pack(fill="x", padx=20, pady=5)

        # Label for showing numerical progress (e.g., "3/6")
        self.progress_label = ttk.Label(self, text="Progress: 0/0")
        self.progress_label.pack(pady=(0, 10))

        # Text widget to display JSON summary output
        self.summary_text = tk.Text(self, height=10, wrap="word")
        self.summary_text.pack(fill="both", expand=True, padx=20, pady=10)

    def run_first_pass(self):
        # Get necessary values in the main thread
        repo_input = self.shared_vars.get("repo_path_var").get().strip()
        repo_type = self.shared_vars.get("repo_type_var").get()
        api_key = self.shared_vars.get("api_gemini_key").get().strip()
        
        # Disable buttons and reset progress bar and label
        self.first_pass_button.config(state="disabled")
        self.second_pass_button.config(state="disabled")
        self.progress.config(value=0)
        self.progress_label.config(text="Progress: 0/0")
        
        # Start the background thread with the captured values
        threading.Thread(
            target=self.first_pass_thread,
            args=(repo_input, repo_type, api_key),
            daemon=True
        ).start()

    def first_pass_thread(self, repo_input, repo_type, api_key):
        try:
            # Validate inputs
            if not repo_input:
                self.after(0, lambda: messagebox.showerror("Error", "Repository path/URL is not set."))
                return
            if not api_key:
                self.after(0, lambda: messagebox.showerror("Error", "API key is not set."))
                return

            # Initialize repository based on type
            if repo_type == "local":
                repo_path = get_local_repo_path(repo_input)
            else:
                repo_path = clone_remote_repo(repo_input)
            repo = initialize_local_repo(repo_path)
            repo_name = Path(repo_path).name

            # Configure Gemini API and initialize the model for first pass analysis
            configure_genai_api(api_key)
            gemini_model = genai.GenerativeModel(MODEL_NAME)
            # Set the module-level model in scanner for functions that rely on it
            scanner.gemini_model = gemini_model

            # Get list of code files
            code_files = extract_code_files(repo)
            total_files = len(code_files)
            if total_files == 0:
                self.after(0, lambda: messagebox.showerror("Error", "No code files found in the repository."))
                return

            # Update progress label with total files
            self.after(0, lambda: self.progress_label.config(text=f"Progress: 0/{total_files}"))

            security_output = {}
            threat_summary = {
                "code quality issue": 0,
                "low": 0,
                "medium": 0,
                "high": 0,
                "critical": 0,
            }

            # Process each file and update progress bar and label
            for idx, file_path in enumerate(code_files, start=1):
                relative_file_path = get_relative_path(repo, file_path, repo_name)
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        file_content = f.read()
                except Exception as e:
                    security_output[relative_file_path] = {"error": f"Failed to read file: {e}"}
                    continue

                try:
                    vulnerabilities = generate_security_report(file_content, relative_file_path, model=gemini_model)
                    if vulnerabilities == {"vulnerabilities": []}:
                        security_output[relative_file_path] = []
                    elif isinstance(vulnerabilities, list):
                        security_output[relative_file_path] = vulnerabilities
                        for vuln in vulnerabilities:
                            level = vuln.get("threat_level", "code quality issue").lower()
                            if level not in threat_summary:
                                level = "code quality issue"
                            threat_summary[level] += 1
                    else:
                        security_output[relative_file_path] = vulnerabilities
                except Exception as e:
                    security_output[relative_file_path] = {"error": f"Failed to analyze: {e}"}

                # Update progress bar and label
                progress_value = int((idx / total_files) * 100)
                self.after(0, lambda val=progress_value: self.progress.config(value=val))
                self.after(0, lambda cur=idx, tot=total_files: self.progress_label.config(text=f"Progress: {cur}/{tot}"))
            
            security_output["threat_summary"] = threat_summary

            # Save JSON output
            script_dir = Path(__file__).parent
            output_path = script_dir / SECURITY_OUTPUT_FILE
            save_json(security_output, output_path, "security vulnerabilities (first pass)")

            summary_text = json.dumps(threat_summary, indent=4)
            self.after(0, lambda: self.summary_text.delete("1.0", tk.END))
            self.after(0, lambda: self.summary_text.insert(tk.END, summary_text))
            self.after(0, lambda: messagebox.showinfo("Success", f"First pass completed.\nResults saved to:\n{output_path}"))
        except Exception as e:
            self.after(0, lambda: messagebox.showerror("Error", f"First pass failed: {e}"))
        finally:
            self.after(0, lambda: self.first_pass_button.config(state="normal"))
            self.after(0, lambda: self.second_pass_button.config(state="normal"))

    def run_second_pass(self):
        # Get necessary values in the main thread
        repo_input = self.shared_vars.get("repo_path_var").get().strip()
        repo_type = self.shared_vars.get("repo_type_var").get()
        api_key = self.shared_vars.get("api_gemini_key").get().strip()

        # Disable buttons and reset progress bar and label
        self.first_pass_button.config(state="disabled")
        self.second_pass_button.config(state="disabled")
        self.progress.config(value=0)
        self.progress_label.config(text="Progress: 0/0")
        
        threading.Thread(
            target=self.second_pass_thread,
            args=(repo_input, repo_type, api_key),
            daemon=True
        ).start()

    def second_pass_thread(self, repo_input, repo_type, api_key):
        try:
            script_dir = Path(__file__).parent
            first_pass_path = script_dir / SECURITY_OUTPUT_FILE
            if not first_pass_path.exists():
                self.after(0, lambda: messagebox.showerror("Error", "First pass results not found. Run first pass first."))
                return
            with open(first_pass_path, "r", encoding="utf-8") as f:
                security_report = json.load(f)

            # Initialize repository again
            if repo_type == "local":
                repo_path = get_local_repo_path(repo_input)
            else:
                repo_path = clone_remote_repo(repo_input)
            repo = initialize_local_repo(repo_path)
            repo_name = Path(repo_path).name

            # Convert repository content to text for context
            repo_content_path = script_dir / REPO_CONTENT_FILE
            repo_content = load_repo_content_to_text(repo, repo_name, repo_content_path)
            if not repo_content:
                self.after(0, lambda: messagebox.showerror("Error", "Failed to load repository content."))
                return

            # Upload repository content to Gemini
            try:
                uploaded_repo = upload_file_to_gemini(repo_content_path)
            except Exception as e:
                uploaded_repo = genai.upload_file(repo_content_path)

            # Configure Gemini API and initialize model for second pass refinement
            configure_genai_api(api_key)
            gemini_model_second = genai.GenerativeModel(SECOND_PASS_MODEL)

            file_keys = [k for k in security_report.keys() if k != "threat_summary"]
            total_files = len(file_keys)
            total_batches = math.ceil(total_files / BATCH_SIZE)
            improved_security_output = {"threat_summary": {
                "code quality issue": 0,
                "low": 0,
                "medium": 0,
                "high": 0,
                "critical": 0,
            }}

            # Update progress label for batches
            self.after(0, lambda: self.progress_label.config(text=f"Progress: 0/{total_batches}"))

            for batch_index in range(0, total_files, BATCH_SIZE):
                batch_files = file_keys[batch_index: batch_index + BATCH_SIZE]
                vulnerability_batch = {}
                for file_path in batch_files:
                    vulnerabilities = security_report.get(file_path, [])
                    if vulnerabilities and not ("error" in vulnerabilities):
                        vulnerability_batch[file_path] = vulnerabilities
                    else:
                        improved_security_output[file_path] = vulnerabilities if vulnerabilities else []
                batch_result = refine_vulnerability_report_gemini_batch(
                    vulnerability_batch, repo_content, uploaded_repo, model=gemini_model_second
                )
                for file_path in batch_files:
                    refined_vulns = batch_result.get(file_path, [])
                    improved_security_output[file_path] = refined_vulns
                    for vuln in refined_vulns:
                        level = vuln.get("threat_level", "code quality issue").lower()
                        if level not in improved_security_output["threat_summary"]:
                            level = "code quality issue"
                        improved_security_output["threat_summary"][level] += 1

                # Update progress bar and label per batch
                current_batch = (batch_index // BATCH_SIZE) + 1
                progress_value = int((current_batch / total_batches) * 100)
                self.after(0, lambda val=progress_value: self.progress.config(value=val))
                self.after(0, lambda cur=current_batch, tot=total_batches: self.progress_label.config(text=f"Progress: {cur}/{tot}"))

            output_path = script_dir / IMPROVED_SECURITY_OUTPUT_FILE
            save_json(improved_security_output, output_path, "improved security vulnerabilities (second pass)")

            first_summary = security_report.get("threat_summary", {})
            improved_summary = improved_security_output.get("threat_summary", {})
            delta_summary = {}
            for key in improved_summary:
                delta = improved_summary[key] - first_summary.get(key, 0)
                # Format with a sign: e.g., "+5" or "-5"
                delta_summary[key] = f"{'+' if delta >= 0 else ''}{delta}"

            # Create a combined summary to display both improved summary and the delta changes
            final_summary = {
                "improved_summary": improved_summary,
                "changes": delta_summary
            }

            # Display the final summary in the text widget
            summary_text = json.dumps(final_summary, indent=4)
            self.after(0, lambda: self.summary_text.delete("1.0", tk.END))
            self.after(0, lambda: self.summary_text.insert(tk.END, summary_text))
            self.after(0, lambda: messagebox.showinfo("Success", f"Second pass completed.\nResults saved to:\n{output_path}"))
        except Exception as e:
            self.after(0, lambda: messagebox.showerror("Error", f"Second pass failed: {e}"))
        finally:
            self.after(0, lambda: self.first_pass_button.config(state="normal"))
            self.after(0, lambda: self.second_pass_button.config(state="normal"))

# For independent testing
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Security Scanner Tab Test")
    shared_vars = {
        'api_gemini_key': tk.StringVar(value="YOUR_API_KEY_HERE"),
        'repo_path_var': tk.StringVar(value="path_or_url_to_repo"),
        'repo_type_var': tk.StringVar(value='local')
    }
    tab = SecurityScannerTab(root, shared_vars)
    tab.pack(expand=True, fill='both')
    root.mainloop()
