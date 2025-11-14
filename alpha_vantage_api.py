# alpha_vantage_api.py
import requests
import time

class AlphaVantageAPI:
    """
    Classe para interagir com a API da Alpha Vantage
    Documentação: https://www.alphavantage.co/documentation/
    """

    BASE_URL = "https://www.alphavantage.co/query"

    def __init__(self, api_key):
        """
        Inicializa a API com a chave fornecida

        Args:
            api_key (str): Chave da API Alpha Vantage
        """
        self.api_key = api_key

    def _make_request(self, params):
        """
        Faz requisição para a API

        Args:
            params (dict): Parâmetros da requisição

        Returns:
            dict: Resposta da API em formato JSON
        """
        try:
            print(f"🔄 Fazendo requisição para: {params.get('function', 'N/A')}")

            response = requests.get(self.BASE_URL, params=params, timeout=30)

            # Adiciona delay para respeitar rate limit da API (5 req/min)
            time.sleep(12)

            response.raise_for_status()
            data = response.json()

            # Verifica se há mensagem de erro
            if 'Error Message' in data:
                raise Exception(data['Error Message'])

            if 'Note' in data:
                raise Exception("Rate limit atingido. Aguarde 1 minuto e tente novamente.")

            return data

        except requests.exceptions.Timeout:
            raise Exception("Timeout ao conectar com a API")
        except requests.exceptions.RequestException as e:
            raise Exception(f"Erro na requisição: {str(e)}")

    def get_etf_profile(self, symbol):
        """
        Obtém o perfil de um ETF

        Args:
            symbol (str): Símbolo do ETF (ex: SPY, QQQ)

        Returns:
            dict: Dados do ETF
        """
        params = {
            'function': 'ETF_PROFILE',
            'symbol': symbol,
            'apikey': self.api_key
        }

        return self._make_request(params)

    def get_time_series_daily(self, symbol, outputsize='compact'):
        """
        Obtém série temporal diária de preços

        Args:
            symbol (str): Símbolo da ação/ETF
            outputsize (str): 'compact' (últimos 100 dias) ou 'full' (20+ anos)

        Returns:
            dict: Dados de preços
        """
        params = {
            'function': 'TIME_SERIES_DAILY',
            'symbol': symbol,
            'outputsize': outputsize,
            'apikey': self.api_key
        }

        return self._make_request(params)

    def get_sma(self, symbol, interval='daily', time_period=20, series_type='close'):
        """
        Obtém Simple Moving Average (SMA)

        Args:
            symbol (str): Símbolo da ação/ETF
            interval (str): Intervalo de tempo ('daily', 'weekly', 'monthly')
            time_period (int): Período da média móvel
            series_type (str): Tipo de série ('close', 'open', 'high', 'low')

        Returns:
            dict: Dados do SMA
        """
        params = {
            'function': 'SMA',
            'symbol': symbol,
            'interval': interval,
            'time_period': time_period,
            'series_type': series_type,
            'apikey': self.api_key
        }

        return self._make_request(params)

    def get_rsi(self, symbol, interval='daily', time_period=14, series_type='close'):
        """
        Obtém Relative Strength Index (RSI)

        Args:
            symbol (str): Símbolo da ação/ETF
            interval (str): Intervalo de tempo ('daily', 'weekly', 'monthly')
            time_period (int): Período do RSI
            series_type (str): Tipo de série ('close', 'open', 'high', 'low')

        Returns:
            dict: Dados do RSI
        """
        params = {
            'function': 'RSI',
            'symbol': symbol,
            'interval': interval,
            'time_period': time_period,
            'series_type': series_type,
            'apikey': self.api_key
        }

        return self._make_request(params)

    def get_company_overview(self, symbol):
        """
        Obtém overview de uma empresa

        Args:
            symbol (str): Símbolo da ação

        Returns:
            dict: Dados da empresa
        """
        params = {
            'function': 'OVERVIEW',
            'symbol': symbol,
            'apikey': self.api_key
        }

        return self._make_request(params)

    def get_income_statement(self, symbol):
        """
        Obtém demonstração de resultados

        Args:
            symbol (str): Símbolo da ação

        Returns:
            dict: Dados da demonstração de resultados
        """
        params = {
            'function': 'INCOME_STATEMENT',
            'symbol': symbol,
            'apikey': self.api_key
        }

        return self._make_request(params)

    def get_balance_sheet(self, symbol):
        """
        Obtém balanço patrimonial

        Args:
            symbol (str): Símbolo da ação

        Returns:
            dict: Dados do balanço patrimonial
        """
        params = {
            'function': 'BALANCE_SHEET',
            'symbol': symbol,
            'apikey': self.api_key
        }

        return self._make_request(params)

    def get_cash_flow(self, symbol):
        """
        Obtém demonstração de fluxo de caixa

        Args:
            symbol (str): Símbolo da ação

        Returns:
            dict: Dados do fluxo de caixa
        """
        params = {
            'function': 'CASH_FLOW',
            'symbol': symbol,
            'apikey': self.api_key
        }

        return self._make_request(params)

    def get_news_sentiment(self, tickers=None, topics=None, time_from=None, time_to=None, limit=50):
        """
        Obtém notícias e análise de sentimento

        Args:
            tickers (str): Símbolos separados por vírgula (ex: "AAPL,MSFT")
            topics (str): Tópicos (ex: "technology,finance")
            time_from (str): Data início formato YYYYMMDDTHHMM
            time_to (str): Data fim formato YYYYMMDDTHHMM
            limit (int): Número de notícias (max 1000)

        Returns:
            dict: Notícias e sentimento
        """
        params = {
            'function': 'NEWS_SENTIMENT',
            'apikey': self.api_key
        }

        if tickers:
            params['tickers'] = tickers
        if topics:
            params['topics'] = topics
        if time_from:
            params['time_from'] = time_from
        if time_to:
            params['time_to'] = time_to
        if limit:
            params['limit'] = limit

        return self._make_request(params)

    def search_symbol(self, keywords):
        """
        Busca símbolos por palavras-chave

        Args:
            keywords (str): Palavras-chave para busca

        Returns:
            dict: Resultados da busca
        """
        params = {
            'function': 'SYMBOL_SEARCH',
            'keywords': keywords,
            'apikey': self.api_key
        }

        return self._make_request(params)

    def get_etf_holdings_search(self, symbol, etf_list):
        """
        Busca ETFs que contêm uma ação específica

        Args:
            symbol (str): Símbolo da ação a buscar
            etf_list (list): Lista de ETFs para buscar

        Returns:
            list: Lista de ETFs que contêm a ação
        """
        etfs_with_holding = []
        symbol_upper = symbol.upper()

        print(f"\n🔍 Iniciando busca por {symbol_upper} em {len(etf_list)} ETFs...")

        for idx, etf in enumerate(etf_list, 1):
            try:
                print(f"[{idx}/{len(etf_list)}] Buscando em {etf}...")
                data = self.get_etf_profile(etf)

                if 'holdings' in data and data['holdings']:
                    for holding in data['holdings']:
                        if holding.get('symbol', '').upper() == symbol_upper:
                            etfs_with_holding.append({
                                'etf_symbol': etf,
                                'etf_name': data.get('name', 'N/A'),
                                'net_assets': data.get('net_assets', 0),
                                'expense_ratio': data.get('net_expense_ratio', 0),
                                'dividend_yield': data.get('dividend_yield', 0),
                                'description': data.get('description', 'N/A'),
                                'holding_weight': holding.get('weight', 0),
                                'holding_shares': holding.get('shares', 0)
                            })
                            print(f"✅ Encontrado em {etf} ({len(etfs_with_holding)} ETFs até agora)")
                            break
            except Exception as e:
                print(f"⚠️ Erro ao buscar {etf}: {str(e)}")
                continue

        print(f"\n✅ Busca concluída! Encontrado em {len(etfs_with_holding)} ETFs.\n")
        return etfs_with_holding
