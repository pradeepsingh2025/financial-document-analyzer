# Financial Document Analyzer

## Project Overview
A comprehensive financial document analysis system that processes corporate reports, financial statements, and investment documents using AI-powered analysis agents (CrewAI). It exposes a FastAPI backend leveraging a robust Queue Worker Model (Celery and Redis) for reliable, non-blocking asynchronous document processing via WebSockets.

## Bugs Found and How They Were Fixed

During the debugging phase of this project, several critical issues were identified and resolved to ensure deterministic and reliable execution:

1. **Broken PDF Extraction**
   - **Bug:** The initial implementation relied on unstable `crewai-tools` that failed to properly parse financial PDFs.
   - **Fix:** Substituted `crewai-tools` for a custom `read_data_tool` leveraging robust `requests` and `pymupdf` (fitz) packages for accurate text extraction from PDFs.
2. **Inefficient and Non-Deterministic Prompts**
   - **Bug:** The agents were producing inconsistent or informal outputs due to vague role descriptions and task assignments.
   - **Fix:** Overhauled agent descriptions to enforce highly professional, precise, and accurate financial reporting. Tasks were also updated to properly pass `context` between each other (e.g., `verification` -> `analyze_financial_document` -> `risk_assessment` -> `investment_analysis`).
3. **CrewAI Execution Errors**
   - **Bug:** The application was crashing due to incorrect imports, misaligned task assignments, and improper `kickoff` mechanics.
   - **Fix:** Corrected imports across `main.py`, `task.py`, and `tools.py`. Fixed task assignments in `run_crew` and properly structured the `kickoff` inputs.
4. **Blocking API Calls**
   - **Bug:** CrewAI's synchronous execution blocked the FastAPI event loop, causing timeouts.
   - **Fix:** Implemented `asyncio.to_thread` in `main.py` to handle the synchronous `run_crew` execution asynchronously, keeping the FastAPI application responsive.

## Setup and Usage Instructions

### Prerequisites
- Python 3.9+
- Redis (Running locally or via Docker)
- Obtain a [Serper API Key](https://serper.dev/) for web search functionalities.
- Appropriate LLM API keys (e.g., `GEMINI_API_KEY` depending on the configured CrewAI LLM).

### Installation
1. **Clone the repository and navigate to the project directory.**
2. **Set up a virtual environment (Optional but recommended):**
   ```sh
   python -m venv venv
   source venv/bin/activate  # On Windows use: venv\Scripts\activate
   ```
3. **Install Required Dependencies:**
   ```sh
   pip install -r requirements.txt
   ```
4. **Configure Environment Variables:**
   Create a `.env` file in the root directory and add your API keys:
   ```env
   SERPER_API_KEY=your_serper_api_key
   GEMINI_API_KEY=your_gemini_api_key
   ```

### Running the Application

This application requires three components to be running concurrently: Redis, the Celery Worker, and the FastAPI application.

1. **Start Redis Server:**
   You can run Redis quickly using Docker:
   ```sh
   docker run -p 6379:6379 -d redis
   ```
   *(Ensure Redis is running on `localhost:6379` before starting the worker).*

2. **Start the Celery Worker:**
   Open a new terminal, activate your virtual environment, and run the worker:
   ```sh
   # On Linux/macOS
   celery -A celery_worker worker --loglevel=info
   
   # On Windows (use the solo pool to avoid multiprocessing issues)
   celery -A celery_worker worker --loglevel=info --pool=solo
   ```

3. **Start the FastAPI Server:**
   Open another terminal, activate your virtual environment, and start Uvicorn:
   ```sh
   uvicorn main:app --host 0.0.0.0 --port 8000 --reload
   ```

### Usage
Because document analysis can be slow, this application uses an asynchronous Queue Worker model with WebSockets.
1. Download a financial report (e.g., Tesla Q2 2025 Update) and save it locally.
2. Send a POST request to `http://localhost:8000/analyze` with the PDF attached as form-data underneath the key `file`. You will immediately receive a `task_id`.
3. Connect to the WebSocket endpoint at `ws://localhost:8000/ws/status/{task_id}` to receive real-time updates and the final result.

## API Documentation

The application exposes a RESTful API powered by FastAPI. You can explore the interactive API documentation by navigating to `http://localhost:8000/docs` (Swagger UI) or `http://localhost:8000/redoc` (ReDoc) when the server is running.

### Endpoints

#### 1. API Health Check
- **Endpoint:** `GET /`
- **Description:** Checks if the API is up and running.
- **Response:**
  ```json
  {
    "message": "Financial Document Analyzer API is running"
  }
  ```

#### 2. Analyze Financial Document
- **Endpoint:** `POST /analyze`
- **Description:** Uploads a financial document (PDF) and queues it for analysis by the CrewAI agents. Returns a task ID immediately.
- **Content-Type:** `multipart/form-data`
- **Parameters:**
  - `file` (File, required): The PDF document to be analyzed.
  - `query` (String, optional): Custom analysis request. Defaults to *"Analyze this financial document for investment insights"*.
- **Success Response (202 Accepted):**
  ```json
  {
      "status": "processing",
      "task_id": "4b9f34a1-8d2b-41c9-a99f-723df76a0c20",
      "message": "Document analysis has been queued.",
      "file_processed": "sample.pdf"
  }
  ```

#### 3. Real-time Status via WebSockets
- **Endpoint:** `ws://localhost:8000/ws/status/{task_id}`
- **Description:** Connect to this WebSocket endpoint to receive real-time status updates and the final analysis result.
- **Message Format:**
  - *While processing:*
    ```json
    {
      "task_id": "4b9f34a1-8d2b-41c9-a99f-723df76a0c20",
      "status": "STARTED",
      "message": "Initializing financial crew..."
    }
    ```
  - *On Success:*
    ```json
    {
      "task_id": "4b9f34a1-8d2b-41c9-a99f-723df76a0c20",
      "status": "SUCCESS",
      "result": "<Detailed AI-generated analysis and recommendation>"
    }
    ```
  - *On Failure:*
     ```json
    {
      "task_id": "4b9f34a1-8d2b-41c9-a99f-723df76a0c20",
      "status": "FAILURE",
      "error": "<Error message detailing why the process failed>"
    }
    ```
