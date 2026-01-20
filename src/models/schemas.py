"""
Request and Response data models using Pydantic.

This module defines all data models for the GitHub User Data Analyzer API.
Models are used for request validation, response serialization, and 
automatic Swagger UI documentation generation.
"""
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Annotated
from datetime import datetime


# ============= INPUT MODELS =============

class AnalyzeRequest(BaseModel):
    """
    Request model for GitHub profile analysis.
    
    This accepts either a GitHub username or a full GitHub profile URL
    and normalizes it to extract the username for processing.
    """
    github_input: Annotated[
        str,
        Field(
            min_length=1,
            max_length=100,
            description="GitHub username or profile URL",
            examples=["torvalds", "https://github.com/torvalds"]
        )
    ]


class ReportRequest(BaseModel):
    """
    Request model for AI-powered candidate report generation.
    
    Generates comprehensive hiring reports using stored or fresh GitHub data.
    """
    username: Annotated[
        str,
        Field(
            min_length=1,
            max_length=100,
            description="""**GitHub Username** to generate report for.
            
Example: 'torvalds', 'octocat', etc.

This is the GitHub username (not URL) of the developer you want to assess.""",
            examples=["torvalds"]
        )
    ]
    
    report_type: Annotated[
        str,
        Field(
            default="full",
            description="""**Type of Report** to generate:

• **"full"** (Recommended) - Complete analysis with all sections:
  - Executive summary
  - Technical skills assessment  
  - Code quality analysis
  - Project complexity
  - Activity patterns
  - Hiring recommendations

• **"summary"** - Brief overview (1-2 paragraphs)

• **"technical"** - Focus on technical skills only

**Default:** "full" """,
            examples=["full", "summary", "technical"]
        )
    ] = "full"
    
    use_stored: Annotated[
        bool,
        Field(
            default=True,
            description="""**Use Stored Data?** (Performance optimization)

• **true** (Recommended) - Use previously analyzed data from `db/{username}.json` if available
  - [SUCCESS] **Much faster** (~2-3 seconds vs 5-10 seconds)
  - [SUCCESS] **Saves API calls**
  - [SUCCESS] **Same data** if user was analyzed recently
  - [WARN] Data might be slightly outdated

• **false** - Always fetch fresh data from GitHub
  - [SUCCESS] **Most current data**
  - [WARN] **Slower** (needs to fetch from GitHub first)
  - [WARN] **More API calls**

**How it works:**
1. When you analyze a user with `/analyze`, data is auto-saved to `db/{username}.json`
2. Later, when generating report:
   - `use_stored: true` → Loads from saved file (fast)
   - `use_stored: false` → Fetches fresh from GitHub (slow but current)
3. If no saved data exists, fresh fetch happens automatically

**Recommendation:** Use `true` unless you need the absolute latest commits (within last 24 hours).

**Default:** true""",
            examples=[True, False]
        )
    ] = True
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "username": "torvalds",
                    "report_type": "full",
                    "use_stored": True
                },
                {
                    "username": "octocat",
                    "report_type": "summary",
                    "use_stored": False
                }
            ]
        }
    }


# ============= OUTPUT MODELS =============

class UserData(BaseModel):
    """
    GitHub user profile data.
    
    Contains comprehensive information about a GitHub user including
    their public profile details, social metrics, and account metadata.
    """
    login: str = Field(..., description="GitHub username", examples=["torvalds"])
    name: Optional[str] = Field(None, description="Full name", examples=["Linus Torvalds"])
    bio: Optional[str] = Field(None, description="User bio/description", examples=["Creator of Linux"])
    location: Optional[str] = Field(None, description="Geographic location", examples=["Portland, OR"])
    followers: int = Field(..., description="Number of followers", examples=[250000])
    following: int = Field(..., description="Number of users following", examples=[50])
    public_repos: int = Field(..., description="Number of public repositories", examples=[5])
    created_at: str = Field(..., description="Account creation timestamp (ISO 8601)")
    updated_at: str = Field(..., description="Last profile update timestamp (ISO 8601)")
    avatar_url: str = Field(..., description="Profile picture URL")
    blog: Optional[str] = Field(None, description="Personal website/blog URL", examples=["https://kernel.org"])
    company: Optional[str] = Field(None, description="Company/organization", examples=["Linux Foundation"])


