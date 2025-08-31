import os
import httpx
import google.generativeai as genai

from dotenv import load_dotenv
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import ValidationError

# Import from our shared library
from core.prompts import get_extraction_prompt
from core.schemas import DealData

# --- Configuration ---
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    raise ValueError("GOOGLE_API_KEY not found. Please set it in your .env file.")
genai.configure(api_key=api_key)

DEAL_SERVICE_URL = "http://127.0.0.1:8001/deals" # URL for our new service

# --- FastAPI App Initialization ---
app = FastAPI(
    title="Ingestion Service",
    description="A microservice to process documents and create structured deal data.",
    version="1.0.0",
)

# --- Add CORS Middleware ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allows all origins for development
    allow_credentials=True,
    allow_methods=["*"], # Allows all methods
    allow_headers=["*"], # Allows all headers
)

# --- Gemini Model Initialization ---
# ... rest of the file is the same



# --- Gemini Model Initialization ---
model = genai.GenerativeModel('gemini-2.0-flash-exp')

# --- API Endpoints ---
@app.post("/ingest/file")
async def ingest_file(file: UploadFile = File(...)):
    """
    Accepts a file upload, extracts structured data using Gemini,
    and saves it via the Deal Management Service.
    """
    print(f"Processing file: {file.filename}...")
    file_bytes = await file.read()

    # --- CORRECTED LOGIC ---
    # Instead of calling upload_file, we create a "file part" object
    # that generate_content can understand directly.
    prompt = get_extraction_prompt()
    file_part = {
        "mime_type": file.content_type,
        "data": file_bytes
    }

    print("Generating content with Gemini...")
    # Pass the prompt and the file part directly to the model
    response = model.generate_content([prompt, file_part])

    try:
        print("Validating Gemini response...")
        
        # --- New Step: Clean the JSON response ---
        # LLMs often wrap JSON in markdown, so we need to strip it before parsing.
        cleaned_json = response.text.strip().removeprefix("```json").removesuffix("```").strip()
        
        deal_data = DealData.model_validate_json(cleaned_json)
        print("Validation successful.")

        # --- Call the Deal Management Service ---
        print(f"Saving data to Deal Management Service at {DEAL_SERVICE_URL}...")
        async with httpx.AsyncClient() as client:
            api_response = await client.post(DEAL_SERVICE_URL, json=deal_data.model_dump())
            api_response.raise_for_status() # Raises an exception for 4xx/5xx responses

        print("Data saved successfully.")
        return api_response.json() # Return the response from the deal service

    except ValidationError as e:
        print(f"Pydantic Validation Error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to validate Gemini response: {e}")
    except httpx.HTTPStatusError as e:
        print(f"Error calling Deal Service: {e.response.text}")
        raise HTTPException(status_code=e.response.status_code, detail=f"Error from Deal Service: {e.response.text}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")


