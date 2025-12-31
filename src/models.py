"""Request and Response data models using Pydantic"""
from pydantic import BaseModel, Field
from typing import Dict, List, Optional
from datetime import datetime


# ============= INPUT MODELS =============

class AnalyzeRequest(BaseModel):
    """Request model for GitHub profile analysis"""
    github_input: str = Field(
        ..., 
        description="GitHub username or URL (e.g., 'torvalds' or 'https://github.com/torvalds')"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "github_input": "torvalds"
            }
        }


# ============= OUTPUT MODELS =============

class UserData(BaseModel):
    """GitHub user profile data"""
    login: str
    name: Optional[str] = None
    bio: Optional[str] = None
    location: Optional[str] = None
    followers: int
    following: int
    public_repos: int
    created_at: str
    updated_at: str
    avatar_url: str
    blog: Optional[str] = None
    company: Optional[str] = None


class LanguageStats(BaseModel):
    """Language breakdown for a repository"""
    raw_bytes: Dict[str, int]
    percentages: Dict[str, float]


class ReadmeInfo(BaseModel):
    """README file information"""
    content: Optional[str] = None
    length_chars: int
    has_readme: bool


class RepositoryData(BaseModel):
    """Complete repository information with popularity and activity metrics"""
    name: str
    full_name: str
    description: Optional[str] = None
    html_url: str
    
    # Popularity metrics
    stargazers_count: int
    forks_count: int
    watchers_count: int = 0
    open_issues_count: int = 0
    
    # Repository metadata
    size_kb: int
    language: Optional[str] = None
    topics: List[str]
    archived: bool
    is_fork: bool
    has_wiki: bool = False
    has_projects: bool = False
    
    # Timestamps
    created_at: str
    updated_at: str
    pushed_at: Optional[str] = None
    
    # Commit activity (NEW!)
    last_commit_date: Optional[str] = None
    days_since_last_commit: Optional[int] = None
    
    # Language breakdown
    languages: LanguageStats
    
    # README content
    readme: Optional[ReadmeInfo] = None


class PerformanceMetrics(BaseModel):
    """API performance metrics"""
    github_api_latency_ms: int
    processing_latency_ms: int
    total_latency_ms: int
    cache_hit: bool
    cache_ttl_remaining_seconds: int


class AnalyzeResponse(BaseModel):
    """Complete analysis response"""
    status: str
    request_id: str
    timestamp: str
    user: UserData
    repositories: List[RepositoryData]
    total_repos_analyzed: int
    total_api_calls: int
    performance: PerformanceMetrics
    cache_info: Dict[str, bool]


# ============= ERROR MODELS =============

class ErrorResponse(BaseModel):
    """Standard error response"""
    status: str = "error"
    error_code: str
    error_message: str
    request_id: Optional[str] = None


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    installation_id: int
    environment: str
    version: str = "1.0.0"
    capacity: str = "112K users/month"
    rate_limit: str = "5000 requests/hour"
