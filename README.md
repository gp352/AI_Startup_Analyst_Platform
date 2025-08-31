AI Analyst for Startup Evaluation
An AI-powered platform that evaluates startups by synthesizing founder materials and public data to generate concise, actionable investment insights.

🚀 Vision
Investors face a deluge of unstructured startup data, making manual analysis slow, inconsistent, and error-prone. 
This project builds an AI Analyst using Google's AI to automate evaluation, cut through the noise, and produce scalable, investor-ready insights.

Core Capabilities
Ingest & Structure: Process pitch decks, call transcripts, and emails to generate structured deal notes.
Benchmark: Compare startups against sector peers using financial multiples and traction signals.
Risk Analysis: Flag potential red flags like inconsistent metrics or inflated market size.
Synthesize & Recommend: Summarize growth potential and generate investor-ready recommendations.

🏛️ Architecture
This platform uses a modular microservice architecture where each core function is an independent service. 
This design makes the platform:
Scalable: Services scale independently based on demand.
Maintainable: Services can be updated and deployed without system-wide impact.
Resilient: An issue in one service is isolated from the rest of the application.

🛠️ Technology Stack
| Component | Technology | Purpose || Backend Framework | Python / FastAPI | For creating high-performance, asynchronous microservices. || AI & Machine Learning | Google Gemini 1.5 Pro | The core LLM for document parsing, reasoning, and synthesis. || Database | Google Firebase (Firestore) | A NoSQL database for storing and managing deal data. || Package Management | uv | An extremely fast Python package installer and resolver. || Deployment (Planned) | Docker, Google Cloud Run | Containerizing and deploying services in a serverless environment. |

🏁 Getting Started
Follow these instructions to run the project locally for development and testing.
Prerequisites:
Git installed.
Python 3.10+ installed.
uv installed.
1. Clone the Repositorygit clone [https://github.com/YourUsername/ai-analyst-platform.git](https://github.com/YourUsername/ai-analyst-platform.git)
cd ai-analyst-platform

2. Set Up Environment VariablesThe project uses a .env file to manage secret keys.Create a file named .env in the root of the services/ingestion-service directory.Add your Gemini API key to this file:# services/ingestion-service/.env
GOOGLE_API_KEY="YOUR_API_KEY_HERE"

3. Install DependenciesEach service has its own environment. To set up the ingestion-service:# Navigate to the service directory
cd services/ingestion-service

# Create the virtual environment
uv venv

# Install dependencies from requirements.txt
uv pip install -r requirements.txt

# Install the shared core-library in editable mode
uv pip install -e ../../core-library

▶️ How to Run the ProjectEach microservice must be run in its own terminal window.Run the Ingestion Service# From the services/ingestion-service directory
uvicorn main:app --reload

The service will be available at http://127.0.0.1:8000.🧪 How to TestThe easiest way to test services is via the auto-generated Swagger UI.Run the service you wish to test (e.g., ingestion-service).
Open your web browser and navigate to http://127.0.0.1:8000/docs.Use the interactive interface to send requests and view responses.

📁 Project Structure/ai-analyst-platform/
|
|--- services/                  # Each microservice is a separate application
|    |--- ingestion-service/     # Handles document processing and data extraction
|    `--- ...                   # Other services (deal-management, etc.)
|
|--- core-library/              # A shared Python library for all backend services
|    |--- core/
|    |    |--- prompts.py       # Centralized Gemini prompt templates
|    |    `--- schemas.py       # Pydantic models for consistent data structures
|    `--- setup.py
|
|--- .gitignore                 # Specifies intentionally untracked files to ignore
|
`--- README.md                  # This file

