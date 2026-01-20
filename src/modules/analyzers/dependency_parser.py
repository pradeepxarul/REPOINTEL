"""
Dependency Parser

Parses package manifest files (package.json, requirements.txt, etc.)
to extract major frameworks and libraries for job matching.
Filters out utility packages to show only relevant frameworks.
"""
import json
import re
from typing import Dict, List, Any, Optional
from utils.logger import logger


class DependencyParser:
    """Parses dependency files to extract major frameworks only."""
    
    def __init__(self):
        """Initialize dependency parser with major framework lists."""
        # Define MAJOR frameworks we care about for job matching
        self.major_frameworks = self._build_major_frameworks()
        logger.info("[DEPENDENCY_PARSER] Initialized (Simplified Mode - Major Frameworks Only)")
    
    def parse_package_json(self, content: str) -> List[Dict]:
        """
        Parse package.json for JavaScript/TypeScript MAJOR frameworks only.
        
        Args:
            content: Raw package.json content
            
        Returns:
            List of MAJOR dependency dicts (filtered)
        """
        try:
            data = json.loads(content)
            all_deps = []
            
            # Production dependencies
            if 'dependencies' in data:
                for name, version in data['dependencies'].items():
                    if self._is_major_framework(name, 'npm'):
                        all_deps.append({
                            'name': name,
                            'version': self._clean_version(version),
                            'type': 'production',
                            'ecosystem': 'npm',
                            'source_file': 'package.json'
                        })
            
            # Dev dependencies (frameworks like testing libraries)
            if 'devDependencies' in data:
                for name, version in data['devDependencies'].items():
                    if self._is_major_framework(name, 'npm'):
                        all_deps.append({
                            'name': name,
                            'version': self._clean_version(version),
                            'type': 'dev',
                            'ecosystem': 'npm',
                            'source_file': 'package.json'
                        })
            
            logger.info(f"[NPM] Found {len(all_deps)} major frameworks in package.json")
            return all_deps
            
        except json.JSONDecodeError:
            logger.warning("[NPM] Failed to parse package.json")
            return []
    
    def parse_requirements_txt(self, content: str) -> List[Dict]:
        """
        Parse requirements.txt for Python MAJOR frameworks only.
        
        Args:
            content: Raw requirements.txt content
            
        Returns:
            List of MAJOR dependency dicts (filtered)
        """
        deps = []
        lines = content.split('\n')
        
        for line in lines:
            line = line.strip()
            
            # Skip comments and empty lines
            if not line or line.startswith('#'):
                continue
            
            # Parse package name and version
            match = re.match(r'^([a-zA-Z0-9\-_\.]+)([=<>!~]+.*)?$', line)
            if match:
                name = match.group(1).lower()
                version = match.group(2) if match.group(2) else ''
                
                # Only add if it's a major framework
                if self._is_major_framework(name, 'pypi'):
                    deps.append({
                        'name': name,
                        'version': self._clean_version(version),
                        'type': 'production',
                        'ecosystem': 'pypi',
                        'source_file': 'requirements.txt'
                    })
        
        logger.info(f"[PYPI] Found {len(deps)} major frameworks in requirements.txt")
        return deps
    
    def parse_pyproject_toml(self, content: str) -> List[Dict]:
        """
        Parse pyproject.toml for Python MAJOR frameworks only.
        
        Args:
            content: Raw pyproject.toml content
            
        Returns:
            List of MAJOR dependency dicts (filtered)
        """
        deps = []
        
        try:
            # Simple regex-based parsing (avoiding heavy toml library)
            dependencies_section = re.search(r'\[tool\.poetry\.dependencies\](.*?)(?=\n\[|\Z)', content, re.DOTALL)
            if dependencies_section:
                dep_text = dependencies_section.group(1)
                
                for line in dep_text.split('\n'):
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue
                    
                    match = re.match(r'^([a-zA-Z0-9\-_]+)\s*=\s*["\']([^"\']+)["\']', line)
                    if match:
                        name = match.group(1).lower()
                        version = match.group(2)
                        
                        if self._is_major_framework(name, 'pypi'):
                            deps.append({
                                'name': name,
                                'version': self._clean_version(version),
                                'type': 'production',
                                'ecosystem': 'pypi',
                                'source_file': 'pyproject.toml'
                            })
            
            logger.info(f"[PYPI] Found {len(deps)} major frameworks in pyproject.toml")
            return deps
            
        except Exception as e:
            logger.warning(f"[PYPI] Failed to parse pyproject.toml: {e}")
            return []
    
    def parse_go_mod(self, content: str) -> List[Dict]:
        """
        Parse go.mod for Go MAJOR frameworks only.
        
        Args:
            content: Raw go.mod content
            
        Returns:
            List of MAJOR dependency dicts (filtered)
        """
        deps = []
        lines = content.split('\n')
        
        in_require = False
        for line in lines:
            line = line.strip()
            
            if line.startswith('require'):
                in_require = True
                continue
            
            if in_require and line == ')':
                in_require = False
                continue
            
            if in_require or line.startswith('require '):
                match = re.match(r'([a-zA-Z0-9\-_/.]+)\s+v?([0-9.]+)', line)
                if match:
                    name = match.group(1)
                    version = match.group(2)
                    
                    if self._is_major_framework(name, 'go'):
                        deps.append({
                            'name': name,
                            'version': version,
                            'type': 'production',
                            'ecosystem': 'go',
                            'source_file': 'go.mod'
                        })
        
        logger.info(f"[GO] Found {len(deps)} major frameworks in go.mod")
        return deps
    
    def parse_gemfile(self, content: str) -> List[Dict]:
        """
        Parse Gemfile for Ruby MAJOR frameworks only.
        
        Args:
            content: Raw Gemfile content
            
        Returns:
            List of MAJOR dependency dicts (filtered)
        """
        deps = []
        lines = content.split('\n')
        
        for line in lines:
            line = line.strip()
            
            if not line or line.startswith('#'):
                continue
            
            match = re.match(r"gem\s+['\"]([^'\"]+)['\"](?:,\s*['\"]([^'\"]+)['\"])?", line)
            if match:
                name = match.group(1)
                version = match.group(2) if match.group(2) else ''
                
                if self._is_major_framework(name, 'rubygems'):
                    deps.append({
                        'name': name,
                        'version': self._clean_version(version),
                        'type': 'production',
                        'ecosystem': 'rubygems',
                        'source_file': 'Gemfile'
                    })
        
        logger.info(f"[RUBY] Found {len(deps)} major frameworks in Gemfile")
        return deps
    
    def parse_composer_json(self, content: str) -> List[Dict]:
        """
        Parse composer.json for PHP MAJOR frameworks only.
        
        Args:
            content: Raw composer.json content
            
        Returns:
            List of MAJOR dependency dicts (filtered)
        """
        try:
            data = json.loads(content)
            deps = []
            
            if 'require' in data:
                for name, version in data['require'].items():
                    if name == 'php':
                        continue
                    
                    if self._is_major_framework(name, 'packagist'):
                        deps.append({
                            'name': name,
                            'version': self._clean_version(version),
                            'type': 'production',
                            'ecosystem': 'packagist',
                            'source_file': 'composer.json'
                        })
            
            logger.info(f"[PHP] Found {len(deps)} major frameworks in composer.json")
            return deps
            
        except json.JSONDecodeError:
            logger.warning("[PHP] Failed to parse composer.json")
            return []
    
    def parse_cargo_toml(self, content: str) -> List[Dict]:
        """
        Parse Cargo.toml for Rust MAJOR frameworks only.
        
        Args:
            content: Raw Cargo.toml content
            
        Returns:
            List of MAJOR dependency dicts (filtered)
        """
        deps = []
        
        dependencies_section = re.search(r'\[dependencies\](.*?)(?=\n\[|\Z)', content, re.DOTALL)
        if dependencies_section:
            dep_text = dependencies_section.group(1)
            
            for line in dep_text.split('\n'):
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                
                match = re.match(r'^([a-zA-Z0-9\-_]+)\s*=\s*["\']([^"\']+)["\']', line)
                if match:
                    name = match.group(1)
                    version = match.group(2)
                    
                    if self._is_major_framework(name, 'cargo'):
                        deps.append({
                            'name': name,
                            'version': self._clean_version(version),
                            'type': 'production',
                            'ecosystem': 'cargo',
                            'source_file': 'Cargo.toml'
                        })
        
        logger.info(f"[RUST] Found {len(deps)} major frameworks in Cargo.toml")
        return deps
    
    def parse_all(self, dependency_files: Dict[str, str]) -> List[Dict]:
        """
        Parse all dependency files and return ONLY major frameworks.
        
        Args:
            dependency_files: Dict mapping filename -> content
            
        Returns:
            Combined list of MAJOR framework dependencies (filtered)
        """
        all_deps = []
        
        parsers = {
            'package.json': self.parse_package_json,
            'requirements.txt': self.parse_requirements_txt,
            'pyproject.toml': self.parse_pyproject_toml,
            'go.mod': self.parse_go_mod,
            'Gemfile': self.parse_gemfile,
            'composer.json': self.parse_composer_json,
            'Cargo.toml': self.parse_cargo_toml,
        }
        
        for filename, content in dependency_files.items():
            if filename in parsers:
                deps = parsers[filename](content)
                all_deps.extend(deps)
        
        logger.info(f"[TOTAL] Extracted {len(all_deps)} MAJOR frameworks across all files")
        return all_deps
    
    def _is_major_framework(self, package_name: str, ecosystem: str) -> bool:
        """
        Check if a package is a major framework worth showing.
        
        Args:
            package_name: Package name (lowercase)
            ecosystem: Ecosystem (npm, pypi, etc.)
            
        Returns:
            True if it's a major framework, False otherwise
        """
        package_name = package_name.lower()
        
        if ecosystem not in self.major_frameworks:
            return False
        
        major_list = self.major_frameworks[ecosystem]
        
        # Exact match
        if package_name in major_list:
            return True
        
        # Partial match for scoped packages (@vue/cli, etc.)
        for major in major_list:
            if major in package_name or package_name in major:
                return True
        
        return False
    
    def _clean_version(self, version: str) -> str:
        """
        Clean version string by removing operators and extra characters.
        
        Args:
            version: Raw version string (e.g., "^18.2.0", ">=4.2.0")
            
        Returns:
            Cleaned version string (e.g., "18.2.0", "4.2.0")
        """
        if not version:
            return ""
        
        # Remove common version operators
        version = re.sub(r'^[\^~>=<]+', '', version.strip())
        # Remove any trailing operators
        version = re.sub(r'[,\s].*$', '', version)
        return version.strip()
    
    def _build_major_frameworks(self) -> Dict[str, List[str]]:
        """
        Build list of major frameworks per ecosystem.
        
        These are the frameworks that matter for job matching.
        Utility packages are excluded.
        
        Returns:
            Dict mapping ecosystem -> list of major framework names
        """
        return {
            # JavaScript/TypeScript (NPM)
            'npm': [
                # Frontend Frameworks
                'react', 'vue', 'angular', 'svelte', 'preact', 'solid-js',
                '@angular/core', '@vue/cli', 'next', 'nuxt', 'gatsby',
                'remix', 'astro', 'sveltekit',
                
                # Backend Frameworks
                'express', 'koa', 'hapi', 'fastify', 'nest', '@nestjs/core',
                'socket.io', 'apollo-server', 'graphql',
                
                # Mobile
                'react-native', 'expo', 'ionic',
                
                # State Management
                'redux', 'mobx', 'zustand', 'recoil', 'pinia', 'vuex', 'ngrx',
                
                # UI Libraries
                'mui', '@mui/material', 'chakra-ui', 'ant-design', 'mantine',
                'tailwindcss', 'bootstrap', 'styled-components',
                
                # Testing
                'jest', 'mocha', 'chai', 'cypress', 'playwright', 'vitest',
                
                # Build Tools
                'webpack', 'vite', 'rollup', 'parcel', 'esbuild',
                
                # Databases/ORMs
                'mongoose', 'sequelize', 'typeorm', 'prisma', 'drizzle-orm',
                
                # Authentication
                'passport', 'next-auth', 'auth0',
            ],
            
            # Python (PyPI)
            'pypi': [
                # Web Frameworks
                'django', 'flask', 'fastapi', 'tornado', 'sanic', 'aiohttp',
                'pyramid', 'bottle', 'falcon',
                
                # AI/ML
                'tensorflow', 'pytorch', 'keras', 'scikit-learn', 'xgboost',
                'lightgbm', 'catboost', 'transformers', 'langchain',
                
                # Data Science
                'pandas', 'numpy', 'scipy', 'matplotlib', 'seaborn', 'plotly',
                
                # ORMs/Databases
                'sqlalchemy', 'peewee', 'mongoengine', 'redis', 'psycopg2',
                
                # Testing
                'pytest', 'unittest2', 'nose',
                
                # Async
                'celery', 'asyncio', 'aiofiles',
            ],
            
            # Go
            'go': [
                'gin', 'echo', 'fiber', 'chi', 'beego', 'iris', 'revel',
                'gorm', 'sqlx', 'grpc', 'gorilla/mux',
            ],
            
            # Ruby
            'rubygems': [
                'rails', 'sinatra', 'hanami', 'grape', 'roda',
                'devise', 'activerecord', 'sequel',
            ],
            
            # PHP
            'packagist': [
                'laravel/framework', 'symfony/symfony', 'slim/slim',
                'codeigniter', 'lumen', 'doctrine/orm', 'guzzlehttp/guzzle',
            ],
            
            # Rust
            'cargo': [
                'actix-web', 'rocket', 'axum', 'warp', 'tokio',
                'serde', 'diesel', 'sqlx',
            ]
        }


# Singleton instance
dependency_parser = DependencyParser()
