# --- START OF FILE security_scanner_tab.py ---

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
# Assuming the scanner module is in the 'app' directory relative to where main.py runs
try:
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
        MODEL_NAME, # Default model for first pass
        SECOND_PASS_MODEL, # Default model for second pass
        upload_file_to_gemini,
        BATCH_SIZE,
    )
except ImportError:
    # Fallback for running this script directly if needed, adjust path as necessary
    import security_scanner_gemini_all_code_withsecondpass as scanner
    from security_scanner_gemini_all_code_withsecondpass import (
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
        # Description label for the tab
        desc_text = (
            "This tab scans your repository to detect potential vulnerabilities.\n\n"
            "• First Pass: Performs an initial scan of all code files and generates a preliminary report "
            "with detected vulnerabilities and a threat summary.\n"
            "• Second Pass: Refines the first pass report by reanalyzing the findings with additional "
            "context from your repository, resulting in an improved and more accurate vulnerability report and a threat summary."
        )
        desc_label = ttk.Label(self, text=desc_text, wraplength=500, justify="left")
        desc_label.pack(pady=(0, 10))

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
        selected_model = self.shared_vars.get("default_gemini_model").get().strip() # Get selected model

        # Disable buttons and reset progress bar and label
        self.first_pass_button.config(state="disabled")
        self.second_pass_button.config(state="disabled")
        self.progress.config(value=0)
        self.progress_label.config(text="Progress: 0/0")

        # Start the background thread with the captured values
        threading.Thread(
            target=self.first_pass_thread,
            args=(repo_input, repo_type, api_key, selected_model), # Pass selected_model
            daemon=True
        ).start()

    def first_pass_thread(self, repo_input, repo_type, api_key, selected_model):
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

            # Configure Gemini API
            configure_genai_api(api_key)

            # Determine the model name to use for the first pass
            first_pass_model_name = MODEL_NAME # Default from scanner module
            if selected_model and selected_model.lower() != "auto":
                first_pass_model_name = selected_model
                print(f"Security Scanner (Pass 1): Using selected model '{first_pass_model_name}'") # Optional logging
            else:
                print(f"Security Scanner (Pass 1): Using default model '{first_pass_model_name}'") # Optional logging

            # Initialize the model for first pass analysis
            gemini_model = genai.GenerativeModel(first_pass_model_name)
            # Set the module-level model in scanner if functions rely on it
            # (Check if scanner.generate_security_report uses a global or passed model)
            # If generate_security_report uses a global model set in scanner, uncomment the next line
            # scanner.gemini_model = gemini_model

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
                    # Pass the initialized gemini_model explicitly
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
                        # Handle unexpected response format (e.g., error dict)
                        security_output[relative_file_path] = vulnerabilities
                except Exception as e:
                    security_output[relative_file_path] = {"error": f"Failed to analyze: {e}"}

                # Update progress bar and label
                progress_value = int((idx / total_files) * 100)
                self.after(0, lambda val=progress_value: self.progress.config(value=val))
                self.after(0, lambda cur=idx, tot=total_files: self.progress_label.config(text=f"Progress: {cur}/{tot}"))

            security_output["threat_summary"] = threat_summary

            # Save JSON output
            # Use Path(__file__).parent to ensure path is relative to this script
            script_dir = Path(__file__).resolve().parent
            output_path = script_dir / SECURITY_OUTPUT_FILE
            save_json(security_output, output_path, "security vulnerabilities (first pass)")

            summary_text = json.dumps(threat_summary, indent=4)
            self.after(0, lambda: self.summary_text.delete("1.0", tk.END))
            self.after(0, lambda: self.summary_text.insert(tk.END, summary_text))
            self.after(0, lambda: messagebox.showinfo("Success", f"First pass completed.\nvulnerability report to:\n{output_path}"))
        except Exception as e:
            self.after(0, lambda: messagebox.showerror("Error", f"First pass failed: {e}"))
        finally:
            # Ensure buttons are re-enabled in the main thread
            self.after(0, lambda: self.first_pass_button.config(state="normal"))
            self.after(0, lambda: self.second_pass_button.config(state="normal"))

    def run_second_pass(self):
        # Get necessary values in the main thread
        repo_input = self.shared_vars.get("repo_path_var").get().strip()
        repo_type = self.shared_vars.get("repo_type_var").get()
        api_key = self.shared_vars.get("api_gemini_key").get().strip()
        selected_model = self.shared_vars.get("default_gemini_model").get().strip() # Get selected model

        # Disable buttons and reset progress bar and label
        self.first_pass_button.config(state="disabled")
        self.second_pass_button.config(state="disabled")
        self.progress.config(value=0)
        self.progress_label.config(text="Progress: 0/0")

        threading.Thread(
            target=self.second_pass_thread,
            args=(repo_input, repo_type, api_key, selected_model), # Pass selected_model
            daemon=True
        ).start()

    def second_pass_thread(self, repo_input, repo_type, api_key, selected_model):
        try:
            # Use Path(__file__).parent to ensure path is relative to this script
            script_dir = Path(__file__).resolve().parent
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
                # Check if upload_file_to_gemini exists in scanner and use it
                if hasattr(scanner, 'upload_file_to_gemini'):
                     uploaded_repo = scanner.upload_file_to_gemini(repo_content_path)
                else: # Fallback if function not found or using older genai version
                     uploaded_repo = genai.upload_file(repo_content_path)
            except Exception as e:
                 # Attempt fallback or handle error
                 print(f"Warning: Failed to use scanner.upload_file_to_gemini, trying genai.upload_file. Error: {e}")
                 try:
                     uploaded_repo = genai.upload_file(repo_content_path)
                 except Exception as upload_err:
                     self.after(0, lambda: messagebox.showerror("Error", f"Failed to upload repo content to Gemini: {upload_err}"))
                     return


            # Configure Gemini API
            configure_genai_api(api_key)

            # Determine the model name to use for the second pass
            second_pass_model_name = SECOND_PASS_MODEL # Default from scanner module
            if selected_model and selected_model.lower() != "auto":
                second_pass_model_name = selected_model
                print(f"Security Scanner (Pass 2): Using selected model '{second_pass_model_name}'") # Optional logging
            else:
                print(f"Security Scanner (Pass 2): Using default model '{second_pass_model_name}'") # Optional logging

            # Initialize model for second pass refinement
            gemini_model_second = genai.GenerativeModel(second_pass_model_name)

            file_keys = [k for k in security_report.keys() if k != "threat_summary"]
            total_files = len(file_keys)
            total_batches = math.ceil(total_files / BATCH_SIZE) if BATCH_SIZE > 0 else 1
            improved_security_output = {"threat_summary": {
                "code quality issue": 0,
                "low": 0,
                "medium": 0,
                "high": 0,
                "critical": 0,
            }}

            # Update progress label for batches
            self.after(0, lambda: self.progress_label.config(text=f"Progress: 0/{total_batches}"))

            # Ensure BATCH_SIZE is positive to avoid infinite loop or division by zero
            current_batch_size = BATCH_SIZE if BATCH_SIZE > 0 else total_files if total_files > 0 else 1

            for batch_index in range(0, total_files, current_batch_size):
                batch_files = file_keys[batch_index: batch_index + current_batch_size]
                vulnerability_batch = {}
                for file_path in batch_files:
                    vulnerabilities = security_report.get(file_path, [])
                    # Ensure we only process actual vulnerability lists, not error dicts
                    if isinstance(vulnerabilities, list) and vulnerabilities:
                         vulnerability_batch[file_path] = vulnerabilities
                    elif isinstance(vulnerabilities, dict) and "error" in vulnerabilities:
                         improved_security_output[file_path] = vulnerabilities # Carry over errors
                    else:
                         improved_security_output[file_path] = [] # Handle empty lists or unexpected types


                # Only run refinement if there are vulnerabilities in the batch
                if vulnerability_batch:
                    try:
                        # Pass the initialized gemini_model_second explicitly
                        batch_result = refine_vulnerability_report_gemini_batch(
                            vulnerability_batch, repo_content, uploaded_repo, model=gemini_model_second
                        )
                        # Merge results back, handling potential errors from refinement
                        for file_path, refined_vulns in batch_result.items():
                             if file_path in batch_files: # Ensure result corresponds to request
                                 improved_security_output[file_path] = refined_vulns
                                 if isinstance(refined_vulns, list): # Only count threats if it's a list
                                    for vuln in refined_vulns:
                                        level = vuln.get("threat_level", "code quality issue").lower()
                                        if level not in improved_security_output["threat_summary"]:
                                            level = "code quality issue" # Default if key is missing/invalid
                                        improved_security_output["threat_summary"][level] += 1
                                 # else: handle potential error dicts from refinement if needed

                    except Exception as refine_err:
                         # Log error for the batch and potentially mark files as failed
                         print(f"Error refining batch starting with {batch_files[0]}: {refine_err}")
                         for file_path in batch_files:
                             if file_path in vulnerability_batch: # Only mark files that were attempted
                                 improved_security_output[file_path] = {"error": f"Refinement failed: {refine_err}"}


                # Update progress bar and label per batch
                current_batch_num = (batch_index // current_batch_size) + 1
                progress_value = int((current_batch_num / total_batches) * 100) if total_batches > 0 else 100
                self.after(0, lambda val=progress_value: self.progress.config(value=val))
                self.after(0, lambda cur=current_batch_num, tot=total_batches: self.progress_label.config(text=f"Progress: {cur}/{tot}"))

            output_path = script_dir / IMPROVED_SECURITY_OUTPUT_FILE
            save_json(improved_security_output, output_path, "improved security vulnerabilities (second pass)")

            first_summary = security_report.get("threat_summary", {})
            improved_summary = improved_security_output.get("threat_summary", {})
            delta_summary = {}
            # Calculate delta based on keys present in the improved summary
            all_keys = set(first_summary.keys()) | set(improved_summary.keys())
            for key in all_keys:
                delta = improved_summary.get(key, 0) - first_summary.get(key, 0)
                # Format with a sign: e.g., "+5" or "-5" or "0"
                delta_summary[key] = f"{'+' if delta >= 0 else ''}{delta}"


            # Create a combined summary to display both improved summary and the delta changes
            final_summary = {
                "improved_summary": improved_summary,
                "changes_from_first_pass": delta_summary
            }

            # Display the final summary in the text widget
            summary_text = json.dumps(final_summary, indent=4)
            self.after(0, lambda: self.summary_text.delete("1.0", tk.END))
            self.after(0, lambda: self.summary_text.insert(tk.END, summary_text))
            self.after(0, lambda: messagebox.showinfo("Success", f"Second pass completed.\nvulnerability report saved to:\n{output_path}"))
        except Exception as e:
            self.after(0, lambda: messagebox.showerror("Error", f"Second pass failed: {e}"))
        finally:
            # Ensure buttons are re-enabled in the main thread
            self.after(0, lambda: self.first_pass_button.config(state="normal"))
            self.after(0, lambda: self.second_pass_button.config(state="normal"))

# For independent testing
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Security Scanner Tab Test")

    # Example shared_vars for testing
    shared_vars_test = {
        'api_gemini_key': tk.StringVar(value="YOUR_API_KEY_HERE"), # Replace with a real key for actual testing
        'repo_path_var': tk.StringVar(value="."), # Example: current directory
        'repo_type_var': tk.StringVar(value='local'),
        'default_gemini_model': tk.StringVar(value="auto") # Test with "auto" or a specific model name like "gemini-1.5-flash"
    }

    # Add a way to change the model selection for testing
    model_frame = ttk.Frame(root)
    model_frame.pack(pady=5)
    ttk.Label(model_frame, text="Select Model:").pack(side=tk.LEFT, padx=5)
    model_options = ["auto", "gemini-1.5-flash", "gemini-1.0-pro", "gemini-pro"] # Add relevant model names
    model_combobox = ttk.Combobox(model_frame, textvariable=shared_vars_test['default_gemini_model'], values=model_options, state="readonly")
    model_combobox.pack(side=tk.LEFT)
    model_combobox.set(shared_vars_test['default_gemini_model'].get()) # Set initial value

    tab = SecurityScannerTab(root, shared_vars_test)
    tab.pack(expand=True, fill='both', padx=10, pady=10)
    root.mainloop()
# --- END OF FILE security_scanner_tab.py ---