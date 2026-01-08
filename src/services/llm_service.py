"""
Production-Grade LLM Service for AI-Powered Candidate Reports

Generates comprehensive, professional GitHub developer analysis reports
suitable for real-world hiring decisions.

Supports:
- GROQ Llama 3.3 70B (Primary - Fast & Cost-effective)
- OpenAI GPT-4o (Alternative)
- Google Gemini Pro (Alternative)
- Template fallback (no API key required)

Features:
- Technology stack analysis with usage metrics
- Project scope analysis per repository
- Comprehensive skills inventory
- Domain/industry classification
- Executive summaries and hiring recommendations
"""
import os
import json
import re
from typing import Dict, Any, Optional, List
from datetime import datetime
from utils.logger import logger


class LLMService:
    """
    Production-grade LLM service for candidate report generation.
    
    Generates comprehensive reports with:
    - Technology analysis (factual usage data)
    - Project scope analysis (business context)
    - Skills inventory (evidence-based)
    - Domain classification (industry expertise)
    - Executive summaries
    - Technical assessments
    - Hiring recommendations
    """
    
    def __init__(self):
        """Initialize LLM service with configuration from environment."""
        from core.config import settings
        
        self.settings = settings
        self.max_tokens = settings.LLM_MAX_TOKENS
        self.temperature = settings.LLM_TEMPERATURE
        
        # Priority 1: Check for Ollama (local, zero cost)
        if settings.USE_OLLAMA:
            self.provider = "ollama"
            self.api_key = None  # Ollama doesn't need API key
            self.model = settings.OLLAMA_MODEL
            self.ollama_url = settings.OLLAMA_URL
            logger.info(f"🚀 LLM Service: Ollama {self.model} (Local, Zero Cost)")
            logger.info(f"📍 Ollama URL: {self.ollama_url}")
        
        # Priority 2: Check for GROQ (cloud, fast & cheap)
        elif settings.GROQ_API_KEY:
            self.provider = "groq"
            self.api_key = settings.GROQ_API_KEY
            self.model = settings.LLM_MODEL
            logger.info(f"🚀 LLM Service: GROQ {self.model}")
        
        # Priority 3: Fallback to other cloud providers
        else:
            self.provider = settings.LLM_PROVIDER if settings.LLM_PROVIDER else "openai"
            self.model = settings.LLM_MODEL
            
            if self.provider == "openai":
                self.api_key = settings.OPENAI_API_KEY
                if self.api_key:
                    logger.info(f"🤖 LLM Service: OpenAI {self.model}")
                else:
                    logger.warning("⚠️ OPENAI_API_KEY not configured")
                    self.api_key = None
                    
            elif self.provider == "gemini":
                self.api_key = settings.GOOGLE_API_KEY
                if self.api_key:
                    logger.info(f"🤖 LLM Service: Gemini Pro")
                else:
                    logger.warning("⚠️ GOOGLE_API_KEY not configured")
                    self.api_key = None
            else:
                logger.warning(f"⚠️ Unknown provider '{self.provider}', using template mode")
                self.api_key = None
    
    def generate_report(self, data: Dict[str, Any], report_type: str = "full") -> Dict[str, Any]:
        """
        Generate professional candidate report from GitHub data.
        
        Args:
            data: Complete GitHub analysis (user + repositories with markdown files)
            report_type: "summary" | "full" | "technical"
        
        Returns:
            Structured report with comprehensive candidate assessment
        """
        try:
            # Try Ollama first if enabled
            if self.provider == "ollama":
                return self._generate_with_ollama(data, report_type)
            
            # Cloud providers require API key
            elif not self.api_key:
                logger.info("📝 Using template report (no API key)")
                return self._generate_template_report(data, report_type)
            
            elif self.provider == "groq":
                return self._generate_with_groq(data, report_type)
            elif self.provider == "openai":
                return self._generate_with_openai(data, report_type)
            elif self.provider == "gemini":
                return self._generate_with_gemini(data, report_type)
            else:
                return self._generate_template_report(data, report_type)
                
        except Exception as e:
            logger.error(f"❌ LLM generation failed: {e}")
            logger.info("📝 Falling back to template report")
            return self._generate_template_report(data, report_type)
    
    def _generate_with_ollama(self, data: Dict[str, Any], report_type: str) -> Dict[str, Any]:
        \"\"\"Generate report using local Ollama (zero cost, local inference).\"\"\"
        import requests
        
        prompt = self._build_detailed_prompt(data, report_type)
        
        logger.info(f\"🚀 Generating report with Ollama {self.model} (local)...\")
        
        try:
            response = requests.post(
                f\"{self.ollama_url}/api/generate\",
                json={
                    \"model\": self.model,
                    \"prompt\": prompt,
                    \"stream\": False,
                    \"options\": {
                        \"temperature\": self.temperature,
                        \"num_predict\": self.max_tokens
                    }
                },
                timeout=120  # 2 minute timeout for local generation
            )
            
            if response.status_code == 200:
                report_text = response.json()[\"response\"]
                logger.info(\"✅ Ollama report generated successfully\")
                return self._parse_llm_response(report_text, data)
            else:
                raise Exception(f\"Ollama HTTP {response.status_code}: {response.text}\")
                
        except requests.exceptions.ConnectionError:
            logger.error(\"❌ Cannot connect to Ollama. Is it running? Try: ollama serve\")
            # Fallback to GROQ if available
            if self.settings.GROQ_API_KEY:
                logger.info(\"🔄 Falling back to GROQ...\")
                self.provider = \"groq\"
                self.api_key = self.settings.GROQ_API_KEY
                self.model = self.settings.LLM_MODEL
                return self._generate_with_groq(data, report_type)
            else:
                logger.info(\"📝 Falling back to template report\")
                return self._generate_template_report(data, report_type)
                
        except Exception as e:
            logger.error(f\"❌ Ollama generation failed: {e}\")
            # Fallback to GROQ if available
            if self.settings.GROQ_API_KEY:
                logger.info(\"🔄 Falling back to GROQ...\")
                self.provider = \"groq\"
                self.api_key = self.settings.GROQ_API_KEY
                self.model = self.settings.LLM_MODEL
                return self._generate_with_groq(data, report_type)
            else:
                logger.info(\"📝 Falling back to template report\")
                return self._generate_template_report(data, report_type)
    
    def _generate_with_groq(self, data: Dict[str, Any], report_type: str) -> Dict[str, Any]:
        """Generate report using GROQ Llama 3.3 70B."""
        from groq import Groq
        
        # GROQ client only needs API key
        client = Groq(api_key=self.api_key)
        prompt = self._build_detailed_prompt(data, report_type)
        
        logger.info(f"🚀 Generating report with GROQ {self.model}...")
        
        response = client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": """You are an expert technical recruiter and senior engineering manager 
with 15+ years of experience evaluating GitHub profiles for hiring decisions. You provide 
detailed, data-driven assessments with specific evidence and actionable recommendations."""
                },
                {"role": "user", "content": prompt}
            ],
            temperature=self.temperature,
            max_tokens=self.max_tokens
        )
        
        report_text = response.choices[0].message.content
        return self._parse_llm_response(report_text, data)
    
    def _generate_with_openai(self, data: Dict[str, Any], report_type: str) -> Dict[str, Any]:
        """Generate report using OpenAI GPT-4."""
        import openai
        
        openai.api_key = self.api_key
        prompt = self._build_detailed_prompt(data, report_type)
        
        logger.info(f"🤖 Generating report with OpenAI {self.model}...")
        
        response = openai.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": """You are an expert technical recruiter and senior engineering manager 
with 15+ years of experience evaluating GitHub profiles for hiring decisions. You provide 
detailed, data-driven assessments with specific evidence and actionable recommendations."""
                },
                {"role": "user", "content": prompt}
            ],
            temperature=self.temperature,
            max_tokens=self.max_tokens
        )
        
        report_text = response.choices[0].message.content
        return self._parse_llm_response(report_text, data)
    
    def _generate_with_gemini(self, data: Dict[str, Any], report_type: str) -> Dict[str, Any]:
        """Generate report using Google Gemini."""
        import google.generativeai as genai
        
        genai.configure(api_key=self.api_key)
        model = genai.GenerativeModel('gemini-pro')
        prompt = self._build_detailed_prompt(data, report_type)
        
        logger.info("🤖 Generating report with Gemini Pro...")
        
        response = model.generate_content(prompt)
        report_text = response.text
        
        return self._parse_llm_response(report_text, data)
    
    def _build_detailed_prompt(self, data: Dict[str, Any], report_type: str) -> str:
        """Build comprehensive prompt with enhanced data extraction for production-quality reports."""
        user = data.get("user", {})
        repos = data.get("repositories", [])
        
        # Calculate comprehensive metrics
        metrics = self._calculate_metrics(user, repos)
        
        prompt = f"""# GitHub Developer Analysis - Factual Data Extraction

**CANDIDATE:** {user.get('login')}
**REPOSITORIES ANALYZED:** {len(repos)}
**TOTAL STARS:** {metrics['total_stars']}
**ACCOUNT AGE:** {metrics['account_age_years']} years

**QUANTITATIVE METRICS:**
- Public Repositories: {metrics['total_repos']}
- Total Stars: {metrics['total_stars']}
- Total Forks: {metrics['total_forks']}
- Documentation Coverage: {metrics['repos_with_readme']}/{metrics['total_repos']} ({metrics['documentation_percentage']:.0f}%)
- Additional Markdown Files: {metrics['total_markdown_files']} files
- Last Commit: {metrics['days_since_last_commit']} days ago
- Active Repos (< 90 days): {metrics['active_repos_count']}

**PRIMARY TECHNOLOGIES:**
{self._format_languages(metrics['language_distribution'])}

**TOP REPOSITORIES:**
{self._format_top_repos(repos[:10])}

---

## EXTRACTION REQUIREMENTS

Extract FACTUAL, EVIDENCE-BASED data from GitHub repositories.
Return ONLY valid JSON (no markdown code blocks).

```json
{{
  "technology_analysis": {{
    "technologies": [
      {{
        "name": "Python",
        "category": "language",
        "usage_percentage": 45.2,
        "repository_count": 8,
        "recent_usage": true,
        "example_repositories": ["repo1", "repo2"]
      }}
    ],
    "primary_stack": ["Python", "JavaScript"],
    "secondary_stack": ["Docker", "PostgreSQL"],
    "technology_summary": "Full-stack developer with Python/JavaScript expertise"
  }},
  
  "project_scope_analysis": [
    {{
      "repository_name": "project-name",
      "business_domain": "E-commerce",
      "project_type": "Web App",
      "complexity_indicators": {{
        "repository_size_kb": 1500,
        "stars": 120,
        "has_documentation": true,
        "has_tests_indicated": true
      }},
      "key_features": ["User authentication", "Payment processing"],
      "technologies_used": ["React", "Node.js", "PostgreSQL"],
      "production_signals": ["CI/CD setup", "Docker deployment"],
      "scope_description": "Full-stack e-commerce platform with payment integration"
    }}
  ],
  
  "comprehensive_skills": {{
    "programming_languages": [
      {{
        "name": "Python",
        "usage_percentage": 45.2,
        "category": "language",
        "evidence": "Used in 8 repositories including project-name"
      }}
    ],
    "frameworks_and_libraries": [
      {{
        "name": "React",
        "category": "frontend",
        "evidence": "Used in 3 web applications"
      }}
    ],
    "tools_and_platforms": [
      {{
        "name": "Docker",
        "category": "containerization",
        "evidence": "Dockerfiles found in 5 repositories"
      }}
    ],
    "soft_skills_indicators": [
      {{
        "name": "Documentation",
        "evidence": "85% of repos have comprehensive READMEs"
      }}
    ],
    "domain_expertise": [
      {{
        "name": "DevOps",
        "evidence": "CI/CD pipelines, Docker usage"
      }}
    ]
  }},
  
  "domain_classification": {{
    "primary_domain": "E-commerce",
    "secondary_domains": ["Finance"],
    "specializations": ["Payment Processing"],
    "evidence": "3 e-commerce projects with payment integration"
  }},
  
  "executive_summary": "2-3 paragraph professional assessment",
  
  "technical_assessment": {{
    "overall_score": 7.5,
    "primary_languages": ["Python", "JavaScript"],
    "language_proficiency": {{
      "Python": {{"score": 8, "evidence": "45% of codebase"}},
      "JavaScript": {{"score": 7, "evidence": "30% of codebase"}}
    }},
    "frameworks_detected": ["React", "FastAPI"],
    "specializations": ["Full-stack"],
    "technical_depth": "Mid to Senior level",
    "learning_trajectory": "Active learner"
  }},
  
  "code_quality": {{
    "overall_score": 8.0,
    "documentation_score": 8.5,
    "documentation_evidence": "{metrics['repos_with_readme']} of {metrics['total_repos']} repos have READMEs",
    "project_structure": "Professional",
    "best_practices": ["Good documentation"],
    "areas_to_verify": ["Test coverage"]
  }},
  
  "project_analysis": {{
    "complexity_assessment": "Medium to High",
    "notable_projects": [
      {{
        "name": "project-name",
        "description": "What it does",
        "technical_highlights": ["React"],
        "impact_indicators": "XX stars",
        "assessment": "Demonstrates skill"
      }}
    ],
    "project_diversity": "Good range",
    "production_readiness": "Production-ready projects"
  }},
  
  "activity_profile": {{
    "consistency_score": 7.0,
    "recent_activity": "Last commit {metrics['days_since_last_commit']} days ago",
    "activity_pattern": "Regular contributor",
    "active_repos": {metrics['active_repos_count']},
    "maintenance_indicator": "Active",
    "collaboration_evidence": "Good documentation",
    "commit_frequency_assessment": "Consistent"
  }},
  
  "strengths": ["Strength with evidence"],
  "areas_for_improvement": ["Area to improve"],
  
  "hiring_recommendation": {{
    "overall_score": 7.5,
    "confidence_level": "High",
    "suitable_roles": ["Full-stack Developer"],
    "seniority_fit": "Mid-level to Senior",
    "team_fit_indicators": "Good documentation",
    "red_flags": [],
    "green_flags": ["Strong documentation"],
    "salary_bracket_suggestion": "Based on skills",
    "recommendation_summary": "Detailed recommendation",
    "next_steps": ["Technical interview"]
  }},
  
  "metadata": {{
    "analysis_confidence": "High",
    "data_completeness": "90%",
    "additional_notes": "Any caveats"
  }}
}}
```

## INSTRUCTIONS

### Technology Analysis
- Aggregate ALL languages, frameworks, tools, platforms
- Calculate usage % from language stats
- Count repos using each tech
- Check if used in last 6 months
- List 2-3 example repos
- Primary stack = >20% usage

### Project Scope (top 10 repos)
- Business domain: E-commerce, Healthcare, Finance, Education, Marketing, IT/Software, etc.
- Project type: Web App, Mobile App, API, Library, CLI Tool
- Extract complexity indicators
- List key features from README
- Identify technologies in THIS project
- Note production signals: CI/CD, Docker, tests

### Skills
- Languages with usage %
- Frameworks from topics/README
- Tools: Docker, AWS, CI/CD, databases
- Soft skills from documentation
- Domain expertise: ML, DevOps, Security
- Specific evidence for each

### Domain Classification
- Primary industry from projects
- Secondary domains if applicable
- Specialization areas
- Evidence from projects

## RULES
✅ Return ONLY JSON (no markdown blocks)
✅ Every field needs evidence
✅ Use actual repo names
✅ Be precise with numbers
✅ null or [] if unavailable

Generate now:"""
        
        return prompt
    
    def _calculate_metrics(self, user: Dict, repos: List[Dict]) -> Dict[str, Any]:
        """Calculate comprehensive metrics from profile data."""
        from datetime import datetime
        
        total_repos = len(repos)
        total_stars = sum(r.get("stargazers_count", 0) for r in repos)
        total_forks = sum(r.get("forks_count", 0) for r in repos)
        
        # Language distribution
        lang_totals = {}
        for repo in repos:
            lang_pct = repo.get("languages", {}).get("percentages", {})
            for lang, pct in lang_pct.items():
                lang_totals[lang] = lang_totals.get(lang, 0) + pct
        
        # Normalize and get top languages
        if lang_totals:
            total_pct = sum(lang_totals.values())
            lang_distribution = {
                lang: round((pct / total_pct) * 100, 1)
                for lang, pct in lang_totals.items()
            }
        else:
            lang_distribution = {}
        
        # Documentation metrics
        repos_with_readme = sum(1 for r in repos if r.get("readme"))
        total_markdown_files = sum(len(r.get("markdown_files", [])) for r in repos)
        
        # Activity metrics
        days_since_last = []
        for repo in repos:
            days = repo.get("days_since_last_commit")
            if days is not None:
                days_since_last.append(days)
        
        min_days_since_commit = min(days_since_last) if days_since_last else None
        active_repos = sum(1 for d in days_since_last if d < 90)
        
        # Account age
        created_at = user.get("created_at", "")
        try:
            created_date = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
            account_age_years = round((datetime.now(created_date.tzinfo) - created_date).days / 365.25, 1)
        except:
            account_age_years = 0
        
        # Quality indicators
        repos_with_wiki = sum(1 for r in repos if r.get("has_wiki"))
        repos_with_projects = sum(1 for r in repos if r.get("has_projects"))
        total_topics = sum(len(r.get("topics", [])) for r in repos)
        avg_repo_size = sum(r.get("size_kb", 0) for r in repos) / total_repos if total_repos > 0 else 0
        
        return {
            "total_repos": total_repos,
            "total_stars": total_stars,
            "total_forks": total_forks,
            "avg_stars_per_repo": total_stars / total_repos if total_repos > 0 else 0,
            "repos_with_readme": repos_with_readme,
            "documentation_percentage": (repos_with_readme / total_repos * 100) if total_repos > 0 else 0,
            "total_markdown_files": total_markdown_files,
            "days_since_last_commit": min_days_since_commit if min_days_since_commit else "N/A",
            "active_repos_count": active_repos,
            "account_age_years": account_age_years,
            "language_distribution": dict(sorted(lang_distribution.items(), key=lambda x: x[1], reverse=True)[:10]),
            "repos_with_wiki": repos_with_wiki,
            "repos_with_projects": repos_with_projects,
            "total_topics": total_topics,
            "avg_repo_size_kb": avg_repo_size
        }
    
    def _format_languages(self, lang_dist: Dict[str, float]) -> str:
        """Format language distribution for prompt."""
        if not lang_dist:
            return "- No language data available"
        
        lines = []
        for lang, pct in list(lang_dist.items())[:5]:
            lines.append(f"- **{lang}**: {pct:.1f}% of codebase")
        return "\n".join(lines)
    
    def _format_top_repos(self, repos: List[Dict]) -> str:
        """Format top repositories for prompt."""
        if not repos:
            return "- No repositories found"
        
        lines = []
        for i, repo in enumerate(repos, 1):
            lines.append(f"\n**{i}. {repo['name']}** ({repo.get('language', 'Unknown')})")
            lines.append(f"   - ⭐ {repo['stargazers_count']} stars, 🍴 {repo['forks_count']} forks")
            if repo.get('description'):
                lines.append(f"   - Description: {repo['description']}")
            if repo.get('topics'):
                lines.append(f"   - Topics: {', '.join(repo['topics'][:5])}")
            if repo.get('readme'):
                readme_len = repo['readme'].get('length_chars', 0)
                lines.append(f"   - README: {readme_len} characters")
            md_files = repo.get('markdown_files', [])
            if md_files:
                lines.append(f"   - Additional Docs: {len(md_files)} markdown files")
        
        return "\n".join(lines)
    
    def _parse_llm_response(self, response_text: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse LLM JSON response into structured format."""
        try:
            # Extract JSON from response (handle markdown code blocks)
            json_match = re.search(r'```json\n(.*?)\n```', response_text, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
            else:
                # Try to find raw JSON
                json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
                if json_match:
                    json_str = json_match.group()
                else:
                    raise ValueError("No JSON found in LLM response")
            
            report_data = json.loads(json_str)
            user = data.get("user", {})
            
            return {
                "status": "success",
                "report": {
                    "candidate": {
                        "name": user.get("name"),
                        "username": user.get("login"),
                        "profile_url": f"https://github.com/{user.get('login')}",
                        "avatar_url": user.get("avatar_url"),
                        "bio": user.get("bio"),
                        "location": user.get("location"),
                        "company": user.get("company")
                    },
                    **report_data
                },
                "generated_at": datetime.utcnow().isoformat() + "Z",
                "provider": self.provider,
                "model": self.model
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to parse LLM response: {e}")
            logger.warning("📝 Falling back to template report")
            return self._generate_template_report(data, "full")
    
    def _generate_template_report(self, data: Dict[str, Any], report_type: str) -> Dict[str, Any]:
        """Generate high-quality template report (works without API key)."""
        user = data.get("user", {})
        repos = data.get("repositories", [])
        
        metrics = self._calculate_metrics(user, repos)
        top_langs = list(metrics['language_distribution'].items())[:3]
        
        return {
            "status": "success",
            "report": {
                "candidate": {
                    "name": user.get("name", "Unknown"),
                    "username": user.get("login", "Unknown"),
                    "profile_url": f"https://github.com/{user.get('login', '')}",
                    "avatar_url": user.get("avatar_url"),
                    "bio": user.get("bio"),
                    "location": user.get("location"),
                    "company": user.get("company")
                },
                "executive_summary": f"GitHub developer with {metrics['total_repos']} public repositories and {metrics['total_stars']} total stars. Primary technologies include {', '.join([l[0] for l in top_langs])}. Account active for {metrics['account_age_years']} years with last commit {metrics['days_since_last_commit']} days ago. Documentation coverage at {metrics['documentation_percentage']:.0f}% with {metrics['total_markdown_files']} additional markdown files.",
                "technical_assessment": {
                    "overall_score": 7.0,
                    "primary_languages": [l[0] for l in top_langs],
                    "specializations": ["Based on repository analysis"],
                    "technical_depth": "Mid-level"
                },
                "code_quality": {
                    "overall_score": 7.0,
                    "documentation_score": min(10, metrics['documentation_percentage'] / 10),
                    "documentation_evidence": f"{metrics['repos_with_readme']} of {metrics['total_repos']} repos have README, plus {metrics['total_markdown_files']} additional markdown files"
                },
                "activity_profile": {
                    "recent_activity": f"Last commit {metrics['days_since_last_commit']} days ago",
                    "active_repos": metrics['active_repos_count'],
                    "consistency_score": 7.0
                },
                "hiring_recommendation": {
                    "overall_score": 7.0,
                    "suitable_roles": [f"{lang} Developer" for lang, _ in top_langs],
                    "seniority_fit": "Mid-level",
                    "recommendation_summary": "Candidate shows active development. Configure LLM API key for detailed AI analysis."
                }
            },
            "generated_at": datetime.utcnow().isoformat() + "Z",
            "provider": "template",
            "model": "template",
            "note": "LLM not configured. Using template report. Add GROQ_API_KEY, OPENAI_API_KEY, or GOOGLE_API_KEY for AI-powered analysis."
        }


# Singleton instance
llm_service = LLMService()
