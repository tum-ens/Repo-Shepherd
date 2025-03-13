import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
import shutil
import tempfile
import google.generativeai as genai
import logging
import sys
import os

# Add path to utils directory
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../utils')))

from app.utils.utils import (
    setup_logging,
    configure_genai_api,
    get_local_repo_path,
    get_remote_repo_url,
    clone_remote_repo,
    convert_file_to_txt,
    upload_file_to_gemini
)

class SecurityGeneratorTab(ttk.Frame):
    def __init__(self, parent, shared_vars):
        super().__init__(parent)
        self.shared_vars = shared_vars
        self.grid(row=0, column=0, sticky='nsew')

        self.model_name = "gemini-1.5-flash"
        self.log_file_path = Path(__file__).parent.parent / "security_generator.log"

        # Shared variables for repository path and type
        self.repo_path_var = shared_vars.get('repo_path_var', tk.StringVar())
        self.repo_type_var = shared_vars.get('repo_type_var', tk.StringVar(value='local'))

        # Contact fields (always visible)
        # We'll still use StringVar for potential other uses but we will read directly from the Entry widgets.
        self.contact_name_var = tk.StringVar()
        self.contact_email_var = tk.StringVar()

        self.create_widgets()
        self.setup_logging()

    def setup_logging(self):
        setup_logging(self.log_file_path)

    def create_widgets(self):
        self.main_frame = ttk.Frame(self, padding="20")
        self.main_frame.pack(expand=True, fill='both')

        # Title
        title_label = ttk.Label(self.main_frame, text="Security.md Generator", font=("Helvetica", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=10)

        # Repository type radio buttons (local/remote)
        repo_type_frame = ttk.Frame(self.main_frame)
        repo_type_frame.grid(row=1, column=0, columnspan=3, pady=5, sticky='ew')
        local_radio = ttk.Radiobutton(
            repo_type_frame, text="Local Repository",
            variable=self.repo_type_var, value='local',
            command=lambda: self.set_repo_type('local')
        )
        local_radio.pack(side=tk.LEFT, padx=10)
        remote_radio = ttk.Radiobutton(
            repo_type_frame, text="Remote Repository",
            variable=self.repo_type_var, value='remote',
            command=lambda: self.set_repo_type('remote')
        )
        remote_radio.pack(side=tk.LEFT, padx=10)

        # Repository path entry and browse button
        self.repo_path_label = ttk.Label(self.main_frame, text="Local Repository Path:")
        self.repo_path_label.grid(row=2, column=0, sticky='w', padx=10, pady=5)
        self.repo_path_entry = ttk.Entry(self.main_frame, textvariable=self.repo_path_var, width=50)
        self.repo_path_entry.grid(row=2, column=1, sticky='ew', padx=10, pady=5)
        self.browse_button = ttk.Button(self.main_frame, text="Browse", command=self.browse_local_repo)
        self.browse_button.grid(row=2, column=2, padx=5, pady=5)

        # Dropdown for Report Vulnerability Via
        report_via_label = ttk.Label(self.main_frame, text="Report Vulnerability Via:")
        report_via_label.grid(row=3, column=0, sticky='w', padx=10, pady=5)
        self.report_via_combo = ttk.Combobox(
            self.main_frame,
            values=["Only With Issues", "Email", "Website Form", "Slack", "Other"],
            state="readonly"
        )
        self.report_via_combo.grid(row=3, column=1, sticky='ew', padx=10, pady=5)

        # Disclosure Policy Time dropdown
        disclosure_time_label = ttk.Label(self.main_frame, text="Disclosure Policy Time:")
        disclosure_time_label.grid(row=4, column=0, sticky='w', padx=10, pady=5)
        self.disclosure_time_combo = ttk.Combobox(
            self.main_frame,
            values=["7 Days", "14 Days", "30 Days", "Custom"],
            state="readonly"
        )
        self.disclosure_time_combo.grid(row=4, column=1, sticky='ew', padx=10, pady=5)

        # Preferred Languages dropdown
        preferred_lang_label = ttk.Label(self.main_frame, text="Preferred Languages:")
        preferred_lang_label.grid(row=5, column=0, sticky='w', padx=10, pady=5)
        self.language_combo = ttk.Combobox(
            self.main_frame,
            values=["English*", "Spanish", "French", "German", "Other"],
            state="readonly"
        )
        self.language_combo.grid(row=5, column=1, sticky='ew', padx=10, pady=5)

        # Contact Information fields (always visible)
        contact_info_label = ttk.Label(
            self.main_frame,
            text="Contact Information (if left empty, README.md contact info will be used):"
        )
        contact_info_label.grid(row=6, column=0, columnspan=3, sticky='w', padx=10, pady=5)

        # Contact Name
        self.contact_name_label = ttk.Label(self.main_frame, text="Contact Name:")
        self.contact_name_label.grid(row=7, column=0, sticky='w', padx=10, pady=5)
        self.contact_name_entry = ttk.Entry(self.main_frame, textvariable=self.contact_name_var, width=50)
        self.contact_name_entry.grid(row=7, column=1, sticky='ew', padx=10, pady=5)

        # Contact Email
        self.contact_email_label = ttk.Label(self.main_frame, text="Contact Email:")
        self.contact_email_label.grid(row=8, column=0, sticky='w', padx=10, pady=5)
        self.contact_email_entry = ttk.Entry(self.main_frame, textvariable=self.contact_email_var, width=50)
        self.contact_email_entry.grid(row=8, column=1, sticky='ew', padx=10, pady=5)

        # Generate button and status label
        self.generate_button = ttk.Button(self.main_frame, text="Generate SECURITY.md", command=self.start_generation)
        self.generate_button.grid(row=9, column=0, columnspan=3, pady=20)
        self.status_label = ttk.Label(self.main_frame, text="", wraplength=400)
        self.status_label.grid(row=10, column=0, columnspan=3, pady=10)

    def set_repo_type(self, repo_type):
        self.repo_type_var.set(repo_type)
        self.update_repo_entry_label()

    def update_repo_entry_label(self):
        if self.repo_type_var.get() == 'local':
            self.repo_path_label.config(text="Local Repository Path:")
            self.browse_button.grid(row=2, column=2, padx=5, pady=5)
            self.repo_path_entry.config(state=tk.NORMAL)
        else:
            self.repo_path_label.config(text="Remote Repository URL:")
            self.browse_button.grid_forget()
            self.repo_path_entry.config(state=tk.NORMAL)

    def browse_local_repo(self):
        repo_path = filedialog.askdirectory()
        if repo_path:
            self.repo_path_var.set(repo_path)

    def start_generation(self):
        # Read values directly from the Entry widgets (like the remote repo URL field)
        repo_input = self.repo_path_entry.get().strip()
        if not repo_input:
            messagebox.showerror("Error", "Please enter a repository path or URL.")
            return

        report_via_value = self.report_via_combo.get()
        disclosure_time_value = self.disclosure_time_combo.get()
        language_value = self.language_combo.get()
        contact_name = self.contact_name_entry.get()
        contact_email = self.contact_email_entry.get()

        print("DEBUG - Repo Path:", repo_input)
        print("DEBUG - Report Vulnerability Via:", report_via_value)
        print("DEBUG - Disclosure Policy Time:", disclosure_time_value)
        print("DEBUG - Preferred Languages:", language_value)
        print("DEBUG - Contact Name:", contact_name)
        print("DEBUG - Contact Email:", contact_email)

        repo_type = self.repo_type_var.get()
        if repo_type == 'local':
            try:
                repo_path = get_local_repo_path(repo_input)
            except (FileNotFoundError, NotADirectoryError) as e:
                messagebox.showerror("Error", str(e))
                return
            repo_selection_info = {'type': 'local', 'path': repo_path}
        else:
            if not (repo_input.startswith("https://github.com/") or repo_input.startswith("git@github.com:")):
                messagebox.showerror("Error", "Invalid GitHub URL. Please enter a valid GitHub repository URL.")
                return
            try:
                repo_url = get_remote_repo_url(repo_input)
            except ValueError as e:
                messagebox.showerror("Error", str(e))
                return
            repo_selection_info = {'type': 'remote', 'url': repo_url}

        self.status_label.config(text="Generating SECURITY.md, please wait...", foreground="blue")
        self.master.config(cursor="wait")

        repo_selection_info['report_via'] = report_via_value
        repo_selection_info['disclosure_time'] = disclosure_time_value
        repo_selection_info['language'] = language_value

        self.after(100, lambda: self._generate_security_md_async(repo_selection_info))

    def _generate_security_md_async(self, repo_selection_info):
        try:
            content = self.generate_security_md_process(repo_selection_info)
            if content:
                self.save_security_md(content, repo_selection_info['type'])
                self.status_label.config(text="SECURITY.md generated successfully!", foreground="green")
            else:
                self.status_label.config(text="SECURITY.md generation failed.", foreground="red")
        except Exception as e:
            logging.error("Error during SECURITY.md generation: %s", e)
            self.status_label.config(text=f"Error generating SECURITY.md: {e}", foreground="red")
            messagebox.showerror("Error", f"SECURITY.md generation error: {e}")
        finally:
            self.master.config(cursor="")

    def generate_security_md_process(self, repo_selection_info):
        API_KEY = self.shared_vars.get('api_gemini_key', tk.StringVar()).get()
        MODEL_NAME = self.model_name

        # Read contact information directly from the Entry widgets.
        contact_name = self.contact_name_entry.get().strip()
        contact_email = self.contact_email_entry.get().strip()

        if not contact_name and not contact_email:
            custom_contact_info = "Using contact information provided in README.md.\n"
        else:
            custom_contact_info = (
                f"Contact Name: {contact_name}\n"
                f"Contact Email: {contact_email}\n"
            )

        report_via_value = repo_selection_info.get('report_via', "Unknown")
        disclosure_time_value = repo_selection_info.get('disclosure_time', "Unknown")
        language_value = repo_selection_info.get('language', "Unknown")

        PROMPT = (
           
            

            "I am working on creating a `SECURITY.md` file for my GitHub repository. I want you to create a `SECURITY.md` "
            "that follows the sections below and uses information from the `README.md` file. Ensure that all website links are "
            "formatted in Markdown as \"[text...](http://...)\". The output should be in Markdown.\n\n"
            "Below are some custom selections from the user:\n\n"
            f"- Report Vulnerability Via: {report_via_value}\n"
            f"- Disclosure Policy Time: {disclosure_time_value}\n"
            f"- Preferred Languages: {language_value}\n"
            f"- Contact Info Setup:\n{custom_contact_info}\n"

            "## Summary\nProvide a brief overview of the security policy and its importance to the project.\n\n"
            "## Reporting Vulnerabilities\nPlease report security vulnerabilities through {report_via_value}. "
            "\n- Contact the [security team](mailto:security@example.com) via email.\n\n"
            "**Please include as much of the information listed below as possible to help us better understand and resolve the issue:**\n\n"
            "- **Type of issue:** (e.g., buffer overflow, SQL injection, cross-site scripting)\n"
            "- **Affected version(s):**\n"
            "- **Impact of the issue:** Including how an attacker might exploit the issue\n"
            "- **Step-by-step instructions to reproduce the issue:**\n"
            "- **Location of the affected source code:** (tag/branch/commit or direct URL)\n"
            "- **Full paths of source file(s) related to the issue:**\n"
            "- **Configuration required to reproduce the issue:**\n"
            "- **Log files related to the issue:** (if possible)\n"
            "- **Proof-of-concept or exploit code:** (if possible)\n\n"
            "## Disclosure Policy\nWe follow a responsible disclosure policy. Upon receiving a vulnerability report, we will acknowledge it within {disclosure_time_value} days and work to resolve the issue within two weeks. Details of fixed vulnerabilities will be publicly disclosed once the fix is released.\n\n"
            "## Preferred Languages\nWe prefer all communications to be in English.\n\n"
            "## License\nInclude the license information from the `README.md`."

            "As a output just write `SECURITY.md` file with the above content"

        )

        if repo_selection_info['type'] == 'local':
            repo_path = repo_selection_info['path']
        else:
            repo_url = repo_selection_info['url']
            repo_path = clone_remote_repo(repo_url)
            self.temp_clone_repo = repo_path

        README_PATH = repo_path / "README.md"
        LICENSE_PATH = repo_path / "LICENSE"

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_dir = Path(temp_dir)
            readme_txt_path = temp_dir / "README.txt"
            license_txt_path = temp_dir / "LICENSE.txt"

            convert_file_to_txt(README_PATH, readme_txt_path)
            convert_file_to_txt(LICENSE_PATH, license_txt_path)

            configure_genai_api(API_KEY)
            readme_file = upload_file_to_gemini(readme_txt_path)
            license_file = upload_file_to_gemini(license_txt_path)

            return self.generate_security_md(readme_file, license_file, PROMPT, MODEL_NAME)

    def generate_security_md(self, readme_file, license_file, prompt, model_name):
        model = genai.GenerativeModel(model_name)
        inputs = [readme_file, "\n\n", license_file, "\n\n", prompt]
        response = model.generate_content(inputs)
        return response.text.strip()

    def save_security_md(self, content, repo_type):
        if repo_type == 'local':
            output_path = Path(self.repo_path_var.get()) / "SECURITY.md"
        else:
            output_path = Path(__file__).parent.parent / "SECURITY.md"

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)
        messagebox.showinfo("Success", f"SECURITY.md saved to: {output_path}")

        if repo_type == 'remote' and hasattr(self, 'temp_clone_repo'):
            try:
                shutil.rmtree(self.temp_clone_repo)
            except Exception as e:
                logging.warning("Failed to clean up temporary repository: %s", e)

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Security Generator Tab Test")
    shared_vars = {'api_gemini_key': tk.StringVar(value="YOUR_API_KEY_HERE")}
    tab = SecurityGeneratorTab(root, shared_vars)
    tab.pack(expand=True, fill='both')
    root.mainloop()
