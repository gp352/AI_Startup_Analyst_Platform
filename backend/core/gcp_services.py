import os
from google.cloud import vision, bigquery, storage, firestore
import vertexai
from vertexai.generative_models import GenerativeModel
from vertexai.language_models import TextEmbeddingModel

class GoogleCloudServices:
    def __init__(self):
        # In production on Cloud Run, project and location are often inherited automatically.
        # For local development, ensure GOOGLE_CLOUD_PROJECT is set in your environment.
        project_id = os.environ.get("GOOGLE_CLOUD_PROJECT")
        location = os.environ.get("GOOGLE_CLOUD_LOCATION", "us-central1")
        
        vertexai.init(project=project_id, location=location)
        
        self.vision_client = vision.ImageAnnotatorClient()
        self.bigquery_client = bigquery.Client()
        self.storage_client = storage.Client()
        self.firestore_client = firestore.Client()
        
        # Initialize the Gemini and Embedding models
        self.gemini_model = GenerativeModel("gemini-1.5-pro")
        self.embedding_model = TextEmbeddingModel.from_pretrained("textembedding-gecko@003")