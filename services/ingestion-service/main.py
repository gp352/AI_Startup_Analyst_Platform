import os
import httpx

from dotenv import load_dotenv
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import ValidationError

# Import from our shared library
from core.prompts import get_extraction_prompt
from core.schemas import DealData

# --- Google Vertex AI ---
from google.cloud import aiplatform
from vertexai.generative_models import GenerativeModel, Part, Content

# --- Configuration ---
load_dotenv()

# Init Vertex AI (auth via ADC: gcloud/service account)
aiplatform.init(
    project="ai-analyst-85388",   # ⬅️ replace with your project id
    location="us-central1",       # ⬅️ must match your region with Gemini support
)

DEAL_SERVICE_URL = "http://127.0.0.1:8001/deals"  # URL for our new service

# --- FastAPI App Initialization ---
app = FastAPI(
    title="Ingestion Service",
    description="A microservice to process documents and create structured deal data.",
    version="1.0.0",
)

# --- Add CORS Middleware ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*", "null"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Gemini Model Initialization (Vertex AI) ---
model = GenerativeModel("gemini-2.5-pro")  # or gemini-1.5-pro


# --- API Endpoints ---
@app.post("/ingest/file")
async def ingest_file(files: list[UploadFile] = File(...)):
    """
    Accepts one or more file uploads, extracts structured data using Gemini,
    and saves it via the Deal Management Service.
    """
    if not files:
        raise HTTPException(status_code=400, detail="No files were uploaded.")

    print(f"Processing {len(files)} file(s)...")

    # --- Prepare Gemini request ---
    parts = [Part.from_text(get_extraction_prompt())]

    for file in files:
        print(f"Preparing file: {file.filename}...")
        file_bytes = await file.read()

        # Determine MIME type
        file_extension = os.path.splitext(file.filename)[1].lower()
        if file_extension == ".pdf":
            mime_type = "application/pdf"
        elif file_extension == ".txt":
            mime_type = "text/plain"
        else:
            mime_type = file.content_type or "application/octet-stream"

        print(f"Determined MIME type: {mime_type} for file: {file.filename}")

        # Wrap file as Part
        parts.append(
            Part.from_data(mime_type=mime_type, data=file_bytes)
        )

    # Create Content with role "user"
    content = Content(role="user", parts=parts)

    print("Generating content with Gemini (Vertex AI)...")
    response = model.generate_content([content])

    try:
        print("Validating Gemini response...")

        # Clean JSON output (strip markdown fences)
        cleaned_json = response.text.strip() \
            .removeprefix("```json") \
            .removesuffix("```") \
            .strip()

        deal_data = DealData.model_validate_json(cleaned_json)
        print("Validation successful.")

        # --- Call Deal Management Service ---
        print(f"Saving data to Deal Management Service at {DEAL_SERVICE_URL}...")
        async with httpx.AsyncClient() as client:
            api_response = await client.post(DEAL_SERVICE_URL, json=deal_data.model_dump())
            api_response.raise_for_status()

        deal_service_response = api_response.json()
        print("Data saved successfully.")

        return {
            "deal_id": deal_service_response.get("deal_id"),
            "data": deal_data.model_dump()
        }

    except ValidationError as e:
        print(f"Pydantic Validation Error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to validate Gemini response: {e}")
    except httpx.HTTPStatusError as e:
        print(f"Error calling Deal Service: {e.response.text}")
        raise HTTPException(status_code=e.response.status_code, detail=f"Error from Deal Service: {e.response.text}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")
