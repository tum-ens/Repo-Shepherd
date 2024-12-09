import json
import os

class DocumentationGenerator:
    def __init__(self, llm_response, output_dir):
        self.llm_response = llm_response
        self.output_dir = output_dir

    def generate_docs(self):
        """
        Parses the LLM response and generates documentation files.
        """
        # Parse the LLM response (assuming it's in JSON format)
        response_data = json.loads(self.llm_response)

        # Generate README.md
        readme_content = self._generate_readme(response_data)
        self._write_file('README.md', readme_content)

        # Generate other documentation files as needed
        other_docs = self._generate_other_docs(response_data)
        for filename, content in other_docs.items():
            self._write_file(filename, content)

    def _generate_readme(self, data):
        """
        Generates the content for README.md based on the parsed data.
        """
        readme_content = f"# {data['project_name']}\n\n"
        readme_content += f"{data['description']}\n\n"
        readme_content += "## Installation\n\n"
        readme_content += f"{data['installation']}\n\n"
        readme_content += "## Usage\n\n"
        readme_content += f"{data['usage']}\n\n"
        return readme_content

    def _generate_other_docs(self, data):
        """
        Generates content for other documentation files based on the parsed data.
        """
        other_docs = {}
        for doc in data.get('other_docs', []):
            filename = doc['filename']
            content = doc['content']
            other_docs[filename] = content
        return other_docs

    def _write_file(self, filename, content):
        """
        Writes the content to a file in the output directory.
        """
        file_path = os.path.join(self.output_dir, filename)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)

# Example usage
llm_response = '{"project_name": "My Project", "description": "This is a sample project.", "installation": "pip install my_project", "usage": "import my_project", "other_docs": [{"filename": "CONTRIBUTING.md", "content": "Contribution guidelines."}]}'
output_dir = './docs'
generator = DocumentationGenerator(llm_response, output_dir)
generator.generate_docs()
