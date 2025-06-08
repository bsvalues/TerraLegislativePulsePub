import os
import shutil
from datetime import datetime
import logging
from pathlib import Path
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CodebaseCleaner:
    def __init__(self):
        self.archive_dir = "archive"
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.archive_path = os.path.join(self.archive_dir, f"archive_{self.timestamp}")
        self.metadata = {
            "archived_at": datetime.now().isoformat(),
            "archived_items": []
        }

    def create_archive_structure(self):
        os.makedirs(self.archive_path, exist_ok=True)
        for subdir in ["code", "assets", "config"]:
            os.makedirs(os.path.join(self.archive_path, subdir), exist_ok=True)
            
    def is_file_used(self, file_path):
        if file_path.endswith(('.pyc', '.pyo', '__pycache__')):
            return False
            
        if file_path.startswith(('.git', 'archive', 'venv', 'env')):
            return False
            
        if file_path in ['main.py', 'app.py', 'config.py', 'models.py']:
            return True
            
        return True
        
    def archive_file(self, file_path):
        if not self.is_file_used(file_path):
            rel_path = os.path.relpath(file_path)
            archive_file_path = os.path.join(self.archive_path, rel_path)
            os.makedirs(os.path.dirname(archive_file_path), exist_ok=True)
            shutil.move(file_path, archive_file_path)
            logger.info(f"Archived: {rel_path}")
            self.metadata["archived_items"].append({
                "original_path": file_path,
                "archive_path": archive_file_path,
                "category": "code",
                "archived_at": datetime.now().isoformat()
            })
            
    def cleanup_directory(self, directory):
        for root, dirs, files in os.walk(directory):
            for file in files:
                file_path = os.path.join(root, file)
                self.archive_file(file_path)
                
    def cleanup(self):
        logger.info("Starting codebase cleanup...")
        self.create_archive_structure()
        
        directories_to_clean = [
            'utils',
            'services',
            'routes',
            'templates',
            'static',
            'agents',
            'mcp'
        ]
        
        for directory in directories_to_clean:
            if os.path.exists(directory):
                self.cleanup_directory(directory)
                
        logger.info(f"Cleanup completed. Archived files can be found in: {self.archive_path}")

    def save_metadata(self):
        metadata_path = os.path.join(self.archive_dir, "archive_metadata.json")
        with open(metadata_path, "w") as f:
            json.dump(self.metadata, f, indent=2)

def main():
    cleaner = CodebaseCleaner()
    cleaner.cleanup()
    cleaner.save_metadata()

if __name__ == "__main__":
    main() 