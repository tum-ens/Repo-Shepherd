# improve_structure_tab.py

import tkinter as tk
from tkinter import ttk, messagebox
import threading
import tempfile
import shutil
from pathlib import Path
import google.generativeai as genai

# Import your utility functions from utils/utils.py
from utils.utils import (
    get_local_repo_path,
    clone_remote_repo,
    convert_repo_to_txt,
    configure_genai_api,
    upload_file_to_gemini
)

class ImproveStructureTab(ttk.Frame):
    def __init__(self, parent, shared_vars):
        super().__init__(parent)
        self.shared_vars = shared_vars
        self.create_widgets()

    def create_widgets(self):
        # Main frame for layout and padding
        self.main_frame = ttk.Frame(self, padding="20")
        self.main_frame.pack(expand=True, fill="both")

        # Title label
        title_label = ttk.Label(
            self.main_frame,
            text="Improve Project Structure",
            font=("Helvetica", 16, "bold")
        )
        title_label.grid(row=0, column=0, columnspan=2, pady=10)

        # Button to start the improvement process
        self.improve_button = ttk.Button(
            self.main_frame,
            text="Improve Structure",
            command=self.run_improvement
        )
        self.improve_button.grid(row=1, column=0, columnspan=2, pady=10)

        # Status label to display progress or errors
        self.status_label = ttk.Label(self.main_frame, text="", wraplength=400, foreground="black")
        self.status_label.grid(row=2, column=0, columnspan=2, pady=10)

        # Text widget to display the improved project structure
        self.output_text = tk.Text(self.main_frame, height=12, wrap="word")
        self.output_text.grid(row=3, column=0, columnspan=2, pady=10, sticky="nsew")

        # Allow the text widget to expand
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(3, weight=1)

    def run_improvement(self):
        # Capture shared variables in the main thread
        repo_input = self.shared_vars.get("repo_path_var").get().strip()
        repo_type = self.shared_vars.get("repo_type_var").get()
        api_key = self.shared_vars.get("api_gemini_key").get().strip()

        # Disable the button and update the status label
        self.improve_button.config(state="disabled")
        self.status_label.config(text="Improving project structure, please wait...", foreground="blue")

        # Start the heavy work in a background thread, passing captured variables
        threading.Thread(
            target=self.improve_structure_thread,
            args=(repo_input, repo_type, api_key),
            daemon=True
        ).start()

    def improve_structure_thread(self, repo_input, repo_type, api_key):
        try:
            if not repo_input:
                raise ValueError("Repository path/URL is not set.")
            if not api_key:
                raise ValueError("API key is not set.")

            # Determine local or remote repository
            if repo_type == "local":
                repo_path = get_local_repo_path(repo_input)
            else:
                repo_path = clone_remote_repo(repo_input)

            # Convert repository to text in a temporary directory
            with tempfile.TemporaryDirectory() as temp_dir_name:
                temp_dir = Path(temp_dir_name)
                output_txt_path = temp_dir / "repo_content.txt"
                convert_repo_to_txt(repo_path, output_txt_path)

                # Configure the Gemini API
                configure_genai_api(api_key)

                # Upload the converted repo text file to Gemini
                uploaded_file = upload_file_to_gemini(output_txt_path)

                # Define the prompt for Gemini (adjust as needed)
                prompt = (
                    """" 
I am working on improving the project structure of a GitLab repository. I want you to check the following templates for different projects and choose the best one for my repository. Please provide an improved file tree and project structure according to the chosen template.

### Available Templates:

1. Cookiecutter Data Science
Purpose: Standardized structure for data science projects.

File Tree:

├── data
│   ├── external
│   ├── interim
│   ├── processed
│   └── raw
├── notebooks
├── references
├── reports
│   └── figures
├── src
│   ├── data
│   ├── features
│   ├── models
│   └── visualization
├── tests
├── .gitignore
├── README.md
└── environment.yml
2. Cookiecutter Django
Purpose: Django web application with best practices.

File Tree:

├── config
│   ├── settings
│   ├── urls.py
│   └── wsgi.py
├── apps
│   └── [app_name]
├── static
├── templates
├── tests
├── manage.py
├── requirements.txt
├── .env
└── README.md
3. Cookiecutter Flask
Purpose: Flask web application with modular structure.

File Tree:

├── app
│   ├── templates
│   ├── static
│   ├── routes.py
│   ├── models.py
│   └── __init__.py
├── tests
├── migrations
├── config.py
├── requirements.txt
├── run.py
├── .env
└── README.md
4. Cookiecutter PyPackage
Purpose: Python package template for library development.

File Tree:

├── src
│   └── [package_name]
│       ├── __init__.py
│       └── module.py
├── tests
│   └── test_module.py
├── docs
├── .gitignore
├── LICENSE
├── README.md
├── setup.py
├── setup.cfg
└── requirements.txt
5. Cookiecutter FastAPI
Purpose: FastAPI application setup with best practices.

File Tree:

├── app
│   ├── api
│   ├── core
│   ├── models
│   ├── routers
│   ├── schemas
│   └── main.py
├── tests
├── alembic
├── requirements.txt
├── .env
├── Dockerfile
└── README.md
6. Cookiecutter React
Purpose: React.js frontend application setup.

File Tree:

├── public
│   ├── index.html
│   └── favicon.ico
├── src
│   ├── components
│   ├── pages
│   ├── assets
│   ├── App.js
│   ├── index.js
│   └── styles.css
├── tests
├── .gitignore
├── package.json
├── webpack.config.js
└── README.md
7. Cookiecutter Node.js
Purpose: Node.js backend application with Express.

File Tree:

├── src
│   ├── controllers
│   ├── models
│   ├── routes
│   ├── middlewares
│   └── app.js
├── tests
├── config
│   └── default.json
├── .gitignore
├── package.json
├── package-lock.json
├── .env
└── README.md
8. Cookiecutter Vue
Purpose: Vue.js frontend application setup.

File Tree:

├── public
│   └── index.html
├── src
│   ├── assets
│   ├── components
│   ├── views
│   ├── router
│   ├── store
│   ├── App.vue
│   └── main.js
├── tests
├── .gitignore
├── package.json
├── vue.config.js
└── README.md
9. Cookiecutter Spring Boot
Purpose: Spring Boot Java application setup.

File Tree:

├── src
│   ├── main
│   │   ├── java
│   │   │   └── com
│   │   │       └── example
│   │   │           └── [app_name]
│   │   │               ├── controllers
│   │   │               ├── models
│   │   │               ├── repositories
│   │   │               └── Application.java
│   │   └── resources
│   │       ├── application.properties
│   │       └── templates
│   └── test
│       └── java
│           └── com
│               └── example
│                   └── [app_name]
│                       └── ApplicationTests.java
├── .gitignore
├── pom.xml
├── README.md
└── Dockerfile
10. Cookiecutter Angular
Purpose: Angular frontend application setup.

File Tree:

├── e2e
├── src
│   ├── app
│   │   ├── components
│   │   ├── services
│   │   ├── app.module.ts
│   │   └── app.component.ts
│   ├── assets
│   ├── environments
│   ├── index.html
│   └── styles.css
├── .gitignore
├── angular.json
├── package.json
├── tsconfig.json
└── README.md
11. Cookiecutter Ruby on Rails
Purpose: Ruby on Rails web application setup.

File Tree:

├── app
│   ├── controllers
│   ├── models
│   ├── views
│   ├── helpers
│   ├── assets
│   └── mailers
├── config
│   ├── environments
│   ├── initializers
│   ├── locales
│   └── routes.rb
├── db
│   ├── migrate
│   └── seeds.rb
├── spec
├── log
├── tmp
├── public
├── Gemfile
├── Rakefile
├── config.ru
└── README.md
12. Cookiecutter Express
Purpose: Express.js backend application with MVC structure.

File Tree:

├── src
│   ├── controllers
│   ├── models
│   ├── routes
│   ├── views
│   ├── middlewares
│   └── app.js
├── config
│   └── default.json
├── tests
├── public
├── .gitignore
├── package.json
├── package-lock.json
├── .env
└── README.md
13. Cookiecutter Go
Purpose: Go application with modular structure.

File Tree:

├── cmd
│   └── [app_name]
│       └── main.go
├── pkg
│   └── [package]
├── internal
│   └── [module]
├── api
├── configs
├── scripts
├── tests
├── .gitignore
├── go.mod
├── go.sum
└── README.md
14. Cookiecutter Electron
Purpose: Electron desktop application setup.

File Tree:

├── src
│   ├── main.js
│   ├── renderer.js
│   ├── index.html
│   └── styles.css
├── assets
├── tests
├── .gitignore
├── package.json
├── webpack.config.js
├── main.js
└── README.md
15. Cookiecutter Laravel
Purpose: Laravel PHP framework application setup.

File Tree:

├── app
│   ├── Console
│   ├── Exceptions
│   ├── Http
│   ├── Models
│   └── Providers
├── bootstrap
├── config
├── database
│   ├── factories
│   ├── migrations
│   └── seeders
├── public
├── resources
│   ├── js
│   ├── lang
│   └── views
├── routes
├── storage
├── tests
├── .env
├── artisan
├── composer.json
├── package.json
└── README.md
16. Cookiecutter Svelte
Purpose: Svelte.js frontend application setup.

File Tree:

├── public
│   ├── index.html
│   └── global.css
├── src
│   ├── components
│   ├── routes
│   ├── stores
│   ├── App.svelte
│   └── main.js
├── tests
├── .gitignore
├── package.json
├── rollup.config.js
└── README.md
17. Cookiecutter Spark
Purpose: Apache Spark project setup.

File Tree:

├── src
│   ├── main
│   │   └── scala
│   │       └── [project_name]
│   │           └── App.scala
│   └── test
│       └── scala
│           └── [project_name]
│               └── AppTest.scala
├── data
├── notebooks
├── config
├── scripts
├── .gitignore
├── build.sbt
├── README.md
└── requirements.txt
18. Cookiecutter Hugo
Purpose: Hugo static site generator setup.

File Tree:

├── archetypes
├── content
│   ├── posts
│   └── about.md
├── layouts
│   ├── _default
│   ├── partials
│   └── index.html
├── static
│   ├── css
│   ├── js
│   └── images
├── themes
├── config.toml
├── .gitignore
└── README.md
19. Cookiecutter Jupyter
Purpose: Jupyter Notebook project setup.

File Tree:

├── notebooks
│   ├── 01_data_cleaning.ipynb
│   ├── 02_exploratory_analysis.ipynb
│   └── 03_modeling.ipynb
├── data
│   ├── raw
│   ├── processed
│   └── external
├── scripts
│   ├── data_cleaning.py
│   └── modeling.py
├── reports
│   └── figures
├── environment.yml
├── requirements.txt
├── .gitignore
└── README.md
20. Cookiecutter Sparkly
Purpose: Sparklyr (R) project setup for Apache Spark.

File Tree:
├── R
│   ├── app.R
│   ├── helpers.R
│   └── models.R
├── data
│   ├── raw
│   └── processed
├── tests
│   └── test_app.R
├── scripts
│   └── deploy.R
├── .gitignore
├── DESCRIPTION
├── NAMESPACE
├── README.md
└── LICENSE

**Output Requirement:**
Please only provide the title of the chosen template and the improved file structure with explanations, nothing else.
"""
                )

                # --- Gemini Model Call on Main Thread ---
                # Schedule the Gemini call on the main thread to avoid threading issues.
                self.after(0, lambda: self.generate_improvement_immediately(uploaded_file, prompt))
        except Exception as e:
            # Schedule error UI updates on the main thread
            self.after(0, lambda err=e: self.show_error(err))
            self.after(0, lambda: self.improve_button.config(state="normal"))

    def generate_improvement_immediately(self, uploaded_file, prompt):
        try:
            # Check the shared variable for default model selection.
            shared_model = self.shared_vars.get("default_gemini_model").get()
            if shared_model.lower() == "auto":
                model_to_use = "gemini-2.0-flash-thinking-exp-01-21"
            else:
                model_to_use = shared_model

            debug_message = f"DEBUG: Using model -> {model_to_use}"
            print(debug_message)
            self.status_label.config(text=debug_message, foreground="purple")

            model = genai.GenerativeModel(model_to_use)
            inputs = [uploaded_file, "\n\n", prompt]
            response = model.generate_content(inputs)
            improved_structure = response.text.strip()
        except Exception as e:
            self.show_error(e)
            self.improve_button.config(state="normal")
            return

        # Save the improved structure to a file in the same directory as this tab's module
        try:
            script_dir = Path(__file__).parent
            structure_path = script_dir / "suggested_project_structure.md"
            backup_path = script_dir / "PROJECT_STRUCTURE_backup.md"

            if structure_path.exists():
                shutil.copy(structure_path, backup_path)
            with open(structure_path, 'w', encoding='utf-8') as f:
                f.write(improved_structure)
        except Exception as file_err:
            self.show_error(file_err)
            self.improve_button.config(state="normal")
            return

        self.show_success(improved_structure)
        self.improve_button.config(state="normal")

    def show_error(self, err):
        self.status_label.config(text=f"Error: {err}", foreground="red")
        messagebox.showerror("Error", str(err))

    def show_success(self, structure):
        self.status_label.config(text="Project structure improved successfully!", foreground="green")
        self.output_text.delete("1.0", tk.END)
        self.output_text.insert(tk.END, structure)
