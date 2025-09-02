from datetime import datetime
from .gcp_services import GoogleCloudServices
from .document_processor import DocumentProcessor
from .benchmarking import BenchmarkingEngine
from .risk_assessment import RiskAssessmentEngine
from .investment_scorer import InvestmentScoringEngine

class StartupAnalyzer:
    def __init__(self):
        self.gcs_services = GoogleCloudServices()
        self.document_processor = DocumentProcessor(self.gcs_services)
        self.benchmarking_engine = BenchmarkingEngine(self.gcs_services)
        self.risk_engine = RiskAssessmentEngine(self.gcs_services)
        self.scoring_engine = InvestmentScoringEngine()

    def analyze_startup(self, file_data: bytes, filename: str, sector: str = None, stage: str = None) -> dict:
        """Complete synchronous startup analysis pipeline."""
        try:
            # Step 1: Process document to get structured data
            document_analysis = self.document_processor.process_pitch_deck(file_data, filename)
            
            if 'error' in document_analysis:
                return document_analysis

            startup_info = document_analysis.get('startup_analysis', {})
            
            # Use detected sector/stage if not provided
            sector = sector or startup_info.get('sector', 'SaaS')
            stage = stage or startup_info.get('funding_stage', 'Seed')
            
            # Step 2: Get benchmarks
            benchmarks = self.benchmarking_engine.get_sector_benchmarks(sector, stage)
            
            # Step 3: Assess risks
            risks = self.risk_engine.assess_startup_risks(document_analysis)
            
            # Step 4: Calculate investment score using real logic
            investment_score = self.scoring_engine.calculate_investment_score(
                document_analysis, benchmarks, risks
            )
            
            analysis_result = {
                'filename': filename,
                'sector': sector,
                'funding_stage': stage,
                'document_analysis': document_analysis,
                'benchmarks': benchmarks,
                'risk_assessment': risks,
                'investment_score': investment_score,
                'analyzed_at': datetime.utcnow().isoformat(),
                'status': 'completed'
            }
            
            # Step 5: Save to Firestore and return
            doc_ref = self.gcs_services.firestore_client.collection('startup_analyses').document()
            doc_ref.set(analysis_result)
            analysis_result['analysis_id'] = doc_ref.id
            return analysis_result
            
        except Exception as e:
            # Log and return a structured error
            error_result = {
                'error': str(e),
                'status': 'failed',
                'analyzed_at': datetime.utcnow().isoformat()
            }
            self.gcs_services.firestore_client.collection('analysis_errors').add(error_result)
            return error_result