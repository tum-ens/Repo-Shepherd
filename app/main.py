from fastapi import FastAPI, BackgroundTasks
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from .proj.tasks import initiate_documentation_task

from .llm_handler import OllamaHandler
from .repository_reader import RepositoryReader
import json

app = FastAPI()

class RepositoryRequest(BaseModel):
    repository_path: str

@app.post("/analyze")
async def analyze_repository(request: RepositoryRequest, background_tasks: BackgroundTasks):
    """
    Endpoint to initiate the repository analysis workflow. 
    Expects a JSON payload with the README file in text format.
    """
    repository_path = request.repository_path

    # Initiate the workflow 
    reader = RepositoryReader(repository_path)
    code = reader.read_code() 

    llm = OllamaHandler()
    llm_response = llm.analyze_code(code)
    
    # Trigger documentation generation as a background task
    background_tasks.add_task(initiate_documentation_task, json.dumps(llm_response), repository_path)
    return JSONResponse({'message': 'Analysis initiated'}, status_code=202) 


# Main entry point
if __name__ == "__main__":
    import uvicorn
    import os
    os.system("uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload")
