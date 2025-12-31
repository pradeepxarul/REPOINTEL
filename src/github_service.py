"""GitHub API client with GitHub App authentication (JWT)"""
import aiohttp
import jwt
import time
import asyncio
from typing import Dict, List, Optional, Any
from config import settings
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
    
    async def _get_last_commit_date(self, owner: str, repo: str) -> Optional[str]:
        """
        Get last commit date for repository
        
        GET /repos/{owner}/{repo}/commits?per_page=1
        
        Returns:
            ISO timestamp of last commit, or None if not found
        """
        await self.ensure_token()
        
        url = f"https://api.github.com/repos/{owner}/{repo}/commits?per_page=1"
        headers = {"Authorization": f"token {self.token}"}
        
        try:
            async with self.session.get(url, headers=headers) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    if data and len(data) > 0:
                        return data[0]['commit']['author']['date']
                return None
        except asyncio.TimeoutError:
            logger.warning(f"⏱️ Timeout getting commits for {owner}/{repo}")
            return None
        except Exception as e:
            logger.warning(f"❌ Error getting commits for {owner}/{repo}: {e}")
            return None
    
    async def _analyze_single_repo(self, repo_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze single repository: get languages + README + last commit in parallel
        
        Args:
            repo_data: Repository object from GitHub API
        
        Returns:
            Enriched repository data with languages, README, and commit activity
        """
        owner = repo_data['owner']['login']
        repo = repo_data['name']
        
        # Fetch languages, README, and last commit in parallel (3 calls per repo)
        lang_task = self._get_repo_languages(owner, repo)
        readme_task = self._get_repo_readme(owner, repo)
        commit_task = self._get_last_commit_date(owner, repo)
        
        languages, readme, last_commit_date = await asyncio.gather(
            lang_task, readme_task, commit_task
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
        
        # Calculate days since last commit
        days_since_commit = None
        if last_commit_date:
            try:
                from datetime import datetime
                commit_dt = datetime.fromisoformat(last_commit_date.replace('Z', '+00:00'))
                now = datetime.now(commit_dt.tzinfo)
                days_since_commit = (now - commit_dt).days
            except:
                pass
        
        # Build enriched repo data with ALL popularity and activity metrics
        return {
            "name": repo_data['name'],
            "full_name": repo_data['full_name'],
            "description": repo_data.get('description'),
            "html_url": repo_data['html_url'],
            
            # Popularity metrics (already in repo_data!)
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
            "pushed_at": repo_data.get('pushed_at'),
            
            # Commit activity (NEW!)
            "last_commit_date": last_commit_date,
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
            } if readme else None
        }
    
    async def analyze_profile(self, username: str) -> Dict[str, Any]:
        """
        MAIN METHOD: Complete GitHub profile analysis
        
        Flow:
        1. Get user profile (1 API call)
        2. Get user repositories (1 API call)
        3. For each repo, get languages + README + last commit (3N API calls in parallel)
        
        Total API calls: 2 + (3 × N repos) ≈ 47 calls for 15 repos
        Expected time: ~1.5 seconds
        
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
        
        # Step 3: Analyze all repos in parallel (languages + READMEs + commits)
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
        api_calls = 2 + (len(repos) * 3)  # profile + repos + (languages + readme + commits) per repo
        
        return {
            "profile": profile,
            "repositories": valid_repos,
            "api_calls": api_calls,
            "latency_ms": int((end_time - start_time) * 1000)
        }
