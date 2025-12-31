"""FastAPI routes for GitHub profile analysis"""
from fastapi import APIRouter, HTTPException
import uuid
from datetime import datetime
import time

from config import settings
from models import AnalyzeRequest, AnalyzeResponse, UserData, RepositoryData, LanguageStats, ReadmeInfo, PerformanceMetrics
from github_service import GitHubService
from cache_service import get_cache, set_cache, clear_all_cache
from utils.validators import normalize_github_input
from utils.logger import logger


router = APIRouter()


@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze_profile(request: AnalyzeRequest) -> AnalyzeResponse:
    """
    Main endpoint: Analyze GitHub profile
    
    INPUT: {"github_input": "torvalds"} or {"github_input": "https://github.com/torvalds"}
    OUTPUT: Complete GitHub data (user profile, repositories, languages, READMEs)
    
    Process:
    1. Normalize input (username/URL → username)
    2. Check cache (24h TTL)
    3. If cache miss → Fetch from GitHub (parallel API calls)
    4. Cache result
    5. Return formatted response
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
            logger.info(f"[{request_id}] ✅ Cache hit for {username}")
            cached_data["request_id"] = request_id
            cached_data["timestamp"] = datetime.utcnow().isoformat()
            cached_data["performance"]["cache_hit"] = True
            cached_data["cache_info"] = {"hit": True}
            return AnalyzeResponse(**cached_data)
        
        logger.info(f"[{request_id}] ❌ Cache miss, fetching from GitHub...")
        
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
            "repositories": [repo.dict() for repo in repositories],
            "total_repos_analyzed": len(repositories),
            "total_api_calls": analysis["api_calls"],
            "performance": performance.dict(),
            "cache_info": {"hit": False}
        }
        
        # Step 5: Cache result
        try:
            cache_payload = {
                "status": "success",
                "user": user.dict(),
                "repositories": [repo.dict() for repo in repositories],
                "total_repos_analyzed": len(repositories),
                "total_api_calls": analysis["api_calls"],
                "performance": performance.dict(),
            }
            await set_cache(cache_key, cache_payload)
            logger.info(f"[{request_id}] 💾 Cached result for {username}")
        except Exception as e:
            logger.warning(f"[{request_id}] Cache write error: {e}")
        
        logger.info(f"[{request_id}] ✅ Analysis complete in {int(total_time * 1000)}ms")
        
        return AnalyzeResponse(**response_data)
    
    except ValueError as e:
        logger.error(f"[{request_id}] ❌ Validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    
    except Exception as e:
        logger.error(f"[{request_id}] ❌ Unexpected error: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@router.get("/health")
async def health_check():
    """
    Health check endpoint
    
    Returns:
    - Server status
    - Installation ID
    - Environment info
    - Capacity metrics
    """
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "installation_id": settings.GITHUB_INSTALLATION_ID,
        "environment": settings.ENVIRONMENT,
        "version": "1.0.0",
        "capacity": "112K users/month",
        "rate_limit": "5000 requests/hour"
    }


@router.post("/cache/clear")
async def clear_cache():
    """
    Clear all cached data (admin only)
    
    WARNING: Use with caution in production!
    """
    try:
        await clear_all_cache()
        return {
            "status": "success",
            "message": "All cache cleared",
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Cache clear error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
