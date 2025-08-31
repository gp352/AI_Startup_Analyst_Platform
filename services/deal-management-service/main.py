import os
import firebase_admin
from firebase_admin import credentials, firestore
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware

# Import the schema from our shared library
from core.schemas import DealData

# --- Firebase Initialization ---
# Get the absolute path to the directory of the current script
# to reliably locate the service account key.
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

# --- FastAPI App Initialization ---
app = FastAPI(
    title="Deal Management Service",
    description="A microservice for managing startup deal data in Firestore.",
    version="1.0.0",
)

# --- Add CORS Middleware ---
# This MUST be added before the routes are defined.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allows all origins for development
    allow_credentials=True,
    allow_methods=["*"], # Allows all methods
    allow_headers=["*"], # Allows all headers
)

# --- API Endpoints ---
@app.get("/")
def read_root():
    """ A simple endpoint to check if the service is running. """
    return {"status": "Deal Management Service is running"}

@app.post("/deals", status_code=status.HTTP_201_CREATED)
async def create_deal(deal_data: DealData):
    """
    Creates a new deal document in the Firestore 'deals' collection.
    """
    try:
        # Pydantic's model_dump() converts the object to a dict, perfect for Firestore
        deal_dict = deal_data.model_dump()
        # Add a new doc with a generated ID
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