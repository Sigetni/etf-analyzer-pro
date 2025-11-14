# overlap_calculator.py
import pandas as pd
from alpha_vantage_api import AlphaVantageAPI

class OverlapCalculator:
    def __init__(self, api_key=None):
        self.api = AlphaVantageAPI(api_key)

    def get_etf_holdings(self, symbol):
        """Extrai holdings de um ETF via Alpha Vantage"""
        try:
            profile = self.api.get_etf_profile(symbol)

            # DEBUG: Ver o que a API retorna
            print(f"\n=== DEBUG: Resposta da API para {symbol} ===")
            print(f"Chaves disponíveis: {profile.keys() if profile else 'None'}")

            if 'holdings' in profile:
                holdings = {}
                for i, holding in enumerate(profile['holdings'][:3]):
                    print(f"\nHolding {i+1}:")
                    print(f"  Dados completos: {holding}")
                    ticker = holding.get('symbol', '')
                    weight = holding.get('weight', 0)
                    print(f"  Ticker: {ticker}")
                    print(f"  Weight (original): {weight} (tipo: {type(weight)})")

                for holding in profile['holdings']:
                    ticker = holding.get('symbol', '')
                    weight = float(holding.get('weight', 0))
                    holdings[ticker] = weight * 100

                print(f"\nTotal de holdings encontrados: {len(holdings)}")
                print(f"Primeiros 3 holdings processados: {dict(list(holdings.items())[:3])}")

                return holdings

            print("ERRO: Chave 'holdings' não encontrada na resposta")
            return None

        except Exception as e:
            print(f"ERRO ao buscar holdings: {str(e)}")
            raise Exception(f"Erro ao buscar holdings de {symbol}: {str(e)}")

    def calculate_overlap(self, etf_a, etf_b):
        """
        Calcula overlap entre dois ETFs (apenas os holdings, sem considerar peso no portfólio)

        Args:
            etf_a: Ticker do ETF A
            etf_b: Ticker do ETF B

        Returns:
            dict com métricas de overlap
        """
        print(f"\n=== CALCULANDO OVERLAP ===")
        print(f"ETF A: {etf_a}")
        print(f"ETF B: {etf_b}")

        holdings_a = self.get_etf_holdings(etf_a)
        holdings_b = self.get_etf_holdings(etf_b)

        if not holdings_a or not holdings_b:
            raise ValueError("Não foi possível obter holdings dos ETFs")

        # Encontra tickers comuns (interseção)
        common_tickers = set(holdings_a.keys()) & set(holdings_b.keys())

        overlap_weight = 0
        common_holdings = []

        print(f"\n=== CALCULANDO OVERLAP ===")
        print(f"Holdings em {etf_a}: {len(holdings_a)}")
        print(f"Holdings em {etf_b}: {len(holdings_b)}")
        print(f"Holdings comuns: {len(common_tickers)}")

        for i, ticker in enumerate(common_tickers):
            weight_a = holdings_a[ticker]
            weight_b = holdings_b[ticker]

            # Overlap = peso mínimo entre os dois ETFs
            overlap_amount = min(weight_a, weight_b)
            overlap_weight += overlap_amount

            # DEBUG: Mostra os primeiros 3 cálculos
            if i < 3:
                print(f"\nTicker: {ticker}")
                print(f"  Peso em {etf_a}: {weight_a:.2f}%")
                print(f"  Peso em {etf_b}: {weight_b:.2f}%")
                print(f"  Overlap: min({weight_a:.2f}, {weight_b:.2f}) = {overlap_amount:.2f}%")

            common_holdings.append({
                'ticker': ticker,
                'weight_in_a': weight_a,
                'weight_in_b': weight_b,
                'overlap': overlap_amount
            })

        # Ordena por overlap
        common_holdings.sort(key=lambda x: x['overlap'], reverse=True)

        # Calcula métricas
        total_weight_a = sum(holdings_a.values())
        total_weight_b = sum(holdings_b.values())

        # % do ETF A que está no ETF B
        overlap_a_in_b = (overlap_weight / total_weight_a * 100) if total_weight_a > 0 else 0

        # % do ETF B que está no ETF A
        overlap_b_in_a = (overlap_weight / total_weight_b * 100) if total_weight_b > 0 else 0

        # Overlap médio
        overlap_average = (overlap_a_in_b + overlap_b_in_a) / 2

        print(f"\n=== RESULTADO FINAL ===")
        print(f"Peso total overlap: {overlap_weight:.2f}%")
        print(f"% de {etf_a} que está em {etf_b}: {overlap_a_in_b:.2f}%")
        print(f"% de {etf_b} que está em {etf_a}: {overlap_b_in_a:.2f}%")
        print(f"Overlap médio: {overlap_average:.2f}%")

        return {
            'overlap_weight': overlap_weight,
            'overlap_a_in_b': overlap_a_in_b,
            'overlap_b_in_a': overlap_b_in_a,
            'overlap_average': overlap_average,
            'common_holdings': common_holdings,
            'total_holdings_a': len(holdings_a),
            'total_holdings_b': len(holdings_b),
            'common_count': len(common_tickers)
        }
