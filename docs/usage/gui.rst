GUI Usage
=========

The application includes a Graphical User Interface (GUI) built with Tkinter and ttk.

Key GUI Components
------------------

Based on the files in `app/gui-dev/`:

* **Main Window (`app/gui-dev/main.py`):** Sets up the main application window with tabs for different functionalities.
* **Getting Started Tab (`app/gui-dev/getting_started.py`):** Provides an initial welcome screen and directs users to the setup.
* **Configuration Tab (`app/gui-dev/configuration.py`):** Allows users to configure API keys (like Gemini), select models (API-based or local like Ollama), and set the repository path. Includes validation for inputs.
* **Readme Automatic Tab (`app/gui-dev/readme_automatic.py`):** Provides functionality to automatically generate a README file, likely using LLM calls based on the repo content.
* **Readme Improvement Tab (`app/gui-dev/readme_improvement.py`):** Allows users to load an existing README, split it into sections, generate improvements for sections using an LLM, and export the result. Also includes features for manual content creation.
* **Commit Analyzer Tab (`app/gui-dev/commit_analyzer.py`):** Fetches current Git changes or historical commits, displays diffs, generates commit messages using an LLM, and allows committing and pushing.
* **Security Generator Tab (`app/gui-dev/security_generator.py`):** Helps create a `SECURITY.md` file by asking for reporting methods, disclosure policies, preferred languages, and contact info, then generates the file content.
* **Security Scanner Tab (`app/gui-dev/security_scanner_tab.py`):** Provides buttons to run security scans (First Pass, Second Pass) on the repository code, displays progress, and shows a summary of findings. It uses the main security scanning logic.
* **Gemini Chat Tab (`app/gui-dev/gemini_chat_tab.py`):** Allows users to chat with an AI assistant (Gemini) about the initialized repository context. Requires initialization which likely involves processing and uploading repo content.
* **Improve Structure Tab (`app/gui-dev/improve_structure_tab.py`):** Analyzes the project structure and suggests improvements based on popular templates (like Cookiecutter) using an LLM.

*(Add specific step-by-step instructions or screenshots from `app/guide/` for using each part of the GUI here.)*
