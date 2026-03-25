import sys
import os

# Adiciona o diretório raiz ao path para importar backend.app
sys.path.insert(0, os.path.dirname(__file__))

from backend.app.main import app
