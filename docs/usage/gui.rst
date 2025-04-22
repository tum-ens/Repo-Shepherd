GUI Usage
=========

The application includes a Graphical User Interface (GUI) built with Tkinter and ttk.

Key GUI Components
------------------

Based on the files in `app/gui/`:

* **Main Window (`app/gui/main.py`):** Sets up the main application window with tabs for different functionalities.
* **Getting Started Tab (`app/gui/getting_started.py`):** Provides an initial welcome screen and directs users to the setup.
* **Configuration Tab (`app/gui/configuration.py`):** Allows users to configure API keys (like Gemini), select models (API-based or local like Ollama), and set the repository path. Includes validation for inputs.
* **Readme Automatic Tab (`app/gui/readme_automatic.py`):** Provides functionality to automatically generate a README file, likely using LLM calls based on the repo content.
* **Readme Improvement Tab (`app/gui/readme_improvement.py`):** Allows users to load an existing README, split it into sections, generate improvements for sections using an LLM, and export the result. Also includes features for manual content creation.
* **Commit Analyzer Tab (`app/gui/commit_analyzer.py`):** Fetches current Git changes or historical commits, displays diffs, generates commit messages using an LLM, and allows committing and pushing.
* **Security Generator Tab (`app/gui/security_generator.py`):** Helps create a `SECURITY.md` file by asking for reporting methods, disclosure policies, preferred languages, and contact info, then generates the file content.
* **Security Scanner Tab (`app/gui/security_scanner_tab.py`):** Provides buttons to run security scans (First Pass, Second Pass) on the repository code, displays progress, and shows a summary of findings. It uses the main security scanning logic.
* **Gemini Chat Tab (`app/gui/gemini_chat_tab.py`):** Allows users to chat with an AI assistant (Gemini) about the initialized repository context. Requires initialization which likely involves processing and uploading repo content.
* **Improve Structure Tab (`app/gui/improve_structure_tab.py`):** Analyzes the project structure and suggests improvements based on popular templates (like Cookiecutter) using an LLM.
