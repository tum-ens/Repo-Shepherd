Quickstart
==========

This guide provides a basic example of how to run the main application.

1.  **Ensure Installation:**
    Make sure you have followed the steps in the :doc:`installation` guide.

2.  **Run the Main Application:**
    The primary entry point seems to be `app/main.py`. Navigate to the project's root directory in your terminal and run:

    .. code-block:: bash

       python -m app.main

    *(Self-correction: Based on the `app/main.py` code, it seems to start a uvicorn server. The command might be different depending on how you intend users to launch it, e.g., directly running `uvicorn app.main:app --reload`)*

3.  **Access the Application:**
    If it's a web application (as suggested by FastAPI and uvicorn usage in `app/main.py`), open your web browser and go to the specified address (e.g., `http://localhost:8000`).

4.  **Basic Interaction:**
    Describe a simple first action a user should take (e.g., navigating to a specific GUI tab, running a basic analysis). *Content needed based on application workflow.*

*(Note: This is a generic quickstart. You should tailor it with specific commands and expected outcomes based on your project's primary function, potentially drawing examples from `app/gui-dev/getting_started.py` or the core logic in `app/main.py`.)*