import os

# Load environment variables from a .env file if it exists (for local development)
# from dotenv import load_dotenv
# load_dotenv()

class Config:
    """Application configuration from environment variables."""

    # Google Cloud Project Settings
    PROJECT_ID = os.environ.get("GOOGLE_CLOUD_PROJECT")
    LOCATION = os.environ.get("GOOGLE_CLOUD_LOCATION", "us-central1")

    # BigQuery Settings
    BIGQUERY_DATASET = os.environ.get("BIGQUERY_DATASET_ID", "startup_benchmarks")

    # To use this, you would import it in other files, for example:
    # from config import Config
    # client = bigquery.Client(project=Config.PROJECT_ID)