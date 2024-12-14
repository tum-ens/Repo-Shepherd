from app.documentation_generator import DocumentationGenerator
from .celery import app

@app.task
def initiate_documentation_task(llm_response, repository_url):
    """
    Celery task to handle documentation generation.
    """
     # Import within the task to avoid circular dependencies
    generator = DocumentationGenerator(llm_response, repository_url)
    generator.generate_docs()

    return f"Docs generated...!"
