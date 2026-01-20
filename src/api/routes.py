"""FastAPI routes for GitHub profile analysis - MVC Architecture"""
from fastapi import APIRouter

from models.schemas import AnalyzeRequest, AnalyzeResponse, ReportRequest
from controllers.analysis_controller import AnalysisController
from controllers.report_controller import ReportController
from services.cache_service import clear_all_cache


router = APIRouter()


@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze_profile(request: AnalyzeRequest) -> AnalyzeResponse:
    """
    **Analyze GitHub Profile**
    
    Fetch complete GitHub user data including repositories, languages, and README files.
    
    **Input**: `{"github_input": "username"}` or full GitHub URL  
    **Output**: User profile + repository data + performance metrics
    """
    return await AnalysisController.analyze_profile(request)


@router.post("/reports/generate")
async def generate_report(request: ReportRequest):
    """
    **Generate Comprehensive Report**
    
    Create AI-powered hiring report with skills, recommendations, and project analysis.
    
    **Input**: `{"username": "...", "use_stored": true}`  
    **Output**: Full hiring report with technical assessment  
    **Speed**: 2-3s (cached) | 8-12s (fresh fetch)
    """
    return await ReportController.generate_report(request)


@router.delete("/cache/clear")
async def clear_cache():
    """
    **Clear Cache**
    
    Remove all cached GitHub API responses. Next requests will fetch fresh data.
    """
    await clear_all_cache()
    return {
        "status": "success",
        "message": "Cache cleared successfully"
    }
