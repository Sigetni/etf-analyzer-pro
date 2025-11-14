# config.py
import os
from pathlib import Path

# API Key da Alpha Vantage
ALPHA_VANTAGE_API_KEY = os.getenv('ALPHA_VANTAGE_KEY', 'XQQGFVANPDON7AEK')

# Configurações de cache
CACHE_DIR = Path('cache')
CACHE_DIR.mkdir(exist_ok=True)
CACHE_EXPIRY_DAYS = 7

# Configurações da aplicação
APP_TITLE = "ETF Analyzer Pro"
APP_ICON = "📊"
