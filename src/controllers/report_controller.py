"""
Report Controller

Handles HTTP requests for generating analysis reports.
Delegates business logic to AnalysisService.
"""
import uuid
from typing import Dict, Any

from fastapi import HTTPException
from models.schemas import ReportRequest
from services.github_service import GitHubService
from services.storage_service import storage_service
from utils.logger import logger


class ReportController:
    """
    Controller for report generation endpoints.
    
    Responsibilities:
    - Handle HTTP request/response for report generation
    - Coordinate data fetching (stored vs fresh)
    - Delegate to AnalysisService for report generation
    """
    
    @staticmethod
    async def generate_report(request: ReportRequest) -> Dict[str, Any]:
        """
        Generate comprehensive analysis report.
        
        Process:
        1. Get data (from storage or fresh analysis)
        2. Delegate to AnalysisService for report generation
        3. Return formatted report
        
        Args:
            request: ReportRequest with username, report_type, use_stored
            
        Returns:
            Dict with comprehensive analysis report
        """
        # Import here to avoid circular dependency
        from services.analysis_service import analysis_service
        
        request_id = str(uuid.uuid4())[:8]
        
        try:
            username = request.username
            report_type = request.report_type
            use_stored = request.use_stored
            
            logger.info(f"[{request_id}] Generating {report_type} report for {username}")
            
            # Step 1: Get data (from storage or fresh analysis)
            data = None
            data_source = "unknown"
            
            if use_stored:
                # Try to load from storage first
                stored = storage_service.load_analysis(username)
                if stored:
                    # Extract the actual data from nested structure
                    stored_data = stored.get("data", {})
                    # Handle both old and new storage formats
                    if "data" in stored_data:
                        # New format: {data: {data: {user, repositories}}}
                        data = stored_data.get("data")
                    else:
                        # Old format: {data: {user, repositories}}
                        data = stored_data
                    
                    data_source = "stored_json"
                    logger.info(f"[{request_id}] Using stored data")
            
            # If no stored data, analyze fresh
            if not data:
                logger.info(f"[{request_id}] No stored data, analyzing fresh...")
                async with GitHubService() as github_service:
                    analysis = await github_service.analyze_profile(username)
                
                # Build data structure
                user_data = {
                    "user": analysis["profile"],
                    "repositories": analysis["repositories"]
                }
                data = user_data
                data_source = "fresh_analysis"
                
                # Save to storage for future use
                try:
                    storage_service.save_analysis(username, {"data": data})
                    logger.info(f"[{request_id}] [SUCCESS] Saved to db/{username}.json")
                except Exception as e:
                    logger.warning(f"[{request_id}] Failed to save: {e}")
            
            # Step 2: Generate deterministic analysis report
            logger.info(f"[{request_id}] Generating deterministic analysis report...")
            report = analysis_service.generate_report(data, report_type)
            
            # Add metadata
            report["request_id"] = request_id
            report["data_source"] = data_source
            
            logger.info(f"[{request_id}] [SUCCESS] Report generated successfully")
            
            return report
            
        except ValueError as e:
            logger.error(f"[{request_id}] Validation error: {e}")
            raise HTTPException(status_code=400, detail=str(e))
        
        except Exception as e:
            logger.error(f"[{request_id}] Report generation failed: {e}")
            raise HTTPException(status_code=500, detail=f"Report generation failed: {str(e)}")
