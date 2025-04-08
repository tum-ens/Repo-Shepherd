app.utils Package
=================

Utility functions used across the application.

.. automodule:: app.utils
   :members:

Modules
-------

app.utils.utils
~~~~~~~~~~~~~~~
.. automodule:: app.utils.utils
   :members:
   :undoc-members:
   :show-inheritance:

   Provides common utility functions: logging setup (`setup_logging`), Gemini API configuration and validation (`configure_genai_api`, `validate_gemini_api_key`), repository path handling (`get_local_repo_path`, `get_remote_repo_url`, `clone_remote_repo`), repository-to-text conversion (`convert_repo_to_txt`), and file uploading (`upload_file_to_gemini`, `convert_file_to_txt`).

app.utils.commit_message
~~~~~~~~~~~~~~~~~~~~~~~~
.. automodule:: app.utils.commit_message
   :members:
   :undoc-members:
   :show-inheritance:

   Contains functions related to Git commit messages. Loads prompts from YAML and defines helper functions (`generate_general_prompt`, `extract_result`). Provides core functions `generate_CM` (generates a commit message from code diffs) and `improve_CM` (improves an existing commit message based on diffs) using an LLM API call (`llm_api.gemini_api`).

app.utils.creation
~~~~~~~~~~~~~~~~~~
.. automodule:: app.utils.creation
   :members:
   :undoc-members:
   :show-inheritance:

   Focuses on creating documentation content. Loads prompts from YAML (`creation_prompt.yaml`). `create_part` generates specific documentation sections (like description, usage, etc.) using an LLM based on provided info and file tree context. `create_feature` generates feature descriptions, potentially ensuring uniqueness against existing features. `structure_markdown` likely reorganizes generated markdown sections into a final document structure.

app.utils.file_tree
~~~~~~~~~~~~~~~~~~~
.. automodule:: app.utils.file_tree
   :members:
   :undoc-members:
   :show-inheritance:

   Contains `generate_file_tree`, a function to create a string representation of the repository's directory structure, controllable by depth and whether to show files.

app.utils.help_popup
~~~~~~~~~~~~~~~~~~~~
.. automodule:: app.utils.help_popup
   :members:
   :undoc-members:
   :show-inheritance:

   Provides a `HelpPopup` class using Tkinter to display an image (likely a guide or screenshot) in a separate window, useful for GUI help buttons.

app.utils.llm_api
~~~~~~~~~~~~~~~~~
.. automodule:: app.utils.llm_api
   :members:
   :undoc-members:
   :show-inheritance:

   Contains functions for interacting with different LLM APIs. Includes `gemini_api` for calls to Google Gemini (with rate-limiting sleep) and `together_api` for calls to the Together AI platform.

app.utils.repo_structure
~~~~~~~~~~~~~~~~~~~~~~~~
.. automodule:: app.utils.repo_structure
   :members:
   :undoc-members:
   :show-inheritance:

   Seems to combine functions also found elsewhere. Contains `generate_file_tree` (like `app.utils.file_tree`) and `get_repo_path`, `convert_repo_to_txt` (like `app.utils.utils`).

app.utils.toolkit
~~~~~~~~~~~~~~~~~
.. automodule:: app.utils.toolkit
   :members:
   :undoc-members:
   :show-inheritance:

   Provides GUI helper functions using Tkinter's `filedialog`, likely intended for use within the main GUI application. Includes `select_folder`, `select_file`, and `export_markdown` to save generated content.
