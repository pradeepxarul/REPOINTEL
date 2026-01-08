"""GitHub API client with GitHub App authentication (JWT)"""
import aiohttp
import jwt
import time
import asyncio
from typing import Dict, List, Optional, Any
from core.config import settings
from utils.logger import logger
from datetime import datetime


class GitHubService:
    """
    GitHub API client using GitHub App authentication
    
    Features:
    - JWT token generation and auto-refresh
    - Installation token exchange (1 hour validity)
    - Parallel API calls (up to 32 concurrent)
    - Complete error handling and timeouts
    
    Authentication Flow:
    1. Generate JWT using App ID and Private Key (10 min validity)
    2. Exchange JWT for installation access token (1 hour validity)
    3. Use installation token for all API calls
    4. Auto-refresh when token expires
    """
    
    def __init__(self):
        self.app_id = settings.GITHUB_APP_ID
        self.private_key = settings.GITHUB_PRIVATE_KEY
        self.installation_id = settings.GITHUB_INSTALLATION_ID
        self.token = None
        self.expires_at = 0
        self.session = None
    
    async def __aenter__(self):
        """Async context manager entry - create HTTP session"""
        timeout = aiohttp.ClientTimeout(total=settings.API_TIMEOUT_SECONDS)
        self.session = aiohttp.ClientSession(timeout=timeout)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit - close HTTP session"""
        if self.session:
            await self.session.close()
    
    async def _get_installation_token(self) -> str:
        """
        Generate JWT and exchange for installation access token
        
        Flow:
        1. Create JWT with App ID (10 min validity)
        2. POST to GitHub API to exchange JWT for installation token
        3. Store token and expiration time
        
        Returns:
            Installation access token
        
        Raises:
            Exception: If token exchange fails
        """
        now = int(time.time())
        
        # Create JWT payload
        payload = {
            "iat": now,  # Issued at
            "exp": now + 600,  # Expires in 10 minutes
            "iss": str(self.app_id)  # Issuer (App ID)
        }
        
        # Encode JWT using RS256 algorithm with private key
        jwt_token = jwt.encode(payload, self.private_key, algorithm="RS256")
        
        # Exchange JWT for installation token
        url = f"https://api.github.com/app/installations/{self.installation_id}/access_tokens"
        headers = {
            "Authorization": f"Bearer {jwt_token}",
            "Accept": "application/vnd.github.v3+json"
        }
        
        async with self.session.post(url, headers=headers, json={}) as resp:
            if resp.status == 201:
                data = await resp.json()
                self.token = data["token"]
                self.expires_at = now + 3600  # Token valid for 1 hour
                logger.info(f"✅ Generated new GitHub token for installation {self.installation_id}")
                return self.token
            
            error_msg = await resp.text()
            raise Exception(f"Token exchange failed ({resp.status}): {error_msg}")
    
    async def ensure_token(self):
        """Auto-refresh token if expired or about to expire (5 min buffer)"""
        now = time.time()
        if not self.token or now > self.expires_at - 300:
            await self._get_installation_token()
    
    async def get_user_profile(self, username: str) -> Dict[str, Any]:
        """
        Get GitHub user profile
        
        GET /users/{username}
        
        Args:
            username: GitHub username
        
        Returns:
            User profile data
        
        Raises:
            ValueError: If user not found
            Exception: If API error occurs
        """
        await self.ensure_token()
        
        url = f"https://api.github.com/users/{username}"
        headers = {"Authorization": f"token {self.token}"}
        
        async with self.session.get(url, headers=headers) as resp:
            if resp.status == 404:
                raise ValueError(f"User '{username}' not found on GitHub")
            if resp.status != 200:
                raise Exception(f"GitHub API error ({resp.status}): {await resp.text()}")
            
            return await resp.json()
    
    async def get_user_repos(self, username: str) -> List[Dict[str, Any]]:
        """
        Get user repositories, sorted by stars, filtered (no forks/archived)
        
        GET /users/{username}/repos?sort=stars&per_page=100&direction=desc
        
        Args:
            username: GitHub username
        
        Returns:
            List of repository objects (top MAX_REPOS_PER_USER by stars)
        """
        await self.ensure_token()
        
        url = f"https://api.github.com/users/{username}/repos?sort=stars&per_page=100&direction=desc"
        headers = {"Authorization": f"token {self.token}"}
        
        async with self.session.get(url, headers=headers) as resp:
            if resp.status != 200:
                raise Exception(f"GitHub API error ({resp.status}): {await resp.text()}")
            
            repos = await resp.json()
            
            # Filter: no forks, no archived repos
            filtered = [
                r for r in repos
                if not r.get('fork', False) and not r.get('archived', False)
            ]
            
            # Sort by stars and limit to max repos
            sorted_repos = sorted(
                filtered,
                key=lambda x: x.get('stargazers_count', 0),
                reverse=True
            )[:settings.MAX_REPOS_PER_USER]
            
            logger.info(f"📦 Found {len(sorted_repos)} repos for {username}")
            return sorted_repos
    
    async def _get_repo_languages(self, owner: str, repo: str) -> Dict[str, int]:
        """
        Get repository language statistics
        
        GET /repos/{owner}/{repo}/languages
        
        Returns:
            Dict of language: bytes (e.g., {"Python": 12345, "JavaScript": 6789})
        """
        await self.ensure_token()
        
        url = f"https://api.github.com/repos/{owner}/{repo}/languages"
        headers = {"Authorization": f"token {self.token}"}
        
        try:
            async with self.session.get(url, headers=headers) as resp:
                if resp.status == 200:
                    return await resp.json()
                return {}
        except asyncio.TimeoutError:
            logger.warning(f"⏱️ Timeout getting languages for {owner}/{repo}")
            return {}
        except Exception as e:
            logger.warning(f"❌ Error getting languages for {owner}/{repo}: {e}")
            return {}
    
    async def _get_repo_readme(self, owner: str, repo: str) -> Optional[str]:
        """
        Get repository README content in plain text
        
        GET /repos/{owner}/{repo}/readme (with raw content type)
        
        Returns:
            README content as plain text, or None if not found
        """
        await self.ensure_token()
        
        url = f"https://api.github.com/repos/{owner}/{repo}/readme"
        headers = {
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github.v3.raw"  # Request raw content
        }
        
        try:
            async with self.session.get(url, headers=headers) as resp:
                if resp.status == 200:
                    return await resp.text()
                return None
        except asyncio.TimeoutError:
            logger.warning(f"⏱️ Timeout getting README for {owner}/{repo}")
            return None
        except Exception as e:
            logger.warning(f"❌ Error getting README for {owner}/{repo}: {e}")
            return None
    
    async def _get_repo_tree(self, owner: str, repo: str, default_branch: str = 'main') -> List[Dict[str, Any]]:
        """
        Get repository file tree to find all files
        
        GET /repos/{owner}/{repo}/git/trees/{branch}?recursive=1
        
        Args:
            owner: Repository owner
            repo: Repository name  
            default_branch: Default branch (main/master)
        
        Returns:
            List of file objects with path, type, size
        """
        await self.ensure_token()
        
        # Try main branch first, fallback to master if not found
        for branch in [default_branch, 'master' if default_branch == 'main' else 'main']:
            url = f"https://api.github.com/repos/{owner}/{repo}/git/trees/{branch}?recursive=1"
            headers = {"Authorization": f"token {self.token}"}
            
            try:
                async with self.session.get(url, headers=headers) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        return data.get('tree', [])
            except Exception as e:
                logger.warning(f"⚠️ Error getting tree for {owner}/{repo} on {branch}: {e}")
                continue
        
        return []
    
    async def _fetch_markdown_content(self, owner: str, repo: str, file_path: str, max_size_kb: int = 100) -> Optional[Dict[str, Any]]:
        """
        Fetch content of a single markdown file
        
        GET /repos/{owner}/{repo}/contents/{file_path}
        
        Args:
            owner: Repository owner
            repo: Repository name
            file_path: Path to markdown file
            max_size_kb: Maximum file size to fetch (default 100KB)
        
        Returns:
            Dict with filename, path, content, length_chars or None if error/too large
        """
        await self.ensure_token()
        
        url = f"https://api.github.com/repos/{owner}/{repo}/contents/{file_path}"
        headers = {
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github.v3.raw"  # Get raw content
        }
        
        try:
            async with self.session.get(url, headers=headers) as resp:
                if resp.status == 200:
                    content = await resp.text()
                    
                    # Check size limit (100KB default)
                    if len(content) > max_size_kb * 1024:
                        logger.warning(f"⚠️ Skipping large markdown file {file_path} ({len(content)} bytes)")
                        return None
                    
                    return {
                        "filename": file_path.split('/')[-1],
                        "path": file_path,
                        "content": content,  # COMPLETE content, no truncation
                        "length_chars": len(content)
                    }
                return None
        except Exception as e:
            logger.warning(f"❌ Error fetching {file_path}: {e}")
            return None
    
    async def _get_all_markdown_files(self, owner: str, repo: str, default_branch: str = 'main', max_files: int = 20) -> List[Dict[str, Any]]:
        """
        Find and extract ALL markdown files from repository
        
        Process:
        1. Get repository file tree
        2. Filter for .md files (exclude README.md as it's fetched separately)
        3. Fetch content for each markdown file in parallel
        4. Return complete list with full content
        
        Args:
            owner: Repository owner
            repo: Repository name
            default_branch: Default branch name
            max_files: Maximum number of markdown files to extract (default 20)
        
        Returns:
            List of markdown file objects with complete content
        """
        # Step 1: Get file tree
        tree = await self._get_repo_tree(owner, repo, default_branch)
        
        if not tree:
            return []
        
        # Step 2: Filter for .md files (case-insensitive, exclude README.md)
        md_files = [
            item for item in tree
            if item.get('type') == 'blob' 
            and item.get('path', '').lower().endswith('.md')
            and item.get('path', '').lower() not in ['readme.md', 'readme.markdown']
        ]
        
        # Limit number of files
        md_files = md_files[:max_files]
        
        if not md_files:
            logger.info(f"📄 No additional markdown files found in {owner}/{repo}")
            return []
        
        logger.info(f"📄 Found {len(md_files)} markdown files in {owner}/{repo}")
        
        # Step 3: Fetch content for all markdown files in parallel
        fetch_tasks = [
            self._fetch_markdown_content(owner, repo, item['path'])
            for item in md_files
        ]
        
        results = await asyncio.gather(*fetch_tasks, return_exceptions=True)
        
        # Filter out None values and exceptions
        valid_files = [
            r for r in results
            if r is not None and not isinstance(r, Exception)
        ]
        
        logger.info(f"✅ Successfully fetched {len(valid_files)} markdown files from {owner}/{repo}")
        return valid_files

    
    async def _analyze_single_repo(self, repo_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze single repository: get languages + README + ALL markdown files in parallel
        
        Args:
            repo_data: Repository object from GitHub API
        
        Returns:
            Enriched repository data with languages, README, markdown files, and commit activity
        """
        owner = repo_data['owner']['login']
        repo = repo_data['name']
        default_branch = repo_data.get('default_branch', 'main')
        
        # Fetch languages, README, and ALL markdown files in parallel
        lang_task = self._get_repo_languages(owner, repo)
        readme_task = self._get_repo_readme(owner, repo)
        markdown_task = self._get_all_markdown_files(owner, repo, default_branch)
        
        languages, readme, markdown_files = await asyncio.gather(
            lang_task, readme_task, markdown_task
        )
        
        # Calculate language percentages
        if languages:
            total_bytes = sum(languages.values())
            percentages = {
                lang: round((bytes_ / total_bytes) * 100, 1)
                for lang, bytes_ in languages.items()
            } if total_bytes > 0 else {}
        else:
            percentages = {}
        
        # Calculate days since last commit using pushed_at (already in repo_data!)
        pushed_at = repo_data.get('pushed_at')
        days_since_commit = None
        if pushed_at:
            try:
                from datetime import datetime, timezone
                commit_dt = datetime.fromisoformat(pushed_at.replace('Z', '+00:00'))
                now = datetime.now(timezone.utc)
                days_since_commit = max(0, (now - commit_dt).days)
            except:
                pass
        
        # Build enriched repo data with ALL metrics
        return {
            "name": repo_data['name'],
            "full_name": repo_data['full_name'],
            "description": repo_data.get('description'),
            "html_url": repo_data['html_url'],
            
            # Popularity metrics (from repo_data)
            "stargazers_count": repo_data.get('stargazers_count', 0),
            "forks_count": repo_data.get('forks_count', 0),
            "watchers_count": repo_data.get('watchers_count', 0),
            "open_issues_count": repo_data.get('open_issues_count', 0),
            
            # Repository metadata
            "size_kb": repo_data.get('size', 0),
            "language": repo_data.get('language'),
            "topics": repo_data.get('topics', []),
            "archived": repo_data.get('archived', False),
            "is_fork": repo_data.get('fork', False),
            "has_wiki": repo_data.get('has_wiki', False),
            "has_projects": repo_data.get('has_projects', False),
            
            # Timestamps
            "created_at": repo_data.get('created_at', ''),
            "updated_at": repo_data.get('updated_at', ''),
            "pushed_at": pushed_at,
            
            # Commit activity (using pushed_at - NO extra API call!)
            "last_commit_date": pushed_at,  # Same as pushed_at
            "days_since_last_commit": days_since_commit,
            
            # Language breakdown
            "languages": {
                "raw_bytes": languages,
                "percentages": percentages
            },
            
            # README content
            "readme": {
                "content": readme,
                "length_chars": len(readme) if readme else 0,
                "has_readme": bool(readme)
            } if readme else None,
            
            # ALL Markdown Files (COMPLETE content extraction!)
            "markdown_files": markdown_files  # List of all .md files with full content
        }
    
    async def analyze_profile(self, username: str) -> Dict[str, Any]:
        """
        MAIN METHOD: Complete GitHub profile analysis
        
        Flow:
        1. Get user profile (1 API call)
        2. Get user repositories (1 API call)  
        3. For each repo, get languages + README (2N API calls in parallel)
        4. Use pushed_at from repo data for commit activity (no extra calls!)
        
        Total API calls: 2 + (2 × N repos) = 32 calls for 15 repos
        Expected time: ~1.2 seconds
        
        Args:
            username: GitHub username
        
        Returns:
            Complete analysis with profile, repos, languages, READMEs, commit activity
        """
        start_time = time.time()
        
        # Step 1-2: Get profile and repos in parallel
        profile_task = self.get_user_profile(username)
        repos_task = self.get_user_repos(username)
        
        profile, repos = await asyncio.gather(profile_task, repos_task)
        
        # Step 3: Analyze all repos in parallel (languages + READMEs)
        # Note: pushed_at for commit activity already in repo data - no extra calls needed!
        repo_tasks = [
            self._analyze_single_repo(repo)
            for repo in repos
        ]
        repo_results = await asyncio.gather(*repo_tasks, return_exceptions=True)
        
        # Filter out any errors
        valid_repos = [
            r for r in repo_results
            if not isinstance(r, Exception)
        ]
        
        end_time = time.time()
        api_calls = 2 + (len(repos) * 2)  # profile + repos + (languages + readme) per repo
        
        return {
            "profile": profile,
            "repositories": valid_repos,
            "api_calls": api_calls,
            "latency_ms": int((end_time - start_time) * 1000)
        }
