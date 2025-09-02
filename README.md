# 🚀 AI Startup Analyst Platform

This project is a web-based platform that uses Google Cloud's AI services (Gemini, Vision, BigQuery) to perform a comprehensive analysis of startup pitch decks and other documents. Users can upload materials, and the backend will generate an investment score, risk assessment, and benchmark comparison.

## ✨ Features

- **Multi-Format Upload:** Accepts PDF, DOCX, and TXT files.
- **AI-Powered Analysis:** Uses Gemini to extract key business metrics, problems, solutions, and team info.
- **Data-Driven Benchmarking:** Compares startup financials against sector averages stored in BigQuery.
- **Intelligent Risk Assessment:** Gemini analyzes market, execution, and financial risks.
- **Automated Scoring:** Generates a final investment score and recommendation.
- **Scalable Infrastructure:** Designed to be deployed on Google Cloud Run with Infrastructure as Code (Terraform).

## 🛠️ Tech Stack

- **Frontend:** HTML5, CSS3, Vanilla JavaScript
- **Backend:** Python, Flask, Gunicorn
- **Cloud/AI Services:**
  - Google Cloud Run (Hosting)
  - Google Vertex AI (Gemini 1.5 Pro)
  - Google Cloud Vision AI (OCR)
  - Google BigQuery (Benchmarking Data)
  - Google Firestore (Storing Results)
  - Google Cloud Build (CI/CD)
- **Infrastructure:** Docker, Terraform

## ⚙️ Setup and Installation

### Prerequisites

- [Google Cloud SDK](https://cloud.google.com/sdk/docs/install)
- [Terraform](https://developer.hashicorp.com/terraform/tutorials/aws-get-started/install-cli)
- [Python 3.10+](https://www.python.org/downloads/)
- [Docker](https://www.docker.com/products/docker-desktop/)

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd ai-startup-analyst
```

### 2. Configure Google Cloud

- Authenticate the gcloud CLI:
  ```bash
  gcloud auth login
  gcloud auth application-default login
  ```
- Create a Google Cloud Project and note the **Project ID**.

### 3. Set Up Backend Environment

- Navigate to the backend directory:
  ```bash
  cd backend
  ```
- Create a Python virtual environment:
  ```bash
  python3 -m venv venv
  source venv/bin/activate
  ```
- Install dependencies:
  ```bash
  pip install -r requirements.txt
  ```
- Create your secret environment file by copying the example:
  ```bash
  cp .env.example .env
  ```
- **Edit the `.env` file** with your Google Cloud Project ID and the path to your service account key.

## 🏃 Running the Application

### 1. Run the Backend Server

- From the `backend/` directory (with the virtual environment activated):
  ```bash
  python app.py
  ```
- The backend API will be running at `http://127.0.0.1:8080`.

### 2. Open the Frontend

- Open the `frontend/index.html` file directly in your web browser.
- In the "Backend API Configuration" section, enter `http://127.0.0.1:8080` and click "Test Connection".
- You are now ready to upload files and perform an analysis.

## ☁️ Deployment

This project is configured for automated deployment to Google Cloud Run.

1.  **Infrastructure:** Use Terraform to build all necessary cloud resources:
    ```bash
    cd deployment/terraform
    terraform init
    terraform apply -var="project_id=your-gcp-project-id"
    ```
2.  **Application:** Use Cloud Build to build the Docker image and deploy it to Cloud Run:
    ```bash
    gcloud builds submit --config cloudbuild.yaml .
    ```
The deployment scripts and configurations in the `deployment/`, `scripts/`, and root directories handle the full CI/CD lifecycle.