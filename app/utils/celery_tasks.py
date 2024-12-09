from celery import Celery

#  Configure the Celery app (replace with your actual broker URL)
app = Celery('tasks', broker='redis://localhost:6379/0') 

@app.task
def initiate_documentation_task(llm_response, repository_url):
    """
    Celery task to handle documentation generation.
    """
    from app.documentation_generator import DocumentationGenerator # Import within the task to avoid circular dependencies
    generator = DocumentationGenerator()
    generator.generate_docs(llm_response, repository_url)