import os
import glob

import os 


class RepositoryReader:
    def __init__(self, repository_path):
        self.repository_path = repository_path

    def read_repository_files(self, repo_path):
        files = glob.glob(os.path.join(repo_path, '*.py'))
        scripts = {}
        for file in files:
            with open(file, 'r', encoding='utf-8') as f:
                scripts[file] = f.read()
        
        return scripts
    


    def read_code(self):
        """
        Reads Python code from the specified local repository path.
        """
        code = ""
        for root, _, files in os.walk(self.repository_path):
            for file in files:
                if file.endswith(".py"):
                    file_path = os.path.join(root, file)
                    with open(file_path, "r") as f:
                        code += f.read() + "\n"
        return code