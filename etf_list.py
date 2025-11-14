# etf_list.py
# Lista dos 100 ETFs mais líquidos do mercado (por volume de negociação)

TOP_100_ETFS = [
    # Broad Market ETFs (S&P 500, Total Market, Nasdaq)
    "SPY", "VOO", "IVV", "VTI", "QQQ", "QQQM", "DIA", "RSP", "SPLG", "ITOT",

    # Growth & Value ETFs
    "VUG", "IWF", "VTV", "IWD", "SCHG", "SCHV", "MGK", "MGV", "VBK", "VBR",

    # International ETFs
    "VEA", "IEFA", "VWO", "IEMG", "EFA", "EEM", "VGK", "VPL", "EWJ", "EWZ",
    "EWG", "EWU", "EWC", "EWA", "FXI", "MCHI", "EWY", "EWT", "EWH", "EWW",

    # Sector ETFs - Technology
    "XLK", "VGT", "FTEC", "IGV", "SMH", "SOXX", "XSD", "HACK", "FINX", "CLOU",

    # Sector ETFs - Financial
    "XLF", "VFH", "KBE", "KRE", "IAI", "KBWB", "KBWR", "FAS", "FAZ", "IYF",

    # Sector ETFs - Healthcare
    "XLV", "VHT", "IYH", "IBB", "XBI", "IHI", "ARKG", "BBH", "IHF", "XHS",

    # Sector ETFs - Consumer
    "XLY", "VCR", "XLP", "VDC", "IYC", "IYK", "RTH", "FXD", "FDIS", "FSTA",

    # Sector ETFs - Energy
    "XLE", "VDE", "IYE", "OIH", "XOP", "IEO", "PXE", "FENY", "ERX", "ERY",

    # Sector ETFs - Industrials
    "XLI", "VIS", "IYJ", "IYT", "JETS", "ITA", "PPA", "FIDU", "XAR", "IHI",

    # Sector ETFs - Real Estate & Utilities
    "XLRE", "VNQ", "IYR", "SCHH", "RWR", "XLU", "VPU", "IDU", "FUTY", "FXU",

    # Sector ETFs - Materials & Communication
    "XLB", "VAW", "IYM", "XLC", "VOX", "IYZ", "FCOM", "XTL", "MXI", "IGE",

    # Bond ETFs
    "AGG", "BND", "LQD", "HYG", "TLT", "IEF", "SHY", "MUB", "VCIT", "VCSH",

    # Dividend ETFs
    "VIG", "SCHD", "VYM", "DVY", "SDY", "DGRO", "HDV", "NOBL", "DHS", "FVD",

    # Small & Mid Cap ETFs
    "IWM", "IJH", "VO", "VB", "IJR", "VXF", "SCHA", "SLYV", "IWN", "IWO"
]

# Descrição dos tipos de ETFs
ETF_CATEGORIES = {
    "Broad Market": ["SPY", "VOO", "IVV", "VTI", "QQQ", "QQQM", "DIA", "RSP", "SPLG", "ITOT"],
    "Growth & Value": ["VUG", "IWF", "VTV", "IWD", "SCHG", "SCHV", "MGK", "MGV", "VBK", "VBR"],
    "International": ["VEA", "IEFA", "VWO", "IEMG", "EFA", "EEM", "VGK", "VPL", "EWJ", "EWZ"],
    "Technology": ["XLK", "VGT", "FTEC", "IGV", "SMH", "SOXX", "XSD", "HACK", "FINX", "CLOU"],
    "Financial": ["XLF", "VFH", "KBE", "KRE", "IAI", "KBWB", "KBWR", "FAS", "FAZ", "IYF"],
    "Healthcare": ["XLV", "VHT", "IYH", "IBB", "XBI", "IHI", "ARKG", "BBH", "IHF", "XHS"],
    "Consumer": ["XLY", "VCR", "XLP", "VDC", "IYC", "IYK", "RTH", "FXD", "FDIS", "FSTA"],
    "Energy": ["XLE", "VDE", "IYE", "OIH", "XOP", "IEO", "PXE", "FENY", "ERX", "ERY"],
    "Industrials": ["XLI", "VIS", "IYJ", "IYT", "JETS", "ITA", "PPA", "FIDU", "XAR", "IHI"],
    "Real Estate & Utilities": ["XLRE", "VNQ", "IYR", "SCHH", "RWR", "XLU", "VPU", "IDU", "FUTY", "FXU"],
    "Materials & Communication": ["XLB", "VAW", "IYM", "XLC", "VOX", "IYZ", "FCOM", "XTL", "MXI", "IGE"],
    "Bonds": ["AGG", "BND", "LQD", "HYG", "TLT", "IEF", "SHY", "MUB", "VCIT", "VCSH"],
    "Dividend": ["VIG", "SCHD", "VYM", "DVY", "SDY", "DGRO", "HDV", "NOBL", "DHS", "FVD"],
    "Small & Mid Cap": ["IWM", "IJH", "VO", "VB", "IJR", "VXF", "SCHA", "SLYV", "IWN", "IWO"]
}
