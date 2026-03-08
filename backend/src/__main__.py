"""Application entry point"""
import logging
from src.main import app
from src.config import get_settings

settings = get_settings()

# Configure logging
logging.basicConfig(
    level=settings.api_log_level,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


if __name__ == "__main__":
    import uvicorn
    
    logger.info(f"Starting HHM Backend on {settings.api_host}:{settings.api_port}")
    logger.info(f"Environment: {settings.environment}")
    logger.info(f"Debug: {settings.debug}")
    
    uvicorn.run(
        "src.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug,
        log_level=settings.api_log_level.lower(),
    )
