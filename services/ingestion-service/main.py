import os
import re
import google.generativeai as genai
from fastapi import FastAPI, HTTPException, UploadFile, File
from pydantic import ValidationError
from dotenv import load_dotenv

# Import from our new shared library
from core.prompts import get_extraction_prompt
from core.schemas import DealData

# --- Configuration & Initialization ---
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    raise ValueError("GOOGLE_API_KEY not found. Please set it in your .env file.")
genai.configure(api_key=api_key)

app = FastAPI(
    title="Ingestion Service",
    description="A microservice to process documents and extract structured startup data.",
    version="1.0.0",
)

model = genai.GenerativeModel('gemini-2.0-flash-exp')

# --- Helper Function ---
def clean_json_response(raw_text: str) -> str:
    """
    Finds and extracts a JSON block from Gemini's raw response,
    which might be wrapped in markdown backticks.
    """
    match = re.search(r"```json\n({.*?})\n```", raw_text, re.DOTALL)
    if match:
        return match.group(1)
    # Fallback for plain JSON without markdown
    return raw_text.strip()

# --- API Endpoints ---
@app.get("/")
def read_root():
    """ A simple endpoint to check if the service is running. """
    return {"status": "Ingestion Service is running"}

@app.post("/ingest/file", response_model=DealData)
async def ingest_file(file: UploadFile = File(...)):
    """
    Receives a file, sends it to Gemini for analysis, and returns
    structured, validated data based on the DealData schema.
    """
    if not file.content_type:
        raise HTTPException(status_code=400, detail="File content type not provided.")

    try:
        # 1. Upload the file to the Gemini API's file service.
        print(f"Uploading file: {file.filename}...")
        uploaded_file = genai.upload_file(
            path=file.file,
            display_name=file.filename,
            mime_type=file.content_type
        )
        print(f"File upload complete.")

        # 2. Prepare the prompt from our core-library
        prompt = get_extraction_prompt()

        # 3. Make the API call to Gemini with both the file and the prompt
        print("Generating content with Gemini...")
        response = model.generate_content([uploaded_file, prompt])

        # 4. Clean and validate the response
        print("Validating Gemini response...")
        cleaned_json_str = clean_json_response(response.text)
        
        # Use Pydantic to parse and validate the JSON against our schema
        deal_data = DealData.model_validate_json(cleaned_json_str)

        return deal_data

    except ValidationError as e:
        print(f"Pydantic Validation Error: {e.errors()}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to validate data from Gemini. Errors: {e}"
        )
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        raise HTTPException(status_code=500, detail=str(e))

