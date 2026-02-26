# Financial Document Analyzer

## Project Overview
A comprehensive financial document analysis system that processes corporate reports, financial statements, and investment documents using AI-powered analysis agents (CrewAI) exposed via a FastAPI backend.

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
Start the FastAPI server using Uvicorn:
```sh
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```
Or simply run the main script:
```sh
python main.py
```

### Usage
Once the server is running, you can interact with the API via the `/analyze` endpoint to upload financial documents (like Tesla's Q2 2025 financial update) and receive AI-driven investment analysis.

**Sample Document Testing:**
1. Download a financial report (e.g., Tesla Q2 2025 Update) and save it locally.
2. Send a POST request to `http://localhost:8000/analyze` with the PDF attached as form-data underneath the key `file`. You can also include a custom analysis request via the `query` form field.

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
- **Description:** Uploads a financial document (PDF) and an optional query. The CrewAI agents process the document to extract metrics, assess risks, and provide investment recommendations based on the user query.
- **Content-Type:** `multipart/form-data`
- **Parameters:**
  - `file` (File, required): The PDF document to be analyzed (uploaded via form data).
  - `query` (String, optional): The custom analysis request or question. Defaults to *"Analyze this financial document for investment insights"*.
- **Success Response (200 OK):**
  ```json
  {
    "status": "success",
    "query": "Analyze this financial document for investment insights",
    "analysis": "<Detailed AI-generated analysis and recommendation>",
    "file_processed": "sample.pdf"
  }
  ```
- **Error Response (500 Internal Server Error):**
  ```json
  {
    "detail": "Error processing financial document: <error_message>"
  }
  ```
