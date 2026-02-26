import os
import sys

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from celery import Celery

# Initialize Celery app
celery_app = Celery(
    "financial_tasks",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/0",
)

# Optionally configure celery settings
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
)


@celery_app.task(name="analyze_document", bind=True)
def analyze_document_task(self, query: str, file_path: str):
    """
    Celery task to run the CrewAI financial analysis process.
    """
    # Import inside the task to avoid circular dependencies or loading models in the main web server process unnecessarily
    from main import run_crew

    try:
        self.update_state(
            state="STARTED", meta={"message": "Initializing financial crew..."}
        )

        # Execute the crew
        result = run_crew(query, file_path)

        # Return the string representation of the crew output
        return {"status": "success", "result": str(result)}

    except Exception as e:
        # Re-raise the exception so Celery marks the task as FAILURE
        raise e

    finally:
        # Clean up the file after processing
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except Exception as e:
                print(f"Failed to clean up file {file_path}: {e}")
