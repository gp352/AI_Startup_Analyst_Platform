AI Analyst for Startup EvaluationAn AI-powered platform that evaluates startups by synthesizing founder materials and public data to generate concise, actionable investment insights.🚀 VisionEarly-stage investors are often overwhelmed by unstructured startup data from pitch decks, founder calls, and emails. Traditional analysis is time-consuming, inconsistent, and prone to error. This project aims to build an AI Analyst that cuts through the noise, evaluates startups like a trained associate, and generates investor-ready insights at scale using Google's powerful AI technologies.Core CapabilitiesIngest & Structure: Process pitch decks, call transcripts, and emails to generate structured deal notes.Benchmark: Compare startups against sector peers using financial multiples and traction signals.Risk Analysis: Flag potential red flags like inconsistent metrics or inflated market size.Synthesize & Recommend: Summarize growth potential and generate investor-ready recommendations.🏛️ ArchitectureThis platform is built using a modular microservice architecture. Each core functionality (e.g., ingestion, data management, reporting) is an independent service. This design ensures the platform is:Scalable: Each service can be scaled independently based on demand.Maintainable: Services can be updated and deployed without impacting the entire system.Resilient: An issue in one service is less likely to bring down the whole application.🛠️ Technology StackComponentTechnologyPurposeBackend FrameworkPython / FastAPIFor creating high-performance, asynchronous microservices.AI & Machine LearningGoogle Gemini 1.5 ProThe core LLM for document parsing, reasoning, and synthesis.DatabaseGoogle Firebase (Firestore)A NoSQL database for storing and managing deal data.Package ManagementuvAn extremely fast Python package installer and resolver.Deployment (Planned)Docker, Google Cloud RunContainerizing and deploying services in a serverless environment.🏁 Getting StartedFollow these instructions to get the project running on your local machine for development and testing.PrerequisitesGit installed.Python 3.10+ installed.uv installed.1. Clone the Repositorygit clone [https://github.com/YourUsername/ai-analyst-platform.git](https://github.com/YourUsername/ai-analyst-platform.git)
cd ai-analyst-platform
2. Set Up Environment VariablesThe project uses a .env file to manage secret keys.Create a file named .env in the root of the services/ingestion-service directory.Add your Gemini API key to this file:# services/ingestion-service/.env
GOOGLE_API_KEY="YOUR_API_KEY_HERE"
3. Install DependenciesEach service has its own environment and dependencies. To set up the ingestion-service:# Navigate to the service directory
cd services/ingestion-service

# Create the virtual environment
uv venv

# Install dependencies from requirements.txt
uv pip install -r requirements.txt

# Install the shared core-library in editable mode
uv pip install -e ../../core-library
▶️ How to Run the ProjectEach microservice must be run in its own terminal window.Run the Ingestion Service# From the services/ingestion-service directory
uvicorn main:app --reload
The service will be available at http://127.0.0.1:8000.🧪 How to TestThe easiest way to test the services is via the automatically generated Swagger UI documentation.Run the service you wish to test (e.g., ingestion-service).Open your web browser and navigate to http://127.0.0.1:8000/docs.Use the interactive interface to send requests and view responses.📁 Project Structure/ai-analyst-platform/
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