class LanguageStats(BaseModel):
    """
    Programming language statistics for a repository.
    
    Provides both raw byte counts and calculated percentages for all
    programming languages detected in the repository.
    """
    raw_bytes: Dict[str, int] = Field(
        ..., 
        description="Raw byte count per language",
        examples=[{"Python": 123456, "JavaScript": 45678}]
    )
    percentages: Dict[str, float] = Field(
        ..., 
        description="Percentage distribution of languages",
        examples=[{"Python": 73.1, "JavaScript": 26.9}]
    )


class MarkdownFile(BaseModel):
    """
    Individual markdown file information and content.
    
    Represents a single .md file found in the repository with its
    complete content (no truncation, all words included).
    """
    filename: str = Field(..., description="Markdown filename", examples=["CONTRIBUTING.md"])
    path: str = Field(..., description="Full path in repository", examples=["docs/CONTRIBUTING.md"])
    content: str = Field(..., description="Complete markdown file content (100% of text)")
    length_chars: int = Field(..., description="Character count", examples=[2450])


class ReadmeInfo(BaseModel):
    """
    README file information and content.
    
    Contains the complete README content along with metadata about
    its presence and length for quality assessment.
    """
    content: Optional[str] = Field(
        None, 
        description="Full README content in markdown format"
    )
    length_chars: int = Field(..., description="Character count of README", examples=[5234])
    has_readme: bool = Field(..., description="Whether repository has a README file", examples=[True])


class RepositoryData(BaseModel):
    """
    Complete repository information with popularity and activity metrics.
    
    This comprehensive model includes all relevant data for job portal candidate
    assessment: technical skills (languages), activity level (commits), code quality
    (stars/forks), and professional practices (documentation, organization).
    """
    # Basic Information
    name: str = Field(..., description="Repository name", examples=["linux"])
    full_name: str = Field(..., description="Full repository name with owner", examples=["torvalds/linux"])
    description: Optional[str] = Field(None, description="Repository description", examples=["Linux kernel source tree"])
    html_url: str = Field(..., description="Repository URL", examples=["https://github.com/torvalds/linux"])
    
    # Popularity Metrics (for quality assessment)
    stargazers_count: int = Field(..., description="Number of stars", examples=[180000])
    forks_count: int = Field(..., description="Number of forks", examples=[60000])
    watchers_count: int = Field(0, description="Number of watchers", examples=[180000])
    open_issues_count: int = Field(0, description="Number of open issues", examples=[1245])
    
    # Repository Metadata
    size_kb: int = Field(..., description="Repository size in kilobytes", examples=[1048576])
    language: Optional[str] = Field(None, description="Primary programming language", examples=["Python"])
    topics: List[str] = Field(..., description="Repository topics/tags", examples=[["machine-learning", "python"]])
    archived: bool = Field(..., description="Whether repository is archived", examples=[False])
    is_fork: bool = Field(..., description="Whether repository is a fork", examples=[False])
    has_wiki: bool = Field(False, description="Whether repository has wiki enabled", examples=[True])
    has_projects: bool = Field(False, description="Whether repository has projects enabled", examples=[False])
    
    # Timestamps (for activity assessment)
    created_at: str = Field(..., description="Repository creation timestamp (ISO 8601)")
    updated_at: str = Field(..., description="Last update timestamp (ISO 8601)")
    pushed_at: Optional[str] = Field(None, description="Last push timestamp (ISO 8601)")
    
    # Commit Activity (for developer activity assessment)
    last_commit_date: Optional[str] = Field(
        None, 
        description="Most recent commit timestamp (same as pushed_at)",
        examples=["2025-12-30T13:31:35Z"]
    )
    days_since_last_commit: Optional[int] = Field(
        None, 
        description="Days since last commit (for activity freshness)",
        examples=[1]
    )
    
    # Language Breakdown (for skill assessment)
    languages: LanguageStats = Field(..., description="Programming language distribution")
    
    # README Content (for project quality assessment)
    readme: Optional[ReadmeInfo] = Field(None, description="README file information")
    
    # All Markdown Files (complete documentation extraction)
    markdown_files: List[MarkdownFile] = Field(
        default_factory=list, 
        description="All .md files found in repository (COMPLETE content, no truncation)"
    )


class PerformanceMetrics(BaseModel):
    """
    API performance and caching metrics.
    
    Provides transparency into response times and cache effectiveness
    for monitoring and optimization purposes.
    """
    github_api_latency_ms: int = Field(..., description="Time spent on GitHub API calls (ms)", examples=[850])
    processing_latency_ms: int = Field(..., description="Time spent processing data (ms)", examples=[200])
    total_latency_ms: int = Field(..., description="Total response time (ms)", examples=[1050])
    cache_hit: bool = Field(..., description="Whether response was served from cache", examples=[False])
    cache_ttl_remaining_seconds: int = Field(..., description="Seconds until cache expires", examples=[86400])


class AnalyzeResponse(BaseModel):
    """
    Complete GitHub profile analysis response.
    
    This is the main response model containing all extracted data about a GitHub user:
    - User profile information
    - Repository details with languages and READMEs
    - Performance metrics
    - Cache information
    
    Perfect for job portal candidate assessment and AI-powered analysis.
    """
    status: str = Field(..., description="Response status", examples=["success"])
    request_id: str = Field(..., description="Unique request identifier", examples=["a3f8b2c1"])
    timestamp: str = Field(..., description="Response timestamp (ISO 8601)")
    user: UserData = Field(..., description="GitHub user profile data")
    repositories: List[RepositoryData] = Field(..., description="List of analyzed repositories (top 15 by stars)")
    total_repos_analyzed: int = Field(..., description="Number of repositories analyzed", examples=[15])
    total_api_calls: int = Field(..., description="Number of GitHub API calls made", examples=[32])
    performance: PerformanceMetrics = Field(..., description="Performance metrics")
    cache_info: Dict[str, bool] = Field(..., description="Cache hit information", examples=[{"hit": False}])


# ============= ERROR MODELS =============

class ErrorResponse(BaseModel):
    """
    Standard error response model.
    
    Returned when validation fails or an error occurs during processing.
    """
    status: str = Field("error", description="Response status")
    error_code: str = Field(..., description="Error code identifier", examples=["INVALID_USERNAME"])
    error_message: str = Field(..., description="Human-readable error message", examples=["User not found"])
    request_id: Optional[str] = Field(None, description="Request identifier for tracking")


class HealthResponse(BaseModel):
    """
    Health check response model.
    
    Provides server status and capacity information for monitoring.
    """
    status: str = Field(..., description="Server health status", examples=["healthy"])
    installation_id: int = Field(..., description="GitHub App installation ID")
    environment: str = Field(..., description="Deployment environment", examples=["production"])
    version: str = Field("1.0.0", description="API version")
    capacity: str = Field("112K users/month", description="Service capacity")
    rate_limit: str = Field("5000 requests/hour", description="GitHub API rate limit")


# ============= ENHANCED REPORT MODELS =============

class Technology(BaseModel):
    """
    Technology with factual usage data.
    
    Represents a single technology (language, framework, tool, or platform)
    with objective metrics about its usage across repositories.
    """
    name: str = Field(..., description="Technology name", examples=["Python", "React", "Docker"])
    category: str = Field(..., description="Technology category", examples=["language", "framework", "tool", "platform"])
    usage_percentage: float = Field(..., description="Percentage of total codebase", examples=[45.2])
    repository_count: int = Field(..., description="Number of repositories using this technology", examples=[8])
    recent_usage: bool = Field(..., description="Used in repositories updated within last 6 months", examples=[True])
    example_repositories: List[str] = Field(..., description="Example repositories using this technology", examples=[["repo1", "repo2"]])


class TechnologyAnalysis(BaseModel):
    """
    Complete technology stack analysis.
    
    Aggregates all technologies used across repositories with usage metrics.
    """
    technologies: List[Technology] = Field(..., description="All technologies with usage data")
    primary_stack: List[str] = Field(..., description="Main technologies (>20% usage)", examples=[["Python", "JavaScript"]])
    secondary_stack: List[str] = Field(..., description="Supporting technologies", examples=[["Docker", "PostgreSQL"]])
    technology_summary: str = Field(..., description="Brief summary of technology stack")


class ComplexityIndicators(BaseModel):
    """
    Objective complexity metrics for a repository.
    
    Provides factual indicators of project complexity and quality.
    """
    repository_size_kb: int = Field(..., description="Repository size in kilobytes", examples=[1500])
    stars: int = Field(..., description="GitHub stars count", examples=[120])
    has_documentation: bool = Field(..., description="Has README or documentation", examples=[True])
    has_tests_indicated: bool = Field(..., description="Indicates presence of tests", examples=[True])


class ProjectScope(BaseModel):
    """
    Factual project scope analysis for a repository.
    
    Provides business context and technical details about a specific project.
    """
    repository_name: str = Field(..., description="Repository name", examples=["ecommerce-platform"])
    business_domain: str = Field(..., description="Business/industry domain", examples=["E-commerce", "Healthcare", "Finance"])
    project_type: str = Field(..., description="Type of project", examples=["Web App", "Mobile App", "API", "Library"])
    complexity_indicators: ComplexityIndicators = Field(..., description="Objective complexity metrics")
    key_features: List[str] = Field(..., description="Main features of the project", examples=[["User authentication", "Payment processing"]])
    technologies_used: List[str] = Field(..., description="Technologies used in this project", examples=[["React", "Node.js", "PostgreSQL"]])
    production_signals: List[str] = Field(..., description="Indicators of production readiness", examples=[["CI/CD setup", "Docker deployment"]])
    scope_description: str = Field(..., description="What this project does and its purpose")


class Skill(BaseModel):
    """
    Skill with evidence from repositories.
    
    Represents a skill with factual evidence of usage.
    """
    name: str = Field(..., description="Skill name", examples=["Python", "Docker", "Documentation"])
    usage_percentage: Optional[float] = Field(None, description="Usage percentage (for languages)", examples=[45.2])
    category: Optional[str] = Field(None, description="Skill category", examples=["language", "tool", "soft_skill"])
    evidence: str = Field(..., description="Specific evidence from repositories", examples=["Used in 8 repositories including project-name"])


class ComprehensiveSkills(BaseModel):
    """
    Complete skills inventory with evidence.
    
    Categorizes all skills extracted from repositories.
    """
    programming_languages: List[Skill] = Field(..., description="Programming languages with usage data")
    frameworks_and_libraries: List[Skill] = Field(..., description="Frameworks and libraries used")
    tools_and_platforms: List[Skill] = Field(..., description="Tools and platforms (Docker, AWS, CI/CD, etc.)")
    soft_skills_indicators: List[Skill] = Field(..., description="Soft skills indicators from documentation and collaboration")
    domain_expertise: List[Skill] = Field(..., description="Domain expertise areas (ML, DevOps, Security, etc.)")


class DomainClassification(BaseModel):
    """
    Industry domain classification.
    
    Classifies developer's industry expertise based on project types and technologies.
    """
    primary_domain: str = Field(..., description="Primary industry domain", examples=["Healthcare", "Finance", "E-commerce"])
    secondary_domains: List[str] = Field(..., description="Secondary industry domains", examples=[["Education", "Marketing"]])
    specializations: List[str] = Field(..., description="Specialization areas within domains", examples=[["Medical Imaging", "Patient Management"]])
    evidence: str = Field(..., description="Evidence for domain classification from projects and technologies")
