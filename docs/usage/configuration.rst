Configuration
=============

The application uses configuration files located in the `config/` directory.

Configuration Files
-------------------

* **`config/settings.py`:** Appears to configure Celery, potentially setting up task queues with Redis. *(More details needed on what specific settings users might need to change).*
* **`config/celeryconfig.py`:** Contains further Celery configuration, including broker URL, result backend, serializers, and task routing. *(Explain key settings like `broker_url` and when a user might modify this).*

Environment Variables
---------------------

* **Gemini API Key:** As seen in `app/gui-dev/configuration.py` and other files, a Gemini API key is required for features leveraging the Gemini model. This is typically configured through the GUI's Setup tab but could potentially be set via environment variables (describe if applicable).

*(Add details about any other necessary configuration steps or environment variables.)*
