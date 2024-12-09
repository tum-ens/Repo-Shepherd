import os

def create_directory_structure(base_dir):
    """
    Creates a predefined directory structure with specified files within a given base directory.
    Args:
        base_dir (str): The base directory where the directory structure will be created.
    The function creates the following directories and files:
        - app: ["__init__.py", "main.py", "repository_reader.py", "llm_handler.py", "documentation_generator.py"]
        - config: ["__init__.py", "settings.py"]
        - data: ["temp_db.sqlite", "config_db.sqlite"]
        - docker: ["Dockerfile", "docker-compose.yml"]
        - tests: ["__init__.py", "test_main.py", "test_repository_reader.py", "test_llm_handler.py", "test_llm_orchestrator.py", "test_documentation_generator.py"]
        - root: ["README.md", "requirements.txt", ".gitignore"]
    If the directories or files already exist, they will not be recreated or overwritten.
    Prints:
        A message indicating the directory structure has been created at the specified base directory.
    """

    directories = [
        "app",
        "config",
        "data",
        "docker",
        "tests"
    ]
    files = {
        "app": ["__init__.py", "main.py", "repository_reader.py", "llm_handler.py", "documentation_generator.py"],
        "config": ["__init__.py", "settings.py"],
        "data": ["temp_db.sqlite", "config_db.sqlite"],
        "docker": ["Dockerfile", "docker-compose.yml"],
        "tests": ["__init__.py", "test_main.py", "test_repository_reader.py", "test_llm_handler.py", "test_llm_orchestrator.py", "test_documentation_generator.py"],
        "": ["README.md", "requirements.txt", ".gitignore"]
    }
    
    for directory in directories:
        os.makedirs(os.path.join(base_dir, directory), exist_ok=True)

    for directory, filenames in files.items():
        for filename in filenames:
            open(os.path.join(base_dir, directory, filename), 'w').close()

    print(f"Directory structure created at: {base_dir}")

if __name__ == "__main__":
    create_directory_structure("")

