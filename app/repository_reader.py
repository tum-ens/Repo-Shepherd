import os
import glob

def read_repository(repo_path):
    files = glob.glob(os.path.join(repo_path, '*.py'))
    scripts = {}
    for file in files:
        with open(file, 'r') as f:
            scripts[file] = f.read()
    return scripts