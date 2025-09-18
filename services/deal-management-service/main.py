import os
import httpx
import firebase_admin
from firebase_admin import credentials, firestore
from fastapi import FastAPI, File, UploadFile, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import ValidationError

# Vertex AI Imports
from google.cloud import aiplatform
from vertexai.generative_models import GenerativeModel

# Import shared prompt & schema
from core.prompts import get_extraction_prompt
from core.schemas import DealData

# --- Configuration ---

# Firestore / Firebase setup
SERVICE_ACCOUNT_KEY_PATH = os.path.join(os.path.dirname(__file__), "serviceAccountKey.json")
if not os.path.exists(SERVICE_ACCOUNT_KEY_PATH):
    raise FileNotFoundError(
        "Firebase service account key not found. "
        "Please download it and place it in the same directory as this script."
    )

cred = credentials.Certificate(SERVICE_ACCOUNT_KEY_PATH)
firebase_admin.initialize_app(cred)
db = firestore.client()
deals_collection = db.collection("deals")

# Vertex AI initialization
# You can get project and location from environment variables or hard-code
PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT", "ai-analyst-85388")
REGION = os.getenv("GOOGLE_CLOUD_REGION", "us-central1")

# This init makes Vertex AI SDK aware of which project / region etc to use
aiplatform.init(
    project=PROJECT_ID,
    location=REGION,
)

# Choose the desired Gemini model
# Update the model name if you have access to a different one
MODEL_NAME = "gemini-1.5-flash"  # or gemini-2.0-flash / gemini-pro etc as per your access

model = GenerativeModel(MODEL_NAME)

# FastAPI app setup
app = FastAPI(
    title="Deal & Ingestion Service",
    description="A microservice to ingest documents, extract structured deal data using Vertex AI Gemini, then manage deals in Firestore.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*", "null"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- API Endpoints ---

@app.get("/")
def read_root():
    return {"status": "Service is running"}


@app.post("/ingest/file")
async def ingest_file(files: list[UploadFile] = File(...)):
    """
    Accepts one or more file uploads, extracts structured data using Gemini (Vertex AI),
    returns that data (and optionally saves via /deals).
    """
    if not files:
        raise HTTPException(status_code=400, detail="No files were uploaded.")

    print(f"Processing {len(files)} file(s)...")

    prompt = get_extraction_prompt()
    gemini_payload = [prompt]

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

        print(f"Determined MIME type: {mime_type} for {file.filename}")

        gemini_payload.append(f"--- Start of Document: {file.filename} ---")
        gemini_payload.append({"mime_type": mime_type, "data": file_bytes})
        gemini_payload.append(f"--- End of Document: {file.filename} ---")

    print("Calling Gemini via Vertex AI to generate content...")
    try:
        response = model.generate_content(gemini_payload)

        print("Cleaning the response JSON...")
        cleaned_json = response.text.strip() \
            .removeprefix("```json") \
            .removesuffix("```") \
            .strip()

        deal_data = DealData.model_validate_json(cleaned_json)
        print("Validation successful.")

        # Save to Firestore
        deal_dict = deal_data.model_dump()
        update_time, doc_ref = deals_collection.add(deal_dict)
        print(f"Deal saved in Firestore with id: {doc_ref.id}")

        return {
            "deal_id": doc_ref.id,
            "data": deal_dict
        }

    except ValidationError as e:
        print(f"Pydantic Validation Error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to validate Gemini response: {e}")
    except Exception as e:
        print(f"An unexpected error during ingestion: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/deals", status_code=status.HTTP_201_CREATED)
async def create_deal(deal_data: DealData):
    """
    Creates a new deal document in Firestore 'deals' collection from provided structured data.
    """
    try:
        deal_dict = deal_data.model_dump()
        update_time, doc_ref = deals_collection.add(deal_dict)
        return {"deal_id": doc_ref.id, "message": "Deal created successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/deals/{deal_id}")
async def get_deal(deal_id: str):
    """
    Retrieves a specific deal document from Firestore by its ID.
    """
    try:
        doc_ref = deals_collection.document(deal_id)
        doc = doc_ref.get()
        if doc.exists:
            return {"deal_id": doc.id, "data": doc.to_dict()}
        else:
            raise HTTPException(status_code=404, detail="Deal not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
