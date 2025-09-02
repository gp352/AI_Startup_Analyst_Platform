import os
from datetime import datetime
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import firebase_admin

# Import the router from the api folder
from api.analysis_routes import router as analysis_router

# Initialize Firebase Admin
# On Cloud Run, it auto-detects credentials. For local dev, set GOOGLE_APPLICATION_CREDENTIALS.
try:
    if not firebase_admin._apps:
        firebase_admin.initialize_app()
except ValueError:
    pass # App may already be initialized in some contexts

# Create the FastAPI App
app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Register the API router. All routes like /api/analyze will now be active.
app.include_router(analysis_router)

@app.get('/health')
def health_check():
    """Health check endpoint to confirm the service is running."""
    return {'status': 'healthy', 'timestamp': datetime.utcnow().isoformat()}

if __name__ == '__main__':
    import uvicorn
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host='0.0.0.0', port=port)