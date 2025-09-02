import numpy as np

class InvestmentScoringEngine:
    def __init__(self):
        self.weights = {
            'market_opportunity': 0.30,
            'team_strength': 0.25,
            'product_solution': 0.20,
            'traction_financials': 0.25
        }

    def _normalize_score(self, value, good_threshold, bad_threshold):
        """Normalizes a value to a 0-100 score."""
        if value >= good_threshold:
            return 100.0
        if value <= bad_threshold:
            return 0.0
        return 100 * (value - bad_threshold) / (good_threshold - bad_threshold)

    def _score_market_opportunity(self, startup_data: dict) -> float:
        """Scores market opportunity based on TAM."""
        tam = startup_data.get('market_size_tam', 0)
        # Score based on market size: >$1B is good, <$50M is poor.
        return self._normalize_score(tam, 1_000_000_000, 50_000_000)

    def _score_team_strength(self, startup_data: dict) -> float:
        """Scores team strength based on the length and quality of their summary."""
        summary = startup_data.get('team_experience_summary', "")
        # A simple metric: longer, more detailed summaries are better.
        return self._normalize_score(len(summary), 200, 50)

    def _score_product_solution(self, startup_data: dict) -> float:
        """Scores the product/solution based on the clarity of the problem and solution statements."""
        problem = startup_data.get('problem', "")
        solution = startup_data.get('solution', "")
        # Score based on combined length. Clearer problem/solution statements are often longer.
        return self._normalize_score(len(problem) + len(solution), 400, 100)

    def _score_traction_financials(self, startup_data: dict, benchmarks: dict) -> float:
        """Scores traction and financials against benchmarks."""
        if not benchmarks or 'error' in benchmarks:
            return 30.0 # Default low score if no benchmarks are available

        financials = startup_data.get('financials', {})
        growth = financials.get('arr', 0) / 12  # Use ARR to estimate monthly growth
        
        # Compare startup's growth to the sector average
        avg_growth = benchmarks.get('avg_revenue_growth', 0)
        if avg_growth == 0:
            return 50.0 # Neutral score if benchmark data is zero
            
        growth_score = self._normalize_score(growth, avg_growth * 1.5, avg_growth * 0.5)
        return growth_score

    def get_investment_recommendation(self, score: float) -> dict:
        """Generates a recommendation based on the final score."""
        if score >= 80:
            return {'action': 'Strong Buy', 'reasoning': 'Exceptional fundamentals and strong market position.', 'confidence': 'High'}
        elif score >= 65:
            return {'action': 'Buy', 'reasoning': 'Solid investment opportunity with manageable risks.', 'confidence': 'Medium-High'}
        elif score >= 50:
            return {'action': 'Hold', 'reasoning': 'Good potential but requires closer monitoring of key risks.', 'confidence': 'Medium'}
        else:
            return {'action': 'Pass', 'reasoning': 'Significant concerns or risks outweigh the potential upside.', 'confidence': 'High'}
            
    def calculate_investment_score(self, startup_data: dict, benchmarks: dict, risks: dict) -> dict:
        """Calculate overall investment attractiveness score with real logic."""
        scores = {}
        analysis = startup_data.get('startup_analysis', {})

        scores['market_opportunity'] = self._score_market_opportunity(analysis)
        scores['team_strength'] = self._score_team_strength(analysis)
        scores['product_solution'] = self._score_product_solution(analysis)
        scores['traction_financials'] = self._score_traction_financials(analysis, benchmarks)
        
        # Calculate weighted overall score
        overall_score = sum(scores[category] * self.weights[category] for category in self.weights)
        
        # Apply risk adjustment. A higher risk score should decrease the investment score.
        risk_score = risks.get('overall_risk_score', 5) # 1-10 scale
        risk_adjustment_factor = 1 - (risk_score / 100) # e.g., risk 5/10 -> 5% reduction
        adjusted_score = overall_score * (1 - risk_adjustment_factor)

        return {
            'overall_score': round(adjusted_score, 1),
            'category_scores': scores,
            'recommendation': self.get_investment_recommendation(adjusted_score)
        }