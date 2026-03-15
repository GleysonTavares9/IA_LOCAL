import logging
import sys
from pathlib import Path
from app.config.settings import LOG_DIR

def setup_logger(name: str, log_file: str = "app.log", level=logging.INFO):
    """Configura um logger para o projeto."""
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    handler = logging.FileHandler(LOG_DIR / log_file)
    handler.setFormatter(formatter)
    
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)
    logger.addHandler(console_handler)
    
    return logger

# Logger padrão
logger = setup_logger("ia_local")
