import json
from .gcp_services import GoogleCloudServices

class RiskAssessmentEngine:
    def __init__(self, gcs_services: GoogleCloudServices):
        self.gcs = gcs_services

    def _assess_with_gemini(self, prompt: str, default_score: int = 5) -> dict:
        """Generic function to get a risk score and concerns from Gemini."""
        try:
            response = self.gcs.gemini_model.generate_content(prompt)
            clean_response = response.text.strip().replace('```json', '').replace('```', '')
            result = json.loads(clean_response)
            # Ensure required keys exist
            if 'score' not in result or 'concerns' not in result:
                return {'score': default_score, 'concerns': ['AI response format was invalid.']}
            return result
        except (json.JSONDecodeError, AttributeError, ValueError):
            return {'score': default_score, 'concerns': [f'AI analysis failed for this risk category.']}

    def _assess_market_risk(self, startup_data: dict) -> dict:
        analysis = startup_data.get('startup_analysis', {})
        prompt = f"""
        Analyze the market risk for a startup with the following details:
        - Description: "{analysis.get('description', 'N/A')}"
        - Problem: "{analysis.get('problem', 'N/A')}"
        - Solution: "{analysis.get('solution', 'N/A')}"
        - TAM: {analysis.get('market_size_tam', 'N/A')}

        Consider competition, market size, and barriers to entry.
        Return a JSON object with a 'score' (1-10, where 1 is low risk) and a 'concerns' array (list of strings).
        """
        return {"type": "Market", **self._assess_with_gemini(prompt, 6)}

    def _assess_team_risk(self, startup_data: dict) -> dict:
        analysis = startup_data.get('startup_analysis', {})
        prompt = f"""
        Analyze the execution risk based on the team's experience:
        - Team Summary: "{analysis.get('team_experience_summary', 'No summary provided.')}"
        
        Is this team likely to be able to execute on their vision? Consider experience and completeness.
        Return a JSON object with a 'score' (1-10, where 1 is low risk) and a 'concerns' array.
        """
        return {"type": "Team/Execution", **self._assess_with_gemini(prompt, 7)}

    def _assess_financial_risk(self, startup_data: dict) -> dict:
        analysis = startup_data.get('startup_analysis', {}).get('financials', {})
        prompt = f"""
        Analyze the financial risk based on these metrics:
        - MRR: {analysis.get('mrr', 'N/A')}
        - Burn Rate: {analysis.get('burn_rate', 'N/A')}
        - Runway: {analysis.get('runway_months', 'N/A')}
        - Funding Ask: {analysis.get('funding_ask_usd', 'N/A')}

        Consider sustainability, burn rate, and financial health.
        Return a JSON object with a 'score' (1-10, where 1 is low risk) and a 'concerns' array.
        """
        return {"type": "Financial", **self._assess_with_gemini(prompt, 5)}

    def _calculate_overall_risk(self, risk_factors: list) -> float:
        if not risk_factors:
            return 5.0
        total_score = sum(factor.get('score', 5) for factor in risk_factors)
        return round(total_score / len(risk_factors), 1)

    def _get_risk_level(self, risk_score: float) -> str:
        if risk_score <= 3: return 'Low'
        if risk_score <= 6: return 'Medium'
        return 'High'
    
    def assess_startup_risks(self, document_analysis: dict) -> dict:
        """Performs a comprehensive, AI-driven risk assessment."""
        risk_factors = [
            self._assess_market_risk(document_analysis),
            self._assess_team_risk(document_analysis),
            self._assess_financial_risk(document_analysis)
        ]
        
        overall_score = self._calculate_overall_risk(risk_factors)
        
        return {
            'risk_factors': risk_factors,
            'overall_risk_score': overall_score,
            'risk_level': self._get_risk_level(overall_score)
        }