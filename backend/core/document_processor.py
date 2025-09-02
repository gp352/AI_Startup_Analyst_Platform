import io
import json
from datetime import datetime
from google.cloud import vision
import docx
import fitz  # PyMuPDF

from .gcp_services import GoogleCloudServices

class DocumentProcessor:
    def __init__(self, gcs_services: GoogleCloudServices):
        self.gcs = gcs_services

    def _extract_text_from_pdf(self, file_data: bytes) -> str:
        """Extracts text content from a PDF file."""
        text = ""
        with fitz.open(stream=file_data, filetype="pdf") as doc:
            for page in doc:
                text += page.get_text()
        return text

    def _extract_text_from_docx(self, file_data: bytes) -> str:
        """Extracts text content from a DOCX file."""
        doc = docx.Document(io.BytesIO(file_data))
        return "\n".join([para.text for para in doc.paragraphs])

    def _extract_text_from_txt(self, file_data: bytes) -> str:
        """Extracts text content from a TXT file."""
        return file_data.decode('utf-8')

    def _extract_text_from_image(self, file_data: bytes) -> str:
        """Extracts text using the Cloud Vision API for image types."""
        image = vision.Image(content=file_data)
        response = self.gcs.vision_client.text_detection(image=image)
        return response.text_annotations[0].description if response.text_annotations else ""

    def get_text_content(self, file_data: bytes, filename: str) -> str:
        """Determines file type and extracts text accordingly."""
        file_extension = filename.split('.')[-1].lower()
        if file_extension == 'pdf':
            return self._extract_text_from_pdf(file_data)
        elif file_extension == 'docx':
            return self._extract_text_from_docx(file_data)
        elif file_extension == 'txt':
            return self._extract_text_from_txt(file_data)
        elif file_extension in ['png', 'jpg', 'jpeg']:
            return self._extract_text_from_image(file_data)
        else:
            raise ValueError(f"Unsupported file type: {file_extension}")
    
    def analyze_startup_narrative(self, text_content: str) -> dict:
        """Analyze startup story and extract key information using Gemini."""
        prompt = f"""
        Analyze this startup pitch deck content and extract key information in JSON format.
        The content is: "{text_content}"

        Provide a structured analysis including:
        1.  `company_name` (string)
        2.  `description` (string)
        3.  `sector` (string, e.g., "SaaS", "FinTech")
        4.  `funding_stage` (string, e.g., "Seed", "Series A")
        5.  `market_size_tam` (integer, Total Addressable Market in USD)
        6.  `problem` (string)
        7.  `solution` (string)
        8.  `team_experience_summary` (string, a brief summary of the team's strengths)
        9.  `financials` (object with fields like `mrr`, `arr`, `burn_rate`, `runway_months`, `funding_ask_usd`)
        
        If a value is not found, set it to null. Ensure your output is a single, valid JSON object.
        """
        response = self.gcs.gemini_model.generate_content(prompt)
        try:
            # Clean the response to ensure it's valid JSON
            clean_response = response.text.strip().replace('```json', '').replace('```', '')
            return json.loads(clean_response)
        except (json.JSONDecodeError, AttributeError):
            return {'error': 'Failed to parse Gemini analysis', 'raw_text': response.text}

    def process_pitch_deck(self, file_data: bytes, filename: str) -> dict:
        """Process uploaded pitch deck using the appropriate text extraction and Gemini."""
        # 1. Extract text based on file type
        text_content = self.get_text_content(file_data, filename)
        
        if not text_content:
            return {'error': 'Could not extract any text from the document.'}
            
        # 2. Analyze content with Gemini to get structured data
        startup_analysis = self.analyze_startup_narrative(text_content)
        
        return {
            'text_content': text_content,
            'startup_analysis': startup_analysis,
            'processed_at': datetime.utcnow().isoformat()
        }