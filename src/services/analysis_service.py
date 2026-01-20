"""
Production-Grade Deterministic Analysis Service (Refactored)

Orchestrates modular analyzers to generate comprehensive GitHub developer analysis reports.
Uses pure Python heuristics with zero LLM usage required.

Architecture:
- Modular design with separate analyzer components
- Clean separation of concerns
- Easy to test and maintain

Components:
- DomainClassifier: Domain detection with weighted scoring
- TechAnalyzer: Technology stack analysis
- ScoringEngine: Metrics calculation and scoring
- RoleRecommender: Role recommendation logic
"""
from typing import Dict, Any, List
from datetime import datetime
from utils.logger import logger

# Import modular analyzers
from modules.analyzers.domain_classifier import domain_classifier
from modules.analyzers.tech_analyzer import tech_analyzer
from modules.analyzers.scoring_engine import scoring_engine
from modules.analyzers.role_recommender import role_recommender
from modules.analyzers.dependency_parser import dependency_parser
from modules.analyzers.readme_analyzer import readme_analyzer
from modules.analyzers.keyword_extractor import keyword_extractor
from modules.analyzers.markdown_analyzer import markdown_analyzer
from modules.analyzers.statistical_keyword_extractor import statistical_keyword_extractor


class AnalysisService:
    """
    Orchestrates modular analyzers to generate comprehensive analysis reports.
    
    This service coordinates the analysis workflow without containing business logic.
    All analysis logic is delegated to specialized analyzer modules.
    """
    
    def __init__(self):
        """Initialize service."""
        from core.config import settings
        self.settings = settings
        logger.info("[SYSTEM] Analysis Service (Deterministic Mode - Modular) Initialized")
        self.provider = "deterministic"
        self.model = "rule-engine-v3-modular"
    
    def generate_report(self, data: Dict[str, Any], report_type: str = "full") -> Dict[str, Any]:
        """
        Generate comprehensive analysis report.
        
        Args:
            data: Dict containing user and repositories data
            report_type: Type of report (currently only "full" supported)
            
        Returns:
            Complete analysis report as dict
        """
        try:
            logger.info("[REPORT] Generating modular deterministic report...")
            return self._generate_deterministic_report(data)
        except Exception as e:
            logger.error(f"[ERROR] Report generation failed: {e}", exc_info=True)
            return self._generate_fallback(data)
    
    def _generate_deterministic_report(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Core report generation logic using modular analyzers.
        
        Workflow:
        1. Calculate metrics (ScoringEngine)
        2. Analyze technologies (TechAnalyzer)
        3. Classify domains (DomainClassifier)
        4. Analyze projects (DomainClassifier + TechAnalyzer)
        5. Compile skills (TechAnalyzer)
        6. Calculate scores (ScoringEngine)
        7. Generate summary
        8. Recommend roles (RoleRecommender)
        9. Assemble final report
        """
        user = data.get("user", {})
        repos = data.get("repositories", [])
        
        # Step 0: Parse dependency files from all repos
        all_dependencies = []
        for repo in repos:
            dependency_files = repo.get("dependency_files", {})
            if dependency_files:
                parsed = dependency_parser.parse_all(dependency_files)
                all_dependencies.extend(parsed)
        
        logger.info(f"[DATA] Parsed {len(all_dependencies)} total dependencies from {len(repos)} repositories")
        
        # Step 1: Calculate raw metrics
        metrics = scoring_engine.calculate_metrics(user, repos)
        
        # Step 2: Analyze technology stack
        tech_analysis = tech_analyzer.analyze_technologies(
            repos,
            metrics['language_distribution']
        )
        
        # Step 3: Classify domains
        domain_analysis = domain_classifier.classify_repositories(repos)
        
        # Step 4: Analyze projects (combines domain + tech info)
        project_analysis = self._analyze_projects(repos, domain_analysis, tech_analysis)
        
        # Step 5: Compile comprehensive skills (with dependency enrichment)
        skills = self._compile_skills(tech_analysis, domain_analysis, metrics, repos, all_dependencies)
        
        # Step 6: Calculate scores
        scores = scoring_engine.calculate_scores(metrics, tech_analysis)
        
        # Step 7: Generate executive summary
        summary = self._generate_summary(user, metrics, tech_analysis, domain_analysis, skills)
        
        # Step 8: Generate role recommendation (with framework awareness!)
        # Add frameworks to tech_analysis for role detection
        tech_analysis_with_frameworks = {
            **tech_analysis,
            'detected_frameworks': skills.get('frameworks_and_libraries', [])
        }
        recommendation = role_recommender.recommend_role(
            domain_analysis,
            tech_analysis_with_frameworks,
            scores,
            metrics
        )
        
        # Step 9: Assemble final report
        return self._assemble_report(
            user, tech_analysis, project_analysis, skills,
            domain_analysis, summary, scores, metrics, recommendation
        )
    
    def _analyze_projects(
        self,
        repos: List[Dict],
        domain_analysis: Dict,
        tech_analysis: Dict
    ) -> List[Dict]:
        """
        Analyze individual projects combining domain and tech information.
        NOW INCLUDES: Keyword extraction for job matching!
        
        Args:
            repos: List of repository data
            domain_analysis: Domain classification results
            tech_analysis: Technology analysis results
            
        Returns:
            List of project analysis dicts with keywords
        """
        projects = []
        
        for repo in repos:
            text = (repo.get('description') or "") + " " + " ".join(repo.get('topics') or [])
            text = text.lower()
            
            # Get domain for this repo
            repo_domain, _ = domain_classifier.classify_repository(repo)
            
            # ENHANCED EXTRACTION: Pattern + Statistical keywords
            # 1. Pattern-based extraction (existing)
            pattern_keywords = keyword_extractor.extract_keywords(repo)
            
            # 2. Statistical extraction (NEW - finds compound terms)
            # Wrapped in try-except for graceful fallback if data is missing
            try:
                all_markdown = markdown_analyzer.extract_all_content(repo)
                combined_text = markdown_analyzer.combine_all_text(all_markdown)
                
                if combined_text.strip():
                    statistical_kws = statistical_keyword_extractor.extract(combined_text, max_keywords=20)
                    # Filter for technical keywords only
                    technical_stat_kws = statistical_keyword_extractor.filter_technical(
                        statistical_kws, 
                        threshold=0.3  # YAKE: lower = better
                    )
                    
                    # Merge pattern + statistical keywords
                    merged_all = statistical_keyword_extractor.merge_with_patterns(
                        technical_stat_kws,
                        pattern_keywords.get('all_keywords', []),
                        prefer_statistical=False  # Prefer pattern matches (more precise)
                    )
                    
                    # Update pattern keywords with merged results
                    pattern_keywords['all_keywords'] = merged_all[:15]  # Top 15
            except Exception as e:
                # Fallback: use pattern-based keywords only
                logger.warning(f"[ENHANCED_EXTRACTION] Statistical extraction failed, using pattern-only: {e}")
            
            keywords = pattern_keywords
            
            # Detect technologies used
            detected_techs = set()
            for kw, category in tech_analyzer.all_tech_keywords.items():
                if tech_analyzer._keyword_matches(kw, text):
                    detected_techs.add(kw)
            
            # Infer project type
            p_type = self._infer_project_type(text)
            
            # Get primary languages
            repo_langs = sorted(
                repo.get('languages', {}).get('percentages', {}).items(),
                key=lambda x: x[1],
                reverse=True
            )
            tech_used = [l[0] for l in repo_langs[:2]] + list(detected_techs)[:3]
            
            # Get features
            features = repo.get('topics', [])[:3]
            if not features:
                features = [f"{repo_domain} project"]
            
            # CRISP DESCRIPTION (max 15 words, one sentence)
            try:
                crisp_desc = self._generate_crisp_description(
                    repo, tech_used, repo_domain, keywords
                )
            except Exception as e:
                # Fallback to simple description
                logger.warning(f"[CRISP_DESC] Generation failed, using fallback: {e}")
                crisp_desc = repo.get('description') or f"{repo_domain} project"
            
            projects.append({
                "repository_name": repo['name'],
                "business_domain": repo_domain,
                "project_type": p_type,
                "complexity_indicators": {
                    "repository_size_kb": repo.get('size_kb'),
                    "stars": repo.get('stargazers_count', 0),
                    "has_documentation": bool(repo.get('readme')),
                },
                "key_features": features,
                "technologies_used": tech_used,
                "production_signals": [],
                "scope_description": crisp_desc,
                
                "keywords": keywords
            })
        
        return projects[:10]
    
    def _infer_project_type(self, text: str) -> str:
        """Infer project type from description text."""
        if "api" in text or "backend" in text or "microservice" in text:
            return "API Service"
        elif "library" in text or "sdk" in text or "package" in text:
            return "Library"
        elif "cli" in text or "tool" in text:
            return "CLI Tool"
        elif "mobile" in text or "app" in text:
            return "Mobile App"
        elif "model" in text or "training" in text or "dataset" in text:
            return "AI Model"
        elif "notebook" in text or "analysis" in text:
            return "Data Analysis"
        else:
            return "Web App"
    
    def _generate_crisp_description(
        self, 
        repo: Dict, 
        tech_used: List[str], 
        domain: str, 
        keywords: Dict
    ) -> str:
        """
        Generate crisp one-sentence project description (max 15 words).
        
        Args:
            repo: Repository data
            tech_used: List of detected technologies
            domain: Business domain
            keywords: Extracted keywords dict
            
        Returns:
            Short, crisp description (one sentence, ≤ 15 words)
        """
        # Priority 1: Use existing repo description if it's short enough
        repo_desc = repo.get('description', '').strip()
        if repo_desc:
            # Take first sentence only
            first_sentence = repo_desc.split('.')[0].strip()
            words = first_sentence.split()
            
            if len(words) <= 15:
                # Perfect! Use as-is
                return first_sentence
            else:
                # Truncate to 15 words
                return ' '.join(words[:15]) + '...'
        
        # Priority 2: Construct from domain + top technologies
        top_techs = tech_used[:2] if tech_used else []
        
        if top_techs:
            tech_str = ' and '.join(top_techs)
            return f"{domain} project using {tech_str}"
        else:
            # Fallback: domain only
            return f"{domain} project"
    
    def _compile_skills(
        self,
        tech_analysis: Dict,
        domain_analysis: Dict,
        metrics: Dict,
        repos: List[Dict],
        parsed_dependencies: List[Dict] = None
    ) -> Dict:
        """
        Compile comprehensive skills from all analysis results.
        
        Args:
            tech_analysis: Technology analysis results
            domain_analysis: Domain classification results
            metrics: Calculated metrics
            repos: Repository data
            parsed_dependencies: Parsed dependencies from manifest files
            
        Returns:
            Dict with programming_languages, frameworks_and_libraries, etc.
        """
        # Programming languages from tech analysis
        languages = [{
            "name": t['name'],
            "usage_percentage": t['usage_percentage'],
            "category": "language",
            "evidence": f"Used in {t['repository_count']} repositories"
        } for t in tech_analysis['technologies']]
        
        # Frameworks and libraries (enriched with dependency versions)
        frameworks = tech_analyzer.detect_frameworks(repos, parsed_dependencies)
        
        # Extract skills from README files
        readme_skills = self._extract_readme_skills(repos)
        
        # Merge README skills with frameworks (prioritize README for additional context)
        frameworks_enhanced = self._merge_readme_skills_with_frameworks(frameworks, readme_skills)
        
        # Soft skills indicators
        soft_skills = []
        if metrics['documentation_percentage'] > 40:
            soft_skills.append({
                "name": "Documentation",
                "evidence": "Consistent README usage"
            })
        
        # Domain expertise
        domain_expertise = [{
            "name": d,
            "evidence": "Project signatures"
        } for d in domain_analysis['specializations']]
        
        # MAJOR FRAMEWORKS ONLY (Top 10 most important)
        # Simplified dependency parser already filtered to major frameworks (React, Django, etc.)
        # NOT showing utility packages (lodash, uuid, etc.)
        detected_dependencies = []
        if parsed_dependencies:
            # Group by ecosystem and deduplicate
            seen = set()
            for dep in parsed_dependencies[:10]:  # TOP 10 MAJOR FRAMEWORKS ONLY
                key = (dep['name'].lower(), dep['ecosystem'])
                if key not in seen:
                    seen.add(key)
                    detected_dependencies.append({
                        "name": dep['name'],
                        "version": dep['version'],
                        "ecosystem": dep['ecosystem'],
                        "source_file": dep['source_file']
                    })
        
        # Add tools from README analysis
        tools_from_readme = [
            {"name": skill.name, "evidence": f"Mentioned in README ({skill.source})"}
            for skill in readme_skills 
            if skill.category in ['tool', 'database']
        ]
        
        return {
            "frameworks_and_libraries": frameworks_enhanced,
            "tools_and_platforms": tools_from_readme[:10],  # Top 10 tools from READMEs
            "soft_skills_indicators": soft_skills,
            "domain_expertise": domain_expertise
        }
    
    def _generate_summary(
        self,
        user: Dict,
        metrics: Dict,
        tech_analysis: Dict,
        domain_analysis: Dict,
        skills: Dict
    ) -> str:
        """Generate executive summary text."""
        name = user.get('login')
        primary_langs = ", ".join(tech_analysis['primary_stack'])
        primary_domain = domain_analysis['primary_domain']
        
        # Top frameworks
        top_fws = [f['name'] for f in skills['frameworks_and_libraries']][:3]
        fw_str = f", utilizing modern tools like {', '.join(top_fws)}" if top_fws else ""
        
        secondary_domains = domain_analysis['secondary_domains'][:2]
        secondary_str = ', '.join(secondary_domains) if secondary_domains else "various technologies"
        
        return (
            f"{name} is a {primary_domain} specialist with strong expertise in {primary_langs}{fw_str}. "
            f"They manage {metrics['total_repos']} repositories with a focus on {secondary_str}. "
            f"Their workflow demonstrates {int(metrics['documentation_percentage'])}% documentation coverage and consistent activity."
        )
    
    def _assemble_report(
        self,
        user: Dict,
        tech_analysis: Dict,
        project_analysis: List[Dict],
        skills: Dict,
        domain_analysis: Dict,
        summary: str,
        scores: Dict,
        metrics: Dict,
        recommendation: Dict
    ) -> Dict:
        """Assemble final report structure."""
        return {
            "status": "success",
            "report": {
                "candidate": {
                    "name": user.get("name") or user.get("login"),
                    "username": user.get("login"),
                    "profile_url": f"https://github.com/{user.get('login')}",
                    "avatar_url": user.get("avatar_url"),
                    "bio": user.get("bio"),
                    "location": user.get("location"),
                    "company": user.get("company")
                },
                "technology_analysis": tech_analysis,
                "project_scope_analysis": project_analysis,
                "comprehensive_skills": skills,
                "domain_classification": domain_analysis,
                "executive_summary": summary,
                "technical_assessment": {
                    "overall_score": scores['overall'],
                    "primary_languages": tech_analysis['primary_stack'],
                    "language_proficiency": scores['proficiency'],
                    "frameworks_detected": [f['name'] for f in skills['frameworks_and_libraries']],
                    "specializations": domain_analysis['secondary_domains'] or ["Generalist"],
                    "technical_depth": scores['depth'],
                    "learning_trajectory": scores['trajectory']
                },
                "code_quality": {
                    "overall_score": scores['quality'],
                    "documentation_score": scores['docs_score'],
                    "documentation_evidence": f"{metrics['repos_with_readme']} of {metrics['total_repos']} repositories have READMEs",
                    "project_structure": "Professional" if metrics['repos_with_readme'] > 0 else "Developing",
                    "best_practices": ["Good documentation"] if metrics['documentation_percentage'] > 50 else [],
                    "areas_to_verify": ["Test coverage", "Code consistency"]
                },
                "hiring_recommendation": recommendation,
                "metadata": {
                    "analysis_confidence": "High",
                    "data_completeness": f"{int(metrics['documentation_percentage'])}%",
                    "additional_notes": "Modular deterministic analysis with dependency extraction from manifest files."
                }
            },
            "generated_at": datetime.utcnow().isoformat() + "Z",
            "provider": "deterministic",
            "model": "rule-engine-v3-modular",
            "data_source": "stored_json"
        }
    
    
    def _extract_readme_skills(self, repos: List[Dict]) -> List:
        """
        Extract skills from all README files across repositories.
        
        Args:
            repos: List of repository dictionaries
            
        Returns:
            List of ExtractedSkill objects from readme_analyzer
        """
        all_skills = []
        
        for repo in repos:
            readme = repo.get('readme', {})
            if readme and readme.get('has_readme'):
                content = readme.get('content', '')
                if content:
                    skills = readme_analyzer.analyze_readme(content)
                    all_skills.extend(skills)
        
        logger.info(f"[README] Extracted {len(all_skills)} skills from {len(repos)} READMEs")
        return all_skills
    
    def _merge_readme_skills_with_frameworks(
        self, 
        frameworks: List[Dict], 
        readme_skills: List
    ) -> List[Dict]:
        """
        Merge README-extracted skills with existing frameworks list.
        
        Args:
            frameworks: Existing frameworks from tech_analyzer
            readme_skills: Skills extracted from READMEs
            
        Returns:
            Enhanced frameworks list with README insights
        """
        # Create a map of existing frameworks
        framework_map = {f['name'].lower(): f for f in frameworks}
        
        # Add new frameworks from README that aren't already detected
        for skill in readme_skills:
            if skill.category in ['framework', 'library']:
                key = skill.name.lower()
                if key not in framework_map:
                    framework_map[key] = {
                        "name": skill.name,
                        "category": skill.category.title(),
                        "evidence": f"Detected in README ({skill.source})"
                    }
        
        return list(framework_map.values())
    
    def _generate_fallback(self, data: Dict) -> Dict:
        """Generate fallback response on error."""
        return {
            "status": "error",
            "message": "Analysis failed",
            "generated_at": datetime.utcnow().isoformat() + "Z"
        }


# Singleton instance
analysis_service = AnalysisService()
