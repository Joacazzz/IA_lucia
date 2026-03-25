import sys
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

logger.info("=== Iniciando aplicacao ===")
logger.info(f"Python: {sys.version}")
logger.info(f"DATABASE_URL presente: {'DATABASE_URL' in os.environ}")
logger.info(f"PORT: {os.environ.get('PORT', 'nao definida')}")

sys.path.insert(0, os.path.dirname(__file__))

try:
    logger.info("Importando backend.app.main...")
    from backend.app.main import app
    logger.info("App importado com sucesso!")
except Exception as e:
    logger.error(f"ERRO ao importar app: {e}")
    raise
