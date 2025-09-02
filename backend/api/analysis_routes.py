from fastapi import APIRouter, File, UploadFile, Form, HTTPException
from core.analyzer import StartupAnalyzer

router = APIRouter(prefix="/api")
analyzer = StartupAnalyzer()

@router.post('/analyze')
async def analyze_startup_endpoint(
    file: UploadFile = File(...),
    sector: str = Form(None),
    stage: str = Form(None)
):
    if not file:
        raise HTTPException(status_code=400, detail="No file uploaded")
    
    if file.filename == '':
        raise HTTPException(status_code=400, detail="No file selected")
    
    try:
        file_data = await file.read()
        # This is now a regular function call
        result = analyzer.analyze_startup(file_data, file.filename, sector, stage)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")

@router.get('/analysis/{analysis_id}')
def get_analysis(analysis_id: str):
    try:
        doc_ref = analyzer.gcs_services.firestore_client.collection('startup_analyses').document(analysis_id)
        doc = doc_ref.get()
        if doc.exists:
            return doc.to_dict()
        else:
            raise HTTPException(status_code=404, detail="Analysis not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get('/benchmarks/{sector}/{stage}')
def get_benchmarks_endpoint(sector: str, stage: str):
    try:
        benchmarks = analyzer.benchmarking_engine.get_sector_benchmarks(sector, stage)
        return benchmarks
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))