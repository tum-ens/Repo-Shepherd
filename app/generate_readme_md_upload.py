import os
import sys
import logging
from pathlib import Path
import shutil
import tempfile
import google.generativeai as genai

# ------------------------------ Configuration ------------------------------

API_KEY = ""  # Replace with your actual Gemini API key
MODEL_NAME = "gemini-1.5-flash"   # Replace with your desired Gemini model

# ------------------------------ Logging Configuration ------------------------------

def setup_logging(log_file: Path):
    logging.basicConfig(
        filename=log_file,
        level=logging.INFO,
        format='%(asctime)s:%(levelname)s:%(message)s'
    )

# ------------------------------ Helper Functions ------------------------------

def get_repo_path() -> Path:
    """
    Prompts the user to input the repository folder path.
    Validates that the path exists and is a directory.
    """
    repo_path = input("Enter the path to your repository folder: ").strip()
    repo = Path(repo_path).resolve()
    if not repo.exists():
        logging.error(f"The path '{repo}' does not exist.")
        print(f"Error: The path '{repo}' does not exist.")
        sys.exit(1)
    if not repo.is_dir():
        logging.error(f"The path '{repo}' is not a directory.")
        print(f"Error: The path '{repo}' is not a directory.")
        sys.exit(1)
    logging.info(f"Repository path set to: {repo}")
    return repo

def convert_repo_to_txt(repo_path: Path, output_txt_path: Path):
    """
    Walks through the repository directory, captures the file tree,
    file names, and file contents, and writes them to a single .txt file.
    """
    try:
        with open(output_txt_path, 'w', encoding='utf-8') as txt_file:
            for root, dirs, files in os.walk(repo_path):
                # Write the directory path
                dir_path = Path(root).relative_to(repo_path)
                txt_file.write(f"\n### Directory: {dir_path}\n\n")
                
                for file in files:
                    file_path = Path(root) / file
                    relative_file_path = file_path.relative_to(repo_path)
                    
                    # Convert to .txt if necessary
                    if file_path.suffix and file_path.suffix.lower() != '.txt' and file_path.suffix.lower() not in ['.md', '.rst', '.py', '.js', '.java', '.cpp', '.c', '.json', '.yaml', '.yml', '.sh', '.rb', '.go', '.ts', '.html', '.css', '.xml', '.ini']:
                        # Skip non-text files based on extension
                        logging.info(f"Skipping non-text file: {relative_file_path}")
                        continue
                    
                    # Write the file name
                    txt_file.write(f"#### File: {relative_file_path}\n\n")
                    
                    # Read and write the file content
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        txt_file.write(content)
                        txt_file.write("\n\n")
                        logging.info(f"Added file to txt: {relative_file_path}")
                    except Exception as e:
                        logging.error(f"Failed to read file {relative_file_path}: {e}")
                        txt_file.write(f"<!-- Failed to read file: {e} -->\n\n")
        logging.info(f"Repository successfully converted to text at {output_txt_path}")
    except Exception as e:
        logging.error(f"Error converting repository to text: {e}")
        print(f"Error converting repository to text: {e}")
        sys.exit(1)

def configure_genai_api(api_key: str):
    """
    Configures the Google Gemini API with the provided API key.
    """
    try:
        genai.configure(api_key=api_key)
        logging.info("Successfully configured Google Gemini API.")
    except Exception as e:
        logging.error(f"Failed to configure Google Gemini API: {e}")
        print(f"Error configuring Google Gemini API: {e}")
        sys.exit(1)

def upload_file_to_gemini(file_path: Path):
    """
    Uploads the specified file to Google Gemini.
    Returns the uploaded file object.
    """
    try:
        uploaded_file = genai.upload_file(file_path)
        logging.info(f"Successfully uploaded file: {file_path.name}")
        return uploaded_file
    except Exception as e:
        logging.error(f"Failed to upload file {file_path.name}: {e}")
        print(f"Error uploading file {file_path.name}: {e}")
        sys.exit(1)

def generate_improved_readme(uploaded_file, prompt: str) -> str:
    """
    Uses Google Gemini to generate an improved README.md based on the prompt.
    Returns the improved README.md content.
    """
    try:
        model = genai.GenerativeModel(MODEL_NAME)
        logging.info(f"Initialized model: {MODEL_NAME}")

        inputs = [
            uploaded_file,
            "\n\n",
            prompt
        ]

        response = model.generate_content(inputs)
        improved_readme = response.text.strip()
        logging.info("Successfully generated improved README.md content.")
        return improved_readme
    except Exception as e:
        logging.error(f"Failed to generate improved README.md: {e}")
        print(f"Error generating improved README.md: {e}")
        sys.exit(1)

def save_improved_readme(repo_path: Path, content: str):
    """
    Saves the improved README.md content to the repository.
    Backs up the original README.md before overwriting.
    """
    readme_path = repo_path / "README.md"
    backup_path = repo_path / "README_backup.md"

    try:
        if readme_path.exists():
            shutil.copy(readme_path, backup_path)
            logging.info(f"Backed up original README.md to {backup_path}")
            print(f"Original README.md backed up to {backup_path}")
        
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(content)
        logging.info(f"Improved README.md successfully written to {readme_path}")
        print(f"Improved README.md successfully generated at {readme_path}")
    except Exception as e:
        logging.error(f"Failed to save improved README.md: {e}")
        print(f"Error saving improved README.md: {e}")
        sys.exit(1)

def save_converted_repo_txt(temp_txt_path: Path, repo_path: Path):
    """
    Saves the converted repository text file to the repository directory.
    If the file already exists, prompts the user to overwrite or cancel.
    """
    destination_path = repo_path / "repo_content_converted.txt"

    if destination_path.exists():
        while True:
            user_input = input(f"The file '{destination_path.name}' already exists in the repository. Overwrite? (y/n): ").strip().lower()
            if user_input == 'y':
                try:
                    shutil.copy(temp_txt_path, destination_path)
                    logging.info(f"Overwritten existing file: {destination_path}")
                    print(f"Converted repository content saved to {destination_path}")
                except Exception as e:
                    logging.error(f"Failed to overwrite file {destination_path}: {e}")
                    print(f"Error overwriting file {destination_path}: {e}")
                    sys.exit(1)
                break
            elif user_input == 'n':
                logging.info("User chose not to overwrite the existing converted repository file.")
                print("Converted repository content not saved to the repository.")
                break
            else:
                print("Please enter 'y' for yes or 'n' for no.")
    else:
        try:
            shutil.copy(temp_txt_path, destination_path)
            logging.info(f"Saved converted repository content to {destination_path}")
            print(f"Converted repository content saved to {destination_path}")
        except Exception as e:
            logging.error(f"Failed to save converted repository file to {destination_path}: {e}")
            print(f"Error saving converted repository file to {destination_path}: {e}")
            sys.exit(1)

# ------------------------------ Main Execution ------------------------------

def main():
    # Define log file path
    script_dir = Path(__file__).parent.resolve()
    log_file = script_dir / "improve_readme.log"
    setup_logging(log_file)
    logging.info("=== README.md Improvement Script Started ===")

    # Step 1: Get repository path from user
    repo_path = get_repo_path()

    # Step 2: Convert repository to text
    with tempfile.TemporaryDirectory() as temp_dir_name:
        temp_dir = Path(temp_dir_name)
        output_txt_path = temp_dir / "repo_content.txt"
        convert_repo_to_txt(repo_path, output_txt_path)

        # Step 3: Save the converted repo text file to the repository
        save_converted_repo_txt(output_txt_path, repo_path)

        # Step 4: Configure Google Gemini API
        configure_genai_api(API_KEY)

        # Step 5: Upload the text file to Gemini
        uploaded_file = upload_file_to_gemini(output_txt_path)

        # Step 6: Define the prompt
        prompt = """
        I am working on improving the README.md file for a GitLab repository. I want you to improve the attached README file section by section. Ensure that all website links are formatted in Markdown as "[text...](http://...)". The output should be in markdown.
        <title>

        Project Title: Introduce the project with a clear, compelling title and a brief description that explains what the project does and why it‘s useful. 

        1. Keep the original title.


        </title>

        <About>

        About: Introduce the project with a clear, compelling title and a brief description that explains what the project does and why it‘s useful. 

        1. Brief Overview: Write a short, impactful introduction that explains the core functionality of the project in 2-3 sentences. 

        2. If there is information about affiliations, organizations, contributors, or related projects, retain them.

        3. Keep this whole part simple, make brief overview and chair information in 2 paragraphs

        </About>

        <description>
        Description: Give a detailed overview of the project’s functionality, including any unique aspects or primary goals. Explain the problem it solves or the gap it addresses.
        1. Improve these into 2 paragraphs
        </description>

        <feature>
        Features: List the main features of the project in bullet points, focusing on what makes it valuable. Highlight any advanced or standout capabilities.
        1. Give a subtitle for each point
        </feature>

        <Requirements>
        Clearly specify requirements, including the use of package managers or similar tools in the Installation section.
        write them in a bullet point list
        </Requirements>

        <installation>
        Installation Process: Guide users through setting up the project step-by-step, making it beginner-friendly and easy to follow.
        If there are extra steps needed, such as choosing an environment in an IDE, mention them.
        </installation>

        <usage>
        Usage:  Provide examples of how to use the project.

        1. Specify which IDEs or tools users can utilize.
        2. Provide explanations for each example to clarify their purpose and usage in a bullet point list.

        If there are any important considerations or common issues users might face, mention them along with troubleshooting tips.
        </usage>

        <contact>
        Contact: Offer contact information, including how to reach the maintainers or ask for help.
        1. Improve the first sentence in original_README.md
        2. You must keep all websites .
        </contact>

        <License>
        Keep the original content. - **If the original README.md does not contain license information, insert the following statement: "Not enough information for license."**
        </License>

        Output:
        Provide only the improved README.md content based on the guidelines above. Only include sections above.
        """

        # Step 7: Generate improved README.md
        improved_readme = generate_improved_readme(uploaded_file, prompt)

    # Step 8: Save the improved README.md to the repository
    save_improved_readme(repo_path, improved_readme)

    logging.info("=== README.md Improvement Script Completed Successfully ===")
    print("Process completed. Check the log file for details.")

if __name__ == "__main__":
    main()
