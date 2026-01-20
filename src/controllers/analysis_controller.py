"""
Analysis Controller

Handles HTTP requests for GitHub profile analysis.
Delegates business logic to AnalysisService.
"""
import uuid
import time
from datetime import datetime
from typing import Dict, Any

from fastapi import HTTPException
from models.schemas import AnalyzeRequest, AnalyzeResponse, UserData, RepositoryData, PerformanceMetrics
from services.github_service import GitHubService
from services.cache_service import get_cache, set_cache
from services.storage_service import storage_service
from utils.validators import normalize_github_input
from utils.logger import logger
from core.config import settings


class AnalysisController:
    """
    Controller for GitHub profile analysis endpoints.
    
    Responsibilities:
    - Handle HTTP request/response
    - Input validation (via Pydantic)
    - Cache management
    - Delegate to GitHubService for data fetching
    - Delegate to StorageService for persistence
    """
    
    @staticmethod
    async def analyze_profile(request: AnalyzeRequest) -> AnalyzeResponse:
        """
        Analyze GitHub profile - main analysis endpoint.
        
        Process:
        1. Normalize input (username/URL → username)
        2. Check cache (24h TTL)
        3. If cache miss → Fetch from GitHub
        4. Save to storage (optional)
        5. Cache result
        6. Return formatted response
        
        Args:
            request: AnalyzeRequest with github_input
            
        Returns:
            AnalyzeResponse with user data and repositories
        """
        request_id = str(uuid.uuid4())[:8]
        start_time = time.time()
        
        try:
            # Step 1: Normalize input
            username, _ = normalize_github_input(request.github_input)
            logger.info(f"[{request_id}] Analyzing: {username}")
            
            # Step 2: Check cache
            cache_key = f"profile:{username.lower()}"
            cached_data = await get_cache(cache_key)
            
            if cached_data:
                logger.info(f"[{request_id}] [SUCCESS] Cache hit for {username}")
                cached_data["request_id"] = request_id
                cached_data["timestamp"] = datetime.utcnow().isoformat()
                cached_data["performance"]["cache_hit"] = True
                cached_data["cache_info"] = {"hit": True}
                # Ensure required fields exist (for backwards compatibility with old cache)
                if "total_repos_analyzed" not in cached_data:
                    cached_data["total_repos_analyzed"] = len(cached_data.get("repositories", []))
                if "total_api_calls" not in cached_data:
                    cached_data["total_api_calls"] = len(cached_data.get("repositories", [])) + 1
                return AnalyzeResponse(**cached_data)
            
            logger.info(f"[{request_id}] Cache miss, fetching from GitHub...")
            
            # Step 3: Fetch from GitHub
            api_start = time.time()
            
            async with GitHubService() as github_service:
                analysis = await github_service.analyze_profile(username)
            
            api_latency = int((time.time() - api_start) * 1000)
            
            # Step 4: Build response
            user = UserData(
                login=analysis["profile"].get("login"),
                name=analysis["profile"].get("name"),
                bio=analysis["profile"].get("bio"),
                location=analysis["profile"].get("location"),
                followers=analysis["profile"].get("followers", 0),
                following=analysis["profile"].get("following", 0),
                public_repos=analysis["profile"].get("public_repos", 0),
                created_at=analysis["profile"].get("created_at", ""),
                updated_at=analysis["profile"].get("updated_at", ""),
                avatar_url=analysis["profile"].get("avatar_url", ""),
                blog=analysis["profile"].get("blog"),
                company=analysis["profile"].get("company"),
            )
            
            repositories = [
                RepositoryData(**repo)
                for repo in analysis["repositories"]
            ]
            
            total_time = time.time() - start_time
            
            performance = PerformanceMetrics(
                github_api_latency_ms=api_latency,
                processing_latency_ms=int((total_time - api_latency / 1000) * 1000),
                total_latency_ms=int(total_time * 1000),
                cache_hit=False,
                cache_ttl_remaining_seconds=settings.CACHE_TTL_SECONDS,
            )
            
            response_data = {
                "status": "success",
                "request_id": request_id,
                "timestamp": datetime.utcnow().isoformat(),
                "user": user.dict(),
                "repositories": [r.dict() for r in repositories],
                "total_repos_analyzed": len(repositories),
                "total_api_calls": len(repositories) + 1,  # 1 for user + 1 per repo
                "performance": performance.dict(),
                "cache_info": {"hit": False},
                "data": {
                    "user": analysis["profile"],
                    "repositories": analysis["repositories"]
                }
            }
            
            # Step 5: Save to storage
            storage_service.save_analysis(username, response_data)
            
            # Step 6: Cache result
            await set_cache(cache_key, response_data)
            
            logger.info(f"[{request_id}] [SUCCESS] Analysis complete: {len(repositories)} repos, {total_time:.2f}s")
            return AnalyzeResponse(**response_data)
            
        except ValueError as e:
            logger.error(f"[{request_id}] [ERROR] Validation error: {e}")
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            logger.error(f"[{request_id}] [ERROR] Analysis failed: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")
