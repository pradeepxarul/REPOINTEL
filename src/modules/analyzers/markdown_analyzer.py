"""
Markdown content extraction for comprehensive skill analysis.
Processes all .md files in a repository (README, docs, etc.)
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
try:
    from mrkdwn_analysis import MarkdownAnalyzer as MrkdwnAnalyzer
    MRKDWN_AVAILABLE = True
except ImportError:
    MRKDWN_AVAILABLE = False
from utils.logger import logger


@dataclass
class MarkdownContent:
    filename: str
    full_text: str
    headers: List[str]
    code_blocks: List[Dict[str, str]]
    metadata: Optional[Dict]
    word_count: int
    char_count: int


class MarkdownAnalyzer:
    """Extracts and parses markdown files from repositories."""
    
    def __init__(self):
        self.available = MRKDWN_AVAILABLE
        if not self.available:
            logger.warning("[MARKDOWN] Library not available, using fallback")
    
    def extract_all_content(self, repo: Dict) -> Dict[str, str]:
        """Extract content from all markdown files in the repo."""
        all_content = {}
        
        # Extract README
        readme = repo.get('readme', {})
        if readme and readme.get('has_readme'):
            readme_content = readme.get('content', '')
            if readme_content:
                all_content['readme'] = readme_content
        
        # Extract other markdown files  
        markdown_files = repo.get('markdown_files', [])
        for md_file in markdown_files:
            content = md_file.get('content', '')
            if content:
                # Clean key name: docs/api.md -> docs_api
                path = md_file.get('path', md_file.get('filename', ''))
                key = path.replace('.md', '').replace('/', '_').lower()
                all_content[key] = content
        
        logger.info(f"[MARKDOWN] Extracted {len(all_content)} files")
        return all_content
    
    def analyze_file(self, content: str, filename: str = "unknown") -> Optional[MarkdownContent]:
        """Parse a single markdown file into structured data."""
        if not content:
            return None
        
        try:
            if self.available:
                analyzer = MrkdwnAnalyzer(content)
                headers = self._get_headers(analyzer)
                code_blocks = self._get_code_blocks(analyzer)
                metadata = self._get_metadata(analyzer)
                
                return MarkdownContent(
                    filename=filename,
                    full_text=content,
                    headers=headers,
                    code_blocks=code_blocks,
                    metadata=metadata,
                    word_count=len(content.split()),
                    char_count=len(content)
                )
            else:
                return self._simple_parse(content, filename)
                
        except Exception as e:
            logger.warning(f"[MARKDOWN] Parse failed for {filename}: {e}")
            return self._simple_parse(content, filename)
    
    def _get_headers(self, analyzer) -> List[str]:
        """Extract headers using mrkdwn_analysis."""
        try:
            if hasattr(analyzer, 'get_headers'):
                return analyzer.get_headers()
            return []
        except:
            return []
    
    def _get_code_blocks(self, analyzer) -> List[Dict[str, str]]:
        """Extract code blocks with language tags."""
        try:
            if hasattr(analyzer, 'get_code_blocks'):
                blocks = analyzer.get_code_blocks()
                return [{'language': b.get('language', ''), 'code': b.get('code', '')} for b in blocks]
            return []
        except:
            return []
    
    def _get_metadata(self, analyzer) -> Optional[Dict]:
        """Extract YAML front matter."""
        try:
            if hasattr(analyzer, 'get_metadata'):
                return analyzer.get_metadata()
            return None
        except:
            return None
    
    def _simple_parse(self, content: str, filename: str) -> MarkdownContent:
        """Fallback parser using regex when library unavailable."""
        import re
        
        # Extract headers (# Title)
        headers = re.findall(r'^#+\s+(.+)$', content, re.MULTILINE)
        
        # Extract code blocks (```lang ... ```)
        code_pattern = r'```(\w+)?\n(.*?)```'
        code_matches = re.findall(code_pattern, content, re.DOTALL)
        code_blocks = [
            {'language': lang or 'text', 'code': code}
            for lang, code in code_matches
        ]
        
        return MarkdownContent(
            filename=filename,
            full_text=content,
            headers=headers,
            code_blocks=code_blocks,
            metadata=None,
            word_count=len(content.split()),
            char_count=len(content)
        )
    
    def combine_all_text(self, content_dict: Dict[str, str]) -> str:
        """Combine all markdown content into single text for analysis."""
        combined = []
        for source, text in content_dict.items():
            combined.append(f"# Source: {source}\n{text}\n\n")
        return '\n'.join(combined)


# Global instance
markdown_analyzer = MarkdownAnalyzer()
