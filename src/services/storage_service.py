"""
JSON Storage Service for GitHub Analysis Data

Stores all analyzed GitHub profiles as JSON files in the db/ directory.
Each user gets their own JSON file with complete analysis data.
"""
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List
from utils.logger import logger


class StorageService:
    """
    Handles saving and loading GitHub analysis data to/from JSON files.
    
    Storage Structure:
        db/
        ├── {username}.json  # Full analysis data
        └── ...
    """
    
    def __init__(self, storage_dir: str = "db"):
        """
        Initialize storage service.
        
        Args:
            storage_dir: Directory to store JSON files (default: "db")
        """
        # Get the directory where this file is located (src/services/)
        current_dir = Path(__file__).parent.parent  # Go up to src/
        self.storage_dir = current_dir / storage_dir
        self.storage_dir.mkdir(exist_ok=True)
        logger.info(f"[STORAGE] Storage directory: {self.storage_dir.absolute()}")
    
    def save_analysis(self, username: str, data: Dict[str, Any]) -> str:
        """
        Save GitHub analysis data to JSON file.
        
        Args:
            username: GitHub username
            data: Complete analysis data (user + repositories)
        
        Returns:
            Path to saved file
        """
        try:
            filename = f"{username}.json"
            filepath = self.storage_dir / filename
            
            # Prepare storage document
            document = {
                "username": username,
                "analyzed_at": datetime.utcnow().isoformat() + "Z",
                "data": data
            }
            
            # Save to JSON file with pretty formatting
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(document, f, indent=2, ensure_ascii=False)
            
            logger.info(f"[SAVE] Saved analysis for '{username}' to {filepath}")
            return str(filepath)
            
        except Exception as e:
            logger.error(f"[ERROR] Failed to save analysis for '{username}': {e}")
            raise
    
    def load_analysis(self, username: str) -> Optional[Dict[str, Any]]:
        """
        Load GitHub analysis data from JSON file.
        
        Args:
            username: GitHub username
        
        Returns:
            Analysis data if found, None otherwise
        """
        try:
            filename = f"{username}.json"
            filepath = self.storage_dir / filename
            
            if not filepath.exists():
                logger.warning(f"[WARN] No stored data found for '{username}'")
                return None
            
            with open(filepath, 'r', encoding='utf-8') as f:
                document = json.load(f)
            
            logger.info(f"[LOAD] Loaded analysis for '{username}' from {filepath}")
            return document
            
        except Exception as e:
            logger.error(f"[ERROR] Failed to load analysis for '{username}': {e}")
            return None
    
    def get_all_stored_users(self) -> List[str]:
        """
        Get list of all usernames with stored data.
        
        Returns:
            List of usernames
        """
        try:
            json_files = list(self.storage_dir.glob("*.json"))
            usernames = [f.stem for f in json_files]
            logger.info(f"[STATS] Found {len(usernames)} stored profiles")
            return sorted(usernames)
        except Exception as e:
            logger.error(f"[ERROR] Failed to list stored users: {e}")
            return []
    
    def delete_analysis(self, username: str) -> bool:
        """
        Delete stored analysis for a user.
        
        Args:
            username: GitHub username
        
        Returns:
            True if deleted, False otherwise
        """
        try:
            filename = f"{username}.json"
            filepath = self.storage_dir / filename
            
            if filepath.exists():
                filepath.unlink()
                logger.info(f"[DELETE] Deleted analysis for '{username}'")
                return True
            else:
                logger.warning(f"[WARN] No file to delete for '{username}'")
                return False
                
        except Exception as e:
            logger.error(f"[ERROR] Failed to delete analysis for '{username}': {e}")
            return False
    
    def get_storage_stats(self) -> Dict[str, Any]:
        """
        Get storage statistics.
        
        Returns:
            Statistics about stored data
        """
        try:
            users = self.get_all_stored_users()
            total_files = len(users)
            
            # Calculate total storage size
            total_size = sum(
                (self.storage_dir / f"{user}.json").stat().st_size 
                for user in users
            )
            
            return {
                "total_profiles": total_files,
                "total_size_bytes": total_size,
                "total_size_mb": round(total_size / (1024 * 1024), 2),
                "users": users
            }
        except Exception as e:
            logger.error(f"[ERROR] Failed to get storage stats: {e}")
            return {}


# Create singleton instance
storage_service = StorageService()
