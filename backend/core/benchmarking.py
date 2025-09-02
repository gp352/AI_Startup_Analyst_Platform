from google.cloud import bigquery
from .gcp_services import GoogleCloudServices

class BenchmarkingEngine:
    def __init__(self, gcs_services: GoogleCloudServices):
        self.gcs = gcs_services
        # It's better to get this from config, but hardcoding is fine for now.
        self.dataset_id = "startup_benchmarks"

    def get_sector_benchmarks(self, sector: str, funding_stage: str) -> dict:
        """Queries BigQuery for sector-specific benchmarks (synchronous)."""
        
        query = f"""
        SELECT 
            AVG(revenue_growth) as avg_revenue_growth,
            AVG(customer_acquisition_cost) as avg_cac,
            AVG(lifetime_value) as avg_ltv,
            AVG(burn_rate) as avg_burn_rate,
            AVG(runway_months) as avg_runway,
            COUNT(*) as sample_size
        FROM `{self.gcs.bigquery_client.project}.{self.dataset_id}.startup_metrics`
        WHERE sector = @sector 
        AND funding_stage = @funding_stage
        AND created_date >= DATE_SUB(CURRENT_DATE(), INTERVAL 2 YEAR)
        """
        
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("sector", "STRING", sector),
                bigquery.ScalarQueryParameter("funding_stage", "STRING", funding_stage),
            ]
        )
        
        # The .result() call is blocking and waits for the query to complete.
        query_job = self.gcs.bigquery_client.query(query, job_config=job_config)
        results = query_job.result()
        
        for row in results:
            # Return the first row of results
            return {
                'avg_revenue_growth': float(row.avg_revenue_growth or 0),
                'avg_cac': float(row.avg_cac or 0),
                'avg_ltv': float(row.avg_ltv or 0),
                'avg_burn_rate': float(row.avg_burn_rate or 0),
                'avg_runway': float(row.avg_runway or 0),
                'sample_size': int(row.sample_size or 0)
            }
        
        return {'error': 'No benchmark data found for the given criteria.'}