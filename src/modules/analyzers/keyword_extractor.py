"""
Keyword Extractor Module

Extracts high-quality, job-relevant keywords from GitHub repositories
for optimal candidate-job matching in the job portal platform.

This module analyzes:
- Repository descriptions
- README content
- Technologies used
- Project features
- Industry domains

And produces ranked keywords in three categories:
1. Technical Keywords (languages, frameworks, tools)
2. Domain Keywords (industries, business domains)
3. Feature Keywords (project capabilities)
"""

import re
from typing import Dict, List, Set, Tuple, Optional
from collections import Counter
from dataclasses import dataclass
from utils.logger import logger


@dataclass
class ExtractedKeyword:
    """Represents a single extracted keyword with metadata."""
    keyword: str
    category: str  # 'technical', 'domain', 'feature'
    confidence: float  # 0.0 to 1.0
    sources: List[str]  # Where it was found: 'description', 'readme', 'topics', etc.
    frequency: int  # How many times it appeared


class KeywordExtractor:
    """
    Extracts and ranks keywords from repository data for job matching.
    
    Uses deterministic analysis to identify the most relevant keywords
    that describe a project's technology stack, business domain, and features.
    """
    
    def __init__(self):
        """Initialize keyword extractor with pattern libraries."""
        self.technical_patterns = self._build_technical_patterns()
        self.domain_patterns = self._build_domain_patterns()
        self.feature_patterns = self._build_feature_patterns()
        
        # Stop words to filter out (common but not useful for job matching)
        self.stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'been', 'be',
            'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
            'should', 'may', 'might', 'can', 'this', 'that', 'these', 'those',
            'it', 'its', 'my', 'your', 'our', 'their', 'project', 'repository',
            'repo', 'code', 'simple', 'basic', 'using', 'used', 'use'
        }
        
        logger.info("[KEYWORD_EXTRACTOR] Initialized with comprehensive pattern libraries")
    
    def extract_keywords(self, repo: Dict) -> Dict[str, List[str]]:
        """
        Extract top keywords from a repository.
        
        Args:
            repo: Repository data dict with description, readme, topics, languages
            
        Returns:
            Dict with categorized keywords:
            {
                'technical_keywords': [...],
                'domain_keywords': [...],
                'feature_keywords': [...],
                'all_keywords': [...]  # Top 15 overall
            }
        """
        # Gather all text sources
        text_sources = self._gather_text_sources(repo)
        
        # Extract keywords by category
        technical = self._extract_technical_keywords(text_sources, repo)
        domain = self._extract_domain_keywords(text_sources)
        feature = self._extract_feature_keywords(text_sources)
        
        # Combine and rank
        all_keywords = self._rank_and_deduplicate([
            *technical,
            *domain,
            *feature
        ])
        
        return {
            'technical_keywords': [kw.keyword for kw in technical[:10]],
            'domain_keywords': [kw.keyword for kw in domain[:8]],
            'feature_keywords': [kw.keyword for kw in feature[:8]],
            'all_keywords': [kw.keyword for kw in all_keywords[:15]]
        }
    
    def _gather_text_sources(self, repo: Dict) -> Dict[str, str]:
        """Gather all text sources from repository."""
        sources = {}
        
        # Description
        if repo.get('description'):
            sources['description'] = repo['description'].lower()
        
        # Topics
        topics = repo.get('topics', [])
        if topics:
            sources['topics'] = ' '.join(topics).lower()
        
        # README (FULL CONTENT - no truncation)
        readme = repo.get('readme', {})
        if readme and readme.get('content'):
            sources['readme'] = readme['content'].lower()
        
        # Repository name (can contain keywords)
        if repo.get('name'):
            # Convert kebab-case and snake_case to words
            name = repo['name'].replace('-', ' ').replace('_', ' ')
            sources['repo_name'] = name.lower()
        
        # ALL MARKDOWN FILES (CONTRIBUTING.md, docs/*.md, etc.)
        markdown_files = repo.get('markdown_files', [])
        for md_file in markdown_files:
            filename = md_file.get('filename', '')
            content = md_file.get('content', '')
            if content:
                # Create unique source key
                source_key = f"md_{filename.lower().replace('.md', '')}"
                sources[source_key] = content.lower()
        
        return sources
    
    def _extract_technical_keywords(
        self, 
        text_sources: Dict[str, str], 
        repo: Dict
    ) -> List[ExtractedKeyword]:
        """Extract technical keywords (languages, frameworks, tools)."""
        keywords = []
        
        # 1. From languages (most reliable)
        languages = repo.get('languages', {}).get('percentages', {})
        for lang, percentage in languages.items():
            if percentage > 5.0:  # At least 5% of codebase
                keywords.append(ExtractedKeyword(
                    keyword=lang,
                    category='technical',
                    confidence=min(percentage / 100.0, 1.0),
                    sources=['languages'],
                    frequency=1
                ))
        
        # 2. From pattern matching in text
        for pattern, tech_name in self.technical_patterns.items():
            sources_found = []
            frequency = 0
            
            for source_name, text in text_sources.items():
                if pattern in text or self._word_boundary_match(pattern, text):
                    sources_found.append(source_name)
                    frequency += 1
            
            if sources_found:
                # Higher confidence if found in multiple sources
                confidence = min(0.5 + (len(sources_found) * 0.2), 1.0)
                keywords.append(ExtractedKeyword(
                    keyword=tech_name,
                    category='technical',
                    confidence=confidence,
                    sources=sources_found,
                    frequency=frequency
                ))
        
        # Sort by confidence and frequency
        keywords.sort(key=lambda k: (k.confidence, k.frequency), reverse=True)
        return keywords
    
    def _extract_domain_keywords(self, text_sources: Dict[str, str]) -> List[ExtractedKeyword]:
        """Extract domain/industry keywords."""
        keywords = []
        
        for pattern, domain_name in self.domain_patterns.items():
            sources_found = []
            frequency = 0
            
            for source_name, text in text_sources.items():
                if pattern in text or self._word_boundary_match(pattern, text):
                    sources_found.append(source_name)
                    frequency += 1
            
            if sources_found:
                # Description and topics are more reliable for domain
                confidence = 0.6
                if 'description' in sources_found:
                    confidence += 0.2
                if 'topics' in sources_found:
                    confidence += 0.2
                
                keywords.append(ExtractedKeyword(
                    keyword=domain_name,
                    category='domain',
                    confidence=min(confidence, 1.0),
                    sources=sources_found,
                    frequency=frequency
                ))
        
        keywords.sort(key=lambda k: (k.confidence, k.frequency), reverse=True)
        return keywords
    
    def _extract_feature_keywords(self, text_sources: Dict[str, str]) -> List[ExtractedKeyword]:
        """Extract feature keywords (authentication, payment, etc.)."""
        keywords = []
        
        for pattern, feature_name in self.feature_patterns.items():
            sources_found = []
            frequency = 0
            
            for source_name, text in text_sources.items():
                if pattern in text or self._word_boundary_match(pattern, text):
                    sources_found.append(source_name)
                    frequency += 1
            
            if sources_found:
                confidence = 0.5 + (len(sources_found) * 0.15)
                keywords.append(ExtractedKeyword(
                    keyword=feature_name,
                    category='feature',
                    confidence=min(confidence, 1.0),
                    sources=sources_found,
                    frequency=frequency
                ))
        
        keywords.sort(key=lambda k: (k.confidence, k.frequency), reverse=True)
        return keywords
    
    def _rank_and_deduplicate(self, keywords: List[ExtractedKeyword]) -> List[ExtractedKeyword]:
        """Rank all keywords and remove duplicates."""
        # Use dict to deduplicate by keyword name (keep highest confidence)
        unique = {}
        for kw in keywords:
            key = kw.keyword.lower()
            if key not in unique or kw.confidence > unique[key].confidence:
                unique[key] = kw
        
        # Sort by confidence and frequency
        ranked = sorted(unique.values(), key=lambda k: (k.confidence, k.frequency), reverse=True)
        return ranked
    
    def _word_boundary_match(self, pattern: str, text: str) -> bool:
        """Check if pattern matches with word boundaries (for short keywords)."""
        if len(pattern) < 4:
            # Use word boundary for short patterns to avoid false positives
            return bool(re.search(r'\b' + re.escape(pattern) + r'\b', text))
        return pattern in text
    
    def _build_technical_patterns(self) -> Dict[str, str]:
        """Build technical keyword patterns (pattern -> display name)."""
        return {
            # Frontend Frameworks
            'react': 'React',
            'vue': 'Vue.js',
            'angular': 'Angular',
            'svelte': 'Svelte',
            'next.js': 'Next.js',
            'nextjs': 'Next.js',
            'nuxt': 'Nuxt.js',
            
            # Backend Frameworks
            'django': 'Django',
            'flask': 'Flask',
            'fastapi': 'FastAPI',
            'express': 'Express.js',
            'nestjs': 'NestJS',
            'spring boot': 'Spring Boot',
            'spring': 'Spring',
            'laravel': 'Laravel',
            'ruby on rails': 'Ruby on Rails',
            'rails': 'Rails',
            
            # Mobile
            'react native': 'React Native',
            'flutter': 'Flutter',
            'swift': 'Swift',
            'kotlin': 'Kotlin',
            'ios': 'iOS',
            'android': 'Android',
            
            # Databases
            'postgresql': 'PostgreSQL',
            'postgres': 'PostgreSQL',
            'mysql': 'MySQL',
            'mongodb': 'MongoDB',
            'redis': 'Redis',
            'firebase': 'Firebase',
            'supabase': 'Supabase',
            
            # DevOps & Cloud
            'docker': 'Docker',
            'kubernetes': 'Kubernetes',
            'k8s': 'Kubernetes',
            'aws': 'AWS',
            'azure': 'Azure',
            'gcp': 'Google Cloud',
            'terraform': 'Terraform',
            'jenkins': 'Jenkins',
            'github actions': 'GitHub Actions',
            
            # AI/ML
            'tensorflow': 'TensorFlow',
            'pytorch': 'PyTorch',
            'scikit-learn': 'Scikit-learn',
            'sklearn': 'Scikit-learn',
            'machine learning': 'Machine Learning',
            'deep learning': 'Deep Learning',
            'neural network': 'Neural Networks',
            'langchain': 'LangChain',
            'transformers': 'Transformers',
            
            # Testing
            'jest': 'Jest',
            'pytest': 'Pytest',
            'cypress': 'Cypress',
            'selenium': 'Selenium',
            
            # Others
            'graphql': 'GraphQL',
            'rest api': 'REST API',
            'websocket': 'WebSocket',
            'microservices': 'Microservices',
        }
    
    def _build_domain_patterns(self) -> Dict[str, str]:
        """Build domain/industry keyword patterns."""
        return {
            # E-commerce & Retail
            'ecommerce': 'E-commerce',
            'e-commerce': 'E-commerce',
            'shopping': 'E-commerce',
            'retail': 'Retail',
            'marketplace': 'Marketplace',
            
            # Healthcare
            'healthcare': 'Healthcare',
            'health': 'Healthcare',
            'medical': 'Healthcare',
            'hospital': 'Healthcare',
            'patient': 'Healthcare',
            'telemedicine': 'Telemedicine',
            
            # Finance
            'fintech': 'FinTech',
            'finance': 'Finance',
            'banking': 'Banking',
            'payment': 'Payments',
            'crypto': 'Cryptocurrency',
            'blockchain': 'Blockchain',
            'trading': 'Trading',
            
            # Education
            'education': 'Education',
            'edtech': 'EdTech',
            'learning': 'E-Learning',
            'course': 'Education',
            'university': 'Education',
            
            # Real Estate
            'real estate': 'Real Estate',
            'property': 'Real Estate',
            'rental': 'Real Estate',
            
            # Social & Communication
            'social network': 'Social Media',
            'social media': 'Social Media',
            'chat': 'Communication',
            'messaging': 'Messaging',
            'forum': 'Community',
            
            # Enterprise
            'enterprise': 'Enterprise',
            'saas': 'SaaS',
            'crm': 'CRM',
            'erp': 'ERP',
            
            # Media & Entertainment
            'streaming': 'Media Streaming',
            'video': 'Video',
            'music': 'Music',
            'gaming': 'Gaming',
            'game': 'Gaming',
            
            # AI & Data
            'artificial intelligence': 'AI',
            'data science': 'Data Science',
            'analytics': 'Analytics',
            'business intelligence': 'Business Intelligence',
        }
    
    def _build_feature_patterns(self) -> Dict[str, str]:
        """Build feature keyword patterns."""
        return {
            # Authentication & Security
            'authentication': 'Authentication',
            'auth': 'Authentication',
            'login': 'User Login',
            'oauth': 'OAuth',
            'jwt': 'JWT',
            'security': 'Security',
            'encryption': 'Encryption',
            
            # Payment
            'payment': 'Payment Processing',
            'stripe': 'Stripe Integration',
            'paypal': 'PayPal',
            'checkout': 'Checkout',
            
            # Real-time
            'real-time': 'Real-time',
            'realtime': 'Real-time',
            'live': 'Real-time',
            'socket': 'Real-time Communication',
            
            # API
            'api': 'API',
            'rest': 'REST API',
            'graphql': 'GraphQL API',
            
            # Data & Analytics
            'dashboard': 'Dashboard',
            'analytics': 'Analytics',
            'reporting': 'Reporting',
            'visualization': 'Data Visualization',
            
            # Collaboration
            'collaboration': 'Collaboration',
            'multi-user': 'Multi-user',
            'team': 'Team Features',
            
            # Content
            'blog': 'Blog',
            'cms': 'Content Management',
            'editor': 'Editor',
            
            # Mobile/Responsive
            'responsive': 'Responsive Design',
            'mobile': 'Mobile-friendly',
            'pwa': 'Progressive Web App',
            
            # Integration
            'integration': 'Integration',
            'webhook': 'Webhooks',
            'notification': 'Notifications',
            'email': 'Email',
            
            # Media
            'upload': 'File Upload',
            'image': 'Image Processing',
            'search': 'Search',
            'filter': 'Filtering',
        }


# Singleton instance
keyword_extractor = KeywordExtractor()
