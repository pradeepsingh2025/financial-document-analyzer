import os
import uuid
import asyncio

from fastapi import (
    FastAPI,
    File,
    UploadFile,
    Form,
    HTTPException,
    WebSocket,
    WebSocketDisconnect,
)
from celery.result import AsyncResult

from crewai import Crew, Process
from agents import financial_analyst, verifier, investment_advisor, risk_assessor
from task import (
    analyze_financial_document,
    verification,
    risk_assessment,
    investment_analysis,
)
from celery_worker import celery_app

app = FastAPI(title="Financial Document Analyzer")


def run_crew(query: str, file_path: str = "data/sample.pdf"):
    """To run the whole crew"""
    financial_crew = Crew(
        agents=[verifier, financial_analyst, risk_assessor, investment_advisor],
        tasks=[
            verification,
            analyze_financial_document,
            risk_assessment,
            investment_analysis,
        ],
        process=Process.sequential,
    )

    result = financial_crew.kickoff(inputs={"query": query, "file_path": file_path})
    return result


@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "Financial Document Analyzer API is running"}


@app.post("/analyze")
async def analyze_financial_document_api(
    file: UploadFile = File(...),
    query: str = Form(
        default="Analyze this financial document for investment insights"
    ),
):
    """Analyze financial document and provide comprehensive investment recommendations"""

    file_id = str(uuid.uuid4())
    file_path = f"data/financial_document_{file_id}.pdf"

    try:
        # Ensure data directory exists
        os.makedirs("data", exist_ok=True)

        # Save uploaded file
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)

        # Validate query
        if not query or query.strip() == "":
            query = "Analyze this financial document for investment insights"

        # Dispatch the task to Celery
        task = celery_app.send_task(
            "analyze_document",
            args=[query.strip(), file_path],
        )

        return {
            "status": "processing",
            "task_id": task.id,
            "message": "Document analysis has been queued.",
            "file_processed": file.filename,
        }

    except Exception as e:
        # If queuing fails, cleanup local file
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except Exception:
                pass
        raise HTTPException(
            status_code=500, detail=f"Error processing financial document: {str(e)}"
        )


@app.websocket("/ws/status/{task_id}")
async def websocket_status_endpoint(websocket: WebSocket, task_id: str):
    await websocket.accept()

    try:
        while True:
            task_result = AsyncResult(task_id, app=celery_app)
            state = task_result.state

            response_data = {
                "task_id": task_id,
                "status": state,
            }

            if state == "SUCCESS":
                response_data["result"] = task_result.result.get("result")
                await websocket.send_json(response_data)
                break

            elif state == "FAILURE":
                response_data["error"] = str(task_result.result)
                await websocket.send_json(response_data)
                break

            elif state == "STARTED":
                if (
                    task_result.info
                    and isinstance(task_result.info, dict)
                    and "message" in task_result.info
                ):
                    response_data["message"] = task_result.info.get("message")

            # Send current status
            await websocket.send_json(response_data)

            # Poll every 2 seconds
            await asyncio.sleep(2)

    except WebSocketDisconnect:
        print(f"WebSocket client disconnected for task {task_id}")
    except Exception as e:
        print(f"WebSocket error: {str(e)}")
        try:
            await websocket.close(code=1011, reason=str(e)[:100])
        except Exception:
            pass


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
