import os
from pathlib import Path

class Config:
    """Configuration settings for the Telegram Torrent Bot"""
    
    # Bot Configuration
    BOT_TOKEN = os.getenv('BOT_TOKEN', '')
    
    # Download Configuration
    DOWNLOAD_DIR = Path('./downloads')
    MAX_FILE_SIZE = 4 * 1024 * 1024 * 1024  # 4GB in bytes
    MAX_CONCURRENT_DOWNLOADS = 3
    
    # Torrent Configuration
    TORRENT_LISTEN_PORT_MIN = 6881
    TORRENT_LISTEN_PORT_MAX = 6891
    TORRENT_TIMEOUT = 300  # 5 minutes timeout for initial connection
    
    # Progress Update Configuration
    PROGRESS_UPDATE_INTERVAL = 5  # seconds
    PROGRESS_UPDATE_THRESHOLD = 5  # percentage
    
    # Upload Configuration
    UPLOAD_CHUNK_SIZE = 1024 * 1024  # 1MB chunks
    UPLOAD_TIMEOUT = 600  # 10 minutes timeout for uploads
    
    # Logging Configuration
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    # Cleanup Configuration
    CLEANUP_AFTER_UPLOAD = True
    CLEANUP_FAILED_DOWNLOADS = True
    
    # Rate Limiting
    MAX_DOWNLOADS_PER_USER = 1
    DOWNLOAD_COOLDOWN = 60  # seconds between downloads per user
    
    @classmethod
    def validate(cls):
        """Validate configuration settings"""
        if not cls.BOT_TOKEN:
            raise ValueError("BOT_TOKEN environment variable is required")
        
        # Create download directory if it doesn't exist
        cls.DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)
        
        return True

# Initialize configuration
config = Config()

# Validate configuration on import
config.validate()
