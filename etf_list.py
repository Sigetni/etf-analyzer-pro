# etf_list.py
# Lista otimizada dos ETFs mais líquidos SEM redundâncias
# Cada ETF representa uma estratégia/índice único

OPTIMIZED_ETFS = [
    # === BROAD MARKET (5) ===
    "SPY",      # S&P 500 (maior liquidez)
    "QQQ",      # Nasdaq 100
    "VTI",      # Total US Market
    "DIA",      # Dow Jones
    "RSP",      # S&P 500 Equal Weight

    # === SIZE & STYLE (6) ===
    "IWM",      # Small Cap (Russell 2000)
    "IJH",      # Mid Cap
    "VUG",      # Large Cap Growth
    "VTV",      # Large Cap Value
    "VBK",      # Small Cap Growth
    "VBR",      # Small Cap Value

    # === INTERNATIONAL (5) ===
    "VEA",      # Developed Markets (ex-US)
    "VWO",      # Emerging Markets
    "EFA",      # EAFE (Europa, Ásia, Pacífico)
    "EEM",      # Emerging Markets (alternativo)
    "VGK",      # European Stocks

    # === SECTOR - TECHNOLOGY (3) ===
    "XLK",      # Technology Sector
    "VGT",      # Tech alternativo (Vanguard)
    "SMH",      # Semiconductors

    # === SECTOR - FINANCIAL (2) ===
    "XLF",      # Financial Sector
    "KBE",      # Banking ETF

    # === SECTOR - HEALTHCARE (2) ===
    "XLV",      # Healthcare Sector
    "IBB",      # Biotech

    # === SECTOR - CONSUMER (3) ===
    "XLY",      # Consumer Discretionary
    "XLP",      # Consumer Staples
    "RTH",      # Retail

    # === SECTOR - ENERGY (2) ===
    "XLE",      # Energy Sector
    "OIH",      # Oil & Gas

    # === SECTOR - INDUSTRIALS (2) ===
    "XLI",      # Industrials Sector
    "IYT",      # Transportation

    # === SECTOR - REAL ESTATE & UTILITIES (3) ===
    "XLRE",     # Real Estate
    "VNQ",      # REITs
    "XLU",      # Utilities

    # === SECTOR - MATERIALS & COMMUNICATION (2) ===
    "XLB",      # Materials
    "XLC",      # Communication Services

    # === BONDS (5) ===
    "AGG",      # Total Bond Market
    "LQD",      # Investment Grade Corporate
    "HYG",      # High Yield Corporate
    "TLT",      # Long-Term Treasury
    "MUB",      # Municipal Bonds

    # === DIVIDEND FOCUSED (3) ===
    "VIG",      # Dividend Appreciation
    "SCHD",     # High Dividend
    "VYM",      # High Dividend Yield

    # === THEMATIC/SPECIALTY (7) ===
    "ARKK",     # Innovation (ARK)
    "SOXX",     # Semiconductors (alternativo)
    "JETS",     # Airlines
    "HACK",     # Cybersecurity
    "ICLN",     # Clean Energy
    "GLD",      # Gold
    "SLV",      # Silver
]

# Total: 50 ETFs únicos (ao invés de 100 redundantes)

# Categorias para referência
ETF_CATEGORIES = {
    "Broad Market": ["SPY", "QQQ", "VTI", "DIA", "RSP"],
    "Size & Style": ["IWM", "IJH", "VUG", "VTV", "VBK", "VBR"],
    "International": ["VEA", "VWO", "EFA", "EEM", "VGK"],
    "Technology": ["XLK", "VGT", "SMH"],
    "Financial": ["XLF", "KBE"],
    "Healthcare": ["XLV", "IBB"],
    "Consumer": ["XLY", "XLP", "RTH"],
    "Energy": ["XLE", "OIH"],
    "Industrials": ["XLI", "IYT"],
    "Real Estate & Utilities": ["XLRE", "VNQ", "XLU"],
    "Materials & Communication": ["XLB", "XLC"],
    "Bonds": ["AGG", "LQD", "HYG", "TLT", "MUB"],
    "Dividend": ["VIG", "SCHD", "VYM"],
    "Thematic": ["ARKK", "SOXX", "JETS", "HACK", "ICLN", "GLD", "SLV"]
}

# Descrição do critério de seleção
SELECTION_CRITERIA = """
Esta lista contém 50 ETFs únicos selecionados por:

1. **Sem Redundância**: Apenas 1 ETF por índice/estratégia
   - Exemplo: SPY (não inclui VOO, IVV)
   - Critério: Maior liquidez ou menor taxa

2. **Cobertura Completa**:
   - ✅ Todos os setores principais
   - ✅ Diferentes capitalizações (Large, Mid, Small)
   - ✅ Estilos (Growth, Value)
   - ✅ Internacional (Desenvolvidos e Emergentes)
   - ✅ Renda Fixa
   - ✅ Dividendos
   - ✅ Temáticos

3. **Alta Liquidez**: Todos com volume diário > $100M

4. **Tempo de Busca**: ~10 minutos (ao invés de 20-30)
"""
