# How to Update the Project Documentation

Our project uses **Sphinx** to generate documentation from source files written primarily in **reStructuredText (`.rst`)**. The documentation is hosted on **Read the Docs** and is automatically updated when changes are pushed to the main branch of our repository.

**Source Files Location:** All documentation source files are located within the `docs/` directory in the project root.

**When to Update Documentation:**

* When adding a new feature.
* When changing existing functionality.
* When fixing a bug that impacts usage or setup.
* When changing the API (update function/class docstrings).
* When adding or changing configuration options.
* When updating dependencies or installation procedures.

**Steps to Update Documentation:**

1.  **Set Up Local Environment (Recommended for Previewing):**
    * Ensure you have Python and `pip` installed.
    * Navigate to the project's root directory in your terminal.
    * Activate the project's virtual environment (e.g., `source venv/bin/activate` or `venv\Scripts\activate` on Windows).
    * Install documentation-specific dependencies:
        ```bash
        pip install -r docs/requirements.txt
        ```

2.  **Edit Documentation Files:**
    * Modify existing content by editing the relevant `.rst` files within the `docs/` directory (e.g., `docs/usage/gui.rst`).
    * Use reStructuredText syntax. Here's a quick primer: [Sphinx reStructuredText Primer](https://www.sphinx-doc.org/en/master/usage/restructuredtext/basics.html)

3.  **Add New Documentation Pages:**
    * Create a new `.rst` file in the appropriate subdirectory (e.g., `docs/usage/new_feature.rst`).
    * **Important:** Add the new file's name (without the extension) to the `toctree` directive in the corresponding `index.rst` file. For example, to add `new_feature.rst` to the Usage section, edit `docs/usage/index.rst` and add `new_feature` to the list under `.. toctree::`.

4.  **Update API Documentation:**
    * Our API documentation (in `docs/api/`) is generated automatically from docstrings in the Python source code (files in `app/`, `app/utils/`, etc.).
    * To update API docs, **edit the docstrings** directly within the relevant `.py` file(s). Follow the chosen docstring format (e.g., Google style).
    * Sphinx will pick up these changes during the build process (via `sphinx.ext.autodoc`).

5.  **Build Locally to Preview:**
    * From the **project root directory**, run the following command:
        ```bash
        sphinx-build -b html docs _build
        ```
    * This generates the HTML output in the `_build/html/` directory.
    * Open `_build/html/index.html` in your web browser to preview your changes locally. Check for formatting issues and ensure links work as expected.

6.  **Commit and Push Changes:**
    * Add the modified `.rst` files, any new `.rst` files, and any `.py` files with updated docstrings to your Git commit.
    * Commit the changes with a clear message.
    * Push your changes to the repository (e.g., to your feature branch for a pull request, or directly to the main branch if that's your workflow).

7.  **Automatic Deployment:**
    * Once your changes are merged into the main branch, Read the Docs will automatically detect the push, rebuild the documentation using the latest source from the `docs/` directory, and deploy the updated version to the live documentation site.

---

**Simple Example: Adding a Configuration Detail**

Let's say you added a new setting to `config/settings.py` called `NEW_SETTING` and you want to document it.

1.  **Edit:** Open the file `docs/usage/configuration.rst`.
2.  **Add Content:** Find the appropriate place (e.g., under the description of `config/settings.py`) and add details about the new setting using reStructuredText:

    ```rst
    * **``NEW_SETTING``:** Controls the behavior of [explain what it does]. Defaults to ``True``. Set this to ``False`` if [explain when to disable].
    ```

3.  **Build Locally (Optional):** Run `sphinx-build -b html docs _build` from the project root and open `_build/html/usage/configuration.html` to check formatting.
4.  **Commit & Push:** Commit the changes to `docs/usage/configuration.rst` and push. Read the Docs will rebuild the live site.
