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
        self._write_file('README-TEST.md', readme_content)

        # Generate other documentation files as needed
        other_docs = self._generate_other_docs(response_data)
        for filename, content in other_docs.items():
            self._write_file(filename, content)

    def _generate_readme(self, data):
        """
        Generates the content for README.md based on the parsed data.
        """
        return str(data['response'])

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

        def extract_data_from_quotes(data):
            """
            Extracts the data within the outermost double quotes, 
            handling escaped quotes within the string.

            Args:
                data: The input string.

            Returns:
                The string without the outermost double quotes, or 
                the original string if no outer quotes are found.
            """
            import re
            match = re.match(r'^"(.*?)"$', data)
            if match:
                return match.group(1)
            else:
                return data
        
        extracted_data = extract_data_from_quotes(content) 

        file_path = os.path.join(self.output_dir, filename)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(extracted_data) 
        return f"Generated file: {file_path}"

