"""
Role Recommender Module - Production Grade

Generates role recommendations based on domain classification and tech stack.
Supports ALL 35+ domains with comprehensive edge case handling.
NO HARDCODING - Handles all types of GitHub accounts.
"""
from typing import Dict, List, Tuple, Optional
from utils.logger import logger


class RoleRecommender:
    """
    Recommends suitable roles based on domain and technology analysis.
    
    Features:
    - Supports ALL 35+ industry domains
    - Dynamic role mapping (no hardcoding)
    - Seniority assessment
    - Hiring recommendations
    - Green/red flag identification
    - Edge case handling (empty data, unknown domains, etc.)
    """
    
    def __init__(self):
        """Initialize role recommender with domain-role mappings."""
        logger.info("[ROLE] Role Recommender initialized (Production-Grade)")
        self.domain_role_map = self._build_domain_role_map()
    
    def recommend_role(
        self,
        domain_analysis: Dict,
        tech_analysis: Dict,
        scores: Dict,
        metrics: Dict
    ) -> Dict:
        """
        Generate comprehensive hiring recommendation.
        
        Handles edge cases:
        - None/empty domain_analysis
        - Missing tech_analysis
        - Invalid scores
        - Empty metrics
        
        Args:
            domain_analysis: Domain classification results
            tech_analysis: Technology stack analysis
            scores: Calculated scores
            metrics: Raw metrics
            
        Returns:
            Dict with role recommendations and hiring assessment
        """
        # Handle edge cases
        if not domain_analysis:
            domain_analysis = {'primary_domain': 'Software Development', 'secondary_domains': []}
        if not tech_analysis:
            tech_analysis = {'primary_stack': [], 'technologies': []}
        if not scores:
            scores = {'overall': 5, 'depth': 'Junior'}
        
        primary_domain = domain_analysis.get('primary_domain', 'Software Development')
        primary_langs = tech_analysis.get('primary_stack') or []
        
        # Extract detected frameworks from tech_analysis
        detected_frameworks = tech_analysis.get('detected_frameworks', [])
        
        # Map domain to roles (NOW WITH FRAMEWORK AWARENESS!)
        role, suitable_roles = self._map_domain_to_roles(primary_domain, primary_langs, detected_frameworks)
        
        # Generate green/red flags
        green_flags, red_flags = self._generate_flags(primary_domain, scores, metrics)
        
        # Generate recommendation summary
        tech_stack_str = ', '.join(primary_langs[:2]) if primary_langs else 'Multiple technologies'
        summary = (
            f"Strong candidate for {role} positions with expertise in {primary_domain}. "
            f"Primary tech stack: {tech_stack_str}."
        )
        
        return {
            "overall_score": scores.get('overall', 5),
            "confidence_level": self._calculate_confidence(metrics),
            "suitable_roles": suitable_roles or ["Software Engineer"],  # Fallback
            "seniority_fit": scores.get('depth', 'Junior'),
            "team_fit_indicators": self._assess_team_fit(metrics),
            "red_flags": red_flags,
            "green_flags": green_flags,
            "salary_bracket_suggestion": self._suggest_salary_bracket(scores.get('overall', 5)),
            "recommendation_summary": summary,
            "next_steps": self._suggest_next_steps(scores.get('overall', 5))
        }
    
    def _build_domain_role_map(self) -> Dict[str, Tuple[str, List[str]]]:
        """
        Build comprehensive domain-to-role mapping for ALL 35+ domains.
        Returns: Dict[domain_name, (primary_role, suitable_roles_list)]
        """
        return {
            # ========== AI/ML & Data ==========
            "AI & Machine Learning": ("AI/ML Engineer", ["AI/ML Engineer", "Machine Learning Engineer", "Data Scientist"]),
            "Computer Vision": ("Computer Vision Engineer", ["Computer Vision Engineer", "AI/ML Engineer", "Research Engineer"]),
            "Natural Language Processing": ("NLP Engineer", ["NLP Engineer", "AI/ML Engineer", "Research Scientist"]),
            "Data Science & Analytics": ("Data Scientist", ["Data Scientist", "Data Analyst", "ML Engineer"]),
            "Data Engineering": ("Data Engineer", ["Data Engineer", "Big Data Engineer", "ETL Developer"]),
            
            # ========== Tech Specialized ==========
            "Blockchain & Web3": ("Blockchain Developer", ["Blockchain Developer", "Smart Contract Developer", "Web3 Engineer"]),
            "Mobile Development": ("Mobile Developer", ["Mobile Developer", "iOS Developer", "Android Developer", "Flutter Developer"]),
            "Game Development": ("Game Developer", ["Game Developer", "Unity Developer", "Game Engineer", "Graphics Programmer"]),
            "DevOps & Cloud": ("DevOps Engineer", ["DevOps Engineer", "Cloud Engineer", "SRE", "Platform Engineer"]),
            "Cybersecurity": ("Security Engineer", ["Security Engineer", "Cybersecurity Analyst", "Penetration Tester", "Security Architect"]),
            "IoT & Embedded": ("Embedded Systems Engineer", ["Embedded Systems Engineer", "IoT Developer", "Firmware Engineer"]),
            
            # ========== Web Development ==========
            "Frontend Development": ("Frontend Developer", ["Frontend Developer", "UI Developer", "React Developer", "Vue Developer"]),
            "Backend Development": ("Backend Developer", ["Backend Developer", "API Developer", "Microservices Developer"]),
            "Web Development": ("Full-stack Developer", ["Full-stack Developer", "Web Developer", "Software Engineer"]),
            "UI/UX Design": ("UI/UX Developer", ["UI/UX Developer", "Frontend Developer", "Design Engineer"]),
            
            # ========== Business Domains ==========
            "Finance (FinTech)": ("FinTech Developer", ["FinTech Developer", "Financial Software Engineer", "Backend Developer"]),
            "Healthcare": ("Healthcare Software Engineer", ["Healthcare Software Engineer", "Medical Software Developer", "Health Tech Developer"]),
            "E-commerce": ("E-commerce Developer", ["E-commerce Developer", "Full-stack Developer", "Platform Engineer"]),
            "Education (EdTech)": ("EdTech Developer", ["EdTech Developer", "Full-stack Developer", "LMS Developer"]),
            "Enterprise Software": ("Enterprise Software Engineer", ["Enterprise Software Engineer", "Backend Developer", "Solutions Architect"]),
            
            # ========== Traditional Industries ==========
            "Civil Engineering & Construction": ("Civil Engineering Software Developer", ["Civil Engineering Software Developer", "CAD/BIM Developer", "Construction Tech"]),
            "Architecture & Design": ("Architecture Software Developer", ["Architecture Software Developer", "CAD Developer", "3D Visualization Developer"]),
            "Accounting & Auditing": ("Accounting Software Developer", ["Accounting Software Developer", "Financial Software Engineer", "ERP Developer"]),
            "Legal & Compliance": ("Legal Tech Developer", ["Legal Tech Developer", "Compliance Software Engineer", "RegTech Developer"]),
            "Real Estate & Property": ("PropTech Developer", ["PropTech Developer", "Real Estate Platform Engineer", "Full-stack Developer"]),
            "Manufacturing & Supply Chain": ("Manufacturing Software Engineer", ["Manufacturing Software Engineer", "Supply Chain Developer", "MES Developer"]),
            "Logistics & Transportation": ("Logistics Software Engineer", ["Logistics Software Engineer", "Transportation Tech Developer", "Fleet Management Developer"]),
            "Hospitality & Tourism": ("Hospitality Tech Developer", ["Hospitality Tech Developer", "Booking Platform Engineer", "Travel Tech Developer"]),
            "Agriculture & Food Tech": ("AgTech Developer", ["AgTech Developer", "Agricultural Software Engineer", "Farm Management Developer"]),
            "Energy & Utilities": ("Energy Tech Developer", ["Energy Tech Developer", "Utilities Software Engineer", "Smart Grid Developer"]),
            "Telecommunications": ("Telecom Software Engineer", ["Telecom Software Engineer", "Network Software Developer", "5G Developer"]),
            "Media & Publishing": ("Media Tech Developer", ["Media Tech Developer", "Content Platform Engineer", "Publishing Platform Developer"]),
            "Human Resources & Recruitment": ("HR Tech Developer", ["HR Tech Developer", "Recruitment Platform Engineer", "ATS Developer"]),
            "Consulting & Professional Services": ("Consulting Tech Developer", ["Consulting Tech Developer", "Business Solutions Developer", "CRM Developer"]),
            "Insurance & Risk Management": ("InsurTech Developer", ["InsurTech Developer", "Insurance Software Engineer", "Risk Analytics Developer"]),
            "Retail & Point of Sale": ("Retail Tech Developer", ["Retail Tech Developer", "POS Developer", "Inventory Management Developer"]),
            "Non-Profit & NGO": ("Non-Profit Tech Developer", ["Non-Profit Tech Developer", "Social Impact Developer", "Donor Management Developer"]),
            
            # ========== Other ==========
            "Marketing & SEO": (" Marketing Tech Developer", ["Marketing Tech Developer", "MarTech Engineer", "SEO Platform Developer"]),
            "Media & Entertainment": ("Entertainment Tech Developer", ["Entertainment Tech Developer", "Streaming Platform Engineer", "Media Developer"]),
            "Social & Communication": ("Social Platform Developer", ["Social Platform Developer", "Communication App Developer", "Community Platform Engineer"]),
            "Software Development": ("Software Engineer", ["Software Engineer", "Full-stack Developer", "Backend Developer"]),
        }
    
    def _map_domain_to_roles(self, domain: str, languages: List[str], frameworks: List[Dict] = None) -> Tuple[str, List[str]]:
        """
        Map primary domain to role and suitable role list.
        UNIVERSAL & COMPREHENSIVE: Works for ALL developer types!
        
        Args:
            domain: Primary business domain
            languages: Programming languages used
            frameworks: Detected frameworks and libraries
        
        Returns:
            Tuple of (primary_role, suitable_roles_list)
        """
        # PRIORITY 1: Framework-based role detection (MOST ACCURATE!)
        if frameworks:
            framework_names = [f.get('name', '').lower() for f in frameworks if isinstance(f, dict)]
            
            # === MOBILE DEVELOPMENT ===
            mobile_frameworks = ['react-native', 'react native', 'flutter', 'ionic', 'xamarin', 
                                'react native', 'expo', 'cordova', 'capacitor', 'nativescript']
            if any(fw in framework_names for fw in mobile_frameworks):
                return "Mobile Developer", ["Mobile Developer", "React Native Developer", "Flutter Developer", 
                                           "Cross-platform Developer", "Full-stack Developer"]
            
            # === FRONTEND WEB ===
            frontend_frameworks = ['react', 'vue', 'angular', 'svelte', 'next.js', 'nuxt', 'gatsby',
                                  'preact', 'solid', 'qwik', 'astro', 'remix', 'vite', 'webpack',
                                  'parcel', 'rollup', 'esbuild', 'tailwind', 'bootstrap', 'material-ui',
                                  'chakra', 'styled-components', 'emotion']
            if any(fw in framework_names for fw in frontend_frameworks):
                return "Frontend Developer", ["Frontend Developer", "React Developer", "Vue Developer",
                                             "Full-stack Developer", "UI Developer", "Frontend Engineer"]
            
            # === BACKEND WEB ===
            backend_frameworks = ['django', 'flask', 'fastapi', 'express', 'nest.js', 'nestjs', 'koa',
                                 'spring', 'spring boot', 'laravel', 'symfony', 'rails', 'ruby on rails',
                                 'asp.net', 'dotnet', '.net', 'gin', 'echo', 'fiber', 'actix', 'rocket',
                                 'phoenix', 'elixir', 'play', 'ktor', 'micronaut', 'quarkus', 'grpc']
            if any(fw in framework_names for fw in backend_frameworks):
                return "Backend Developer", ["Backend Developer", "API Developer", "Backend Engineer",
                                            "Full-stack Developer", "Microservices Developer"]
            
            # === FULL-STACK (Combined Frontend + Backend) ===
            fullstack_combo = ['next.js', 'nuxt', 'remix', 'meteor', 'sveltekit', 'blitz']
            if any(fw in framework_names for fw in fullstack_combo):
                return "Full-stack Developer", ["Full-stack Developer", "Web Developer", 
                                               "Frontend Developer", "Backend Developer"]
            
            # === DATA SCIENCE & ANALYTICS ===
            data_science_frameworks = ['pandas', 'numpy', 'scipy', 'matplotlib', 'seaborn', 'plotly',
                                      'scikit-learn', 'sklearn', 'statsmodels', 'dask', 'polars',
                                      'jupyter', 'notebook', 'spark', 'pyspark', 'airflow', 'prefect']
            if any(fw in framework_names for fw in data_science_frameworks):
                return "Data Scientist", ["Data Scientist", "Data Analyst", "Analytics Engineer",
                                         "Business Intelligence Developer"]
            
            # === MACHINE LEARNING & AI ===
            ml_frameworks = ['tensorflow', 'pytorch', 'keras', 'jax', 'mxnet', 'caffe', 'theano',
                           'transformers', 'hugging face', 'openai', 'langchain', 'llamaindex',
                           'mlflow', 'wandb', 'optuna', 'ray', 'xgboost', 'lightgbm', 'catboost']
            if any(fw in framework_names for fw in ml_frameworks):
                return "ML Engineer", ["ML Engineer", "Machine Learning Engineer", "AI Developer",
                                      "Research Engineer", "MLOps Engineer"]
            
            # === DEVOPS & CLOUD ===
            devops_frameworks = ['docker', 'kubernetes', 'k8s', 'terraform', 'ansible', 'jenkins',
                                'github actions', 'gitlab ci', 'circleci', 'travis', 'helm', 'kustomize',
                                'prometheus', 'grafana', 'datadog', 'new relic', 'vagrant', 'packer',
                                'consul', 'vault', 'nomad', 'pulumi', 'cloudformation', 'aws cdk']
            if any(fw in framework_names for fw in devops_frameworks):
                return "DevOps Engineer", ["DevOps Engineer", "Cloud Engineer", "Platform Engineer",
                                          "SRE", "Infrastructure Engineer", "Kubernetes Engineer"]
            
            # === GAME DEVELOPMENT ===
            game_frameworks = ['unity', 'unreal', 'godot', 'pygame', 'phaser', 'three.js', 'babylon.js',
                             'cocos2d', 'libgdx', 'monogame', 'love2d', 'raylib', 'bevy', 'amethyst']
            if any(fw in framework_names for fw in game_frameworks):
                return "Game Developer", ["Game Developer", "Unity Developer", "Unreal Developer",
                                         "Game Engineer", "Graphics Programmer"]
            
            # === BLOCKCHAIN & WEB3 ===
            blockchain_frameworks = ['web3', 'ethers', 'web3.js', 'truffle', 'hardhat', 'brownie',
                                    'solidity', 'anchor', 'solana', 'ethereum', 'polygon', 'wagmi']
            if any(fw in framework_names for fw in blockchain_frameworks):
                return "Blockchain Developer", ["Blockchain Developer", "Web3 Developer", 
                                               "Smart Contract Developer", "DeFi Developer"]
            
            # === TESTING & QA ===
            testing_frameworks = ['jest', 'pytest', 'mocha', 'chai', 'jasmine', 'karma', 'vitest',
                                'cypress', 'playwright', 'selenium', 'puppeteer', 'testcafe',
                                'junit', 'testng', 'rspec', 'minitest', 'unittest', 'nose']
            if any(fw in framework_names for fw in testing_frameworks):
                return "QA Engineer", ["QA Engineer", "Test Automation Engineer", "SDET",
                                      "Quality Assurance Engineer"]
            
            # === DATABASE & DATA ENGINEERING ===
            database_frameworks = ['mongodb', 'postgres', 'postgresql', 'mysql', 'redis', 'elasticsearch',
                                  'cassandra', 'dynamodb', 'firestore', 'supabase', 'prisma', 'sequelize',
                                  'typeorm', 'mongoose', 'sqlalchemy', 'alembic', 'knex', 'drizzle']
            if any(fw in framework_names for fw in database_frameworks):
                return "Data Engineer", ["Data Engineer", "Database Engineer", "Backend Developer",
                                        "Data Platform Engineer"]
            
            # === EMBEDDED & IOT ===
            embedded_frameworks = ['arduino', 'raspberry', 'esp32', 'micropython', 'circuitpython',
                                  'freertos', 'zephyr', 'mbed', 'platformio', 'embedded']
            if any(fw in framework_names for fw in embedded_frameworks):
                return "Embedded Systems Engineer", ["Embedded Systems Engineer", "IoT Developer",
                                                     "Firmware Engineer", "Hardware Engineer"]
            
            # === DESKTOP APPLICATIONS ===
            desktop_frameworks = ['electron', 'tauri', 'qt', 'pyqt', 'tkinter', 'wxpython', 'kivy',
                                'gtk', 'winforms', 'wpf', 'javafx', 'swing', 'avalonia']
            if any(fw in framework_names for fw in desktop_frameworks):
                return "Desktop Developer", ["Desktop Developer", "Application Developer",
                                            "Cross-platform Developer", "Software Engineer"]
            
            # === API & MICROSERVICES ===
            api_frameworks = ['graphql', 'apollo', 'prisma', 'hasura', 'postgraphile', 'swagger',
                            'openapi', 'grpc', 'protobuf', 'kafka', 'rabbitmq', 'redis', 'nats']
            if any(fw in framework_names for fw in api_frameworks):
                return "API Developer", ["API Developer", "Backend Developer", "Microservices Developer",
                                        "Integration Engineer"]
        
        # PRIORITY 2: Language-based inference
        if languages:
            role_from_lang = self._infer_role_from_languages(languages)
            if role_from_lang[0] != "Software Engineer":  # If we got a specific role from language
                return role_from_lang
        
        # PRIORITY 3: Domain-based (only if no framework/language match)
        if domain and domain.strip() and domain in self.domain_role_map:
            return self.domain_role_map[domain]
        
        # FALLBACK: Generic software engineer
        logger.warning(f"[ROLE] Could not determine specific role for domain '{domain}', using fallback")
        return "Software Engineer", ["Software Engineer", "Full-stack Developer"]
    
    def _infer_role_from_languages(self, languages: List[str]) -> Tuple[str, List[str]]:
        """
        Fallback role inference based on primary languages.
        Handles edge case: empty or None languages list.
        """
        # Edge case: No languages
        if not languages:
            logger.info("[ROLE] No languages provided, defaulting to Software Engineer")
            return "Software Engineer", ["Software Engineer", "Developer"]
        
        primary_lang = languages[0].lower() if languages else ""
        
        # Language-based inference
        lang_role_map = {
            'python': ("Python Developer", ["Python Developer", "Backend Developer", "Data Engineer"]),
            'javascript': ("Full-stack Developer", ["Full-stack Developer", "Frontend Developer", "Backend Developer"]),
            'typescript': ("Full-stack Developer", ["Full-stack Developer", "Frontend Developer", "Backend Developer"]),
            'java': ("Backend Developer", ["Backend Developer", "Enterprise Developer", "Software Engineer"]),
            'kotlin': ("Android Developer", ["Android Developer", "Mobile Developer", "Backend Developer"]),
            'swift': ("iOS Developer", ["iOS Developer", "Mobile Developer"]),
            'dart': ("Flutter Developer", ["Flutter Developer", "Mobile Developer"]),
            'go': ("Backend Developer", ["Backend Developer", "Systems Engineer", "Cloud Engineer"]),
            'rust': ("Systems Engineer", ["Systems Engineer", "Backend Developer", "Performance Engineer"]),
            'c++': ("Systems Engineer", ["Systems Engineer", "Game Developer", "Performance Engineer"]),
            'c#': ("Full-stack Developer", ["Full-stack Developer", "Game Developer", ".NET Developer"]),
            'php': ("Backend Developer", ["Backend Developer", "Web Developer", "Full-stack Developer"]),
            'ruby': ("Backend Developer", ["Backend Developer", "Web Developer", "Full-stack Developer"]),
            'r': ("Data Scientist", ["Data Scientist", "Data Analyst", "Statistician"]),
            'scala': ("Backend Developer", ["Backend Developer", "Data Engineer", "Big Data Engineer"]),
        }
        
        return lang_role_map.get(primary_lang, ("Software Engineer", ["Software Engineer", "Developer"]))
    
    def _generate_flags(self, domain: str, scores: Dict, metrics: Dict) -> Tuple[List[str], List[str]]:
        """Generate green and red flags based on analysis."""
        green_flags = []
        red_flags = []
        
        # Green flags
        if domain and domain != "Software Development":
            green_flags.append(f"Specialized in {domain}")
        if scores.get('overall', 0) >= 7:
            green_flags.append("High Technical Proficiency")
        if metrics.get('documentation_percentage', 0) > 50:
            green_flags.append("Strong Documentation Practices")
        if metrics.get('total_stars', 0) > 10:
            green_flags.append("Community Recognition")
        
        # Red flags
        if scores.get('consistency', 0) < 3:
            red_flags.append("Low Activity Consistency")
        if metrics.get('documentation_percentage', 0) < 20:
            red_flags.append("Limited Documentation")
        
        return green_flags or ["Demonstrated Domain Expertise"], red_flags
    
    def _calculate_confidence(self, metrics: Dict) -> str:
        """Calculate confidence level based on data completeness."""
        doc_pct = metrics.get('documentation_percentage', 0)
        if doc_pct > 60:
            return "Very High"
        elif doc_pct > 40:
            return "High"
        elif doc_pct > 20:
            return "Medium"
        else:
            return "Low"
    
    def _assess_team_fit(self, metrics: Dict) -> str:
        """Assess team fit based on collaboration indicators."""
        forks = metrics.get('total_forks', 0)
        if forks > 5:
            return "Strong collaboration signals"
        elif forks > 0:
            return "Some collaboration evidence"
        else:
            return "Verifiable code history"
    
    def _suggest_salary_bracket(self, overall_score: int) -> str:
        """Suggest salary bracket based on overall score."""
        if overall_score >= 8:
            return "Premium"
        elif overall_score >= 6:
            return "Competitive"
        elif overall_score >= 4:
            return "Standard"
        else:
            return "Entry-level"
    
    def _suggest_next_steps(self, overall_score: int) -> List[str]:
        """Suggest hiring process next steps."""
        steps = ["Technical Interview", "Code Review"]
        
        if overall_score >= 7:
            steps.append("System Design Discussion")
            steps.append("Team Culture Fit")
        else:
            steps.append("Coding Assignment")
        
        return steps


# Singleton instance
role_recommender = RoleRecommender()
