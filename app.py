# app.py
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
from etf_list import TOP_100_ETFS, ETF_CATEGORIES
from config import APP_TITLE, APP_ICON, ALPHA_VANTAGE_API_KEY
from alpha_vantage_api import AlphaVantageAPI
from overlap_calculator import OverlapCalculator

st.set_page_config(
    page_title=APP_TITLE,
    page_icon=APP_ICON,
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inicializa API
@st.cache_resource
def get_api():
    return AlphaVantageAPI(ALPHA_VANTAGE_API_KEY)

api = get_api()

# ==================== SIDEBAR NAVIGATION ====================
st.sidebar.title(f"{APP_ICON} {APP_TITLE}")
st.sidebar.markdown("---")

page = st.sidebar.radio(
    "Navegação",
    [
        "🏠 Home",
        "🔍 ETF Profile",
        "📊 ETF Overlap Analysis",
        "💹 Price Analysis",
        "📈 Technical Indicators",
        "💰 Fundamentals",
        "📰 News",
        "🔎 Symbol Search"
    ]
)

st.sidebar.markdown("---")
st.sidebar.caption("📊 ETF Analyzer Pro v1.0")
st.sidebar.caption("Built with Streamlit")

# ==================== HOME PAGE ====================
if page == "🏠 Home":
    st.title(f"{APP_ICON} {APP_TITLE}")

    st.markdown("""
    ## 👋 Welcome to ETF Analyzer Pro!

    A comprehensive tool for analyzing ETFs, stocks, and market trends.

    ### 🚀 Features:

    - **🔍 ETF Profile**: View detailed information about any ETF
    - **📊 ETF Overlap Analysis**: Compare holdings between two ETFs
    - **💹 Price Analysis**: Analyze historical price data with interactive charts
    - **📈 Technical Indicators**: View SMA, RSI, and other technical indicators
    - **💰 Fundamentals**: Deep dive into company financials (Income, Balance Sheet, Cash Flow)
    - **📰 Market News**: Real-time news with sentiment analysis
    - **🔎 Symbol Search**: Find stock/ETF symbols by keywords

    ### 📌 How to Use:

    1. Select a tool from the **sidebar** (left menu)
    2. Enter the stock/ETF symbol
    3. Explore the data and insights!

    ### 💡 Tips:

    - Most features work with both **ETFs** and **individual stocks**
    - Use the **Custom Chart** in Fundamentals to compare different metrics
    - Check **News Sentiment** to gauge market mood
    - **Overlap Analysis** helps avoid redundancy in your portfolio

    ---

    **Powered by Alpha Vantage API**
    """)

# ==================== ETF PROFILE ====================
elif page == "🔍 ETF Profile":
    st.title("🔍 ETF Profile")

    # Inicializa session state
    if 'etf_profile_data' not in st.session_state:
        st.session_state.etf_profile_data = None

    col1, col2 = st.columns([3, 1])
    with col1:
        symbol = st.text_input("Enter ETF Symbol", value="SPY", key="etf_profile_symbol")
    with col2:
        st.write("")
        st.write("")
        if st.button("🔍 Search", key="etf_profile_search"):
            try:
                with st.spinner(f"Loading data for {symbol}..."):
                    st.session_state.etf_profile_data = api.get_etf_profile(symbol)
                    st.session_state.etf_profile_symbol_searched = symbol
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
                st.session_state.etf_profile_data = None

    # Função auxiliar para converter valores
    def safe_float(value, default=0):
        try:
            if value is None or value == '' or value == 'None':
                return default
            return float(value)
        except (ValueError, TypeError):
            return default

    # Exibe dados se existirem
    if st.session_state.etf_profile_data and 'net_assets' in st.session_state.etf_profile_data:
        data = st.session_state.etf_profile_data

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            net_assets = safe_float(data.get('net_assets', 0))
            st.metric("Net Assets", f"${net_assets/1e9:.2f}B" if net_assets > 0 else "N/A")
        with col2:
            expense_ratio = safe_float(data.get('net_expense_ratio', 0))
            st.metric("Expense Ratio", f"{expense_ratio*100:.2f}%" if expense_ratio > 0 else "N/A")
        with col3:
            dividend_yield = safe_float(data.get('dividend_yield', 0))
            st.metric("Dividend Yield", f"{dividend_yield*100:.2f}%" if dividend_yield > 0 else "N/A")
        with col4:
            st.metric("Inception Date", data.get('inception_date', 'N/A'))

        # Sectors
        if 'sectors' in data and data['sectors']:
            st.subheader("📊 Sector Allocation")
            sectors_df = pd.DataFrame(data['sectors'])

            fig = go.Figure(data=[go.Pie(
                labels=sectors_df['sector'],
                values=sectors_df['weight'],
                hole=0.3
            )])
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)

        # Top Holdings
        if 'holdings' in data and data['holdings']:
            st.subheader("🏢 Top 10 Holdings")
            holdings_df = pd.DataFrame(data['holdings'][:10])
            holdings_df['weight'] = holdings_df['weight'].apply(lambda x: safe_float(x) * 100)

            fig = go.Figure(data=[go.Bar(
                x=holdings_df['weight'],
                y=holdings_df['symbol'],
                orientation='h',
                text=holdings_df['weight'].round(2),
                textposition='auto',
            )])
            fig.update_layout(
                xaxis_title="Weight (%)",
                yaxis_title="Symbol",
                height=400,
                yaxis={'categoryorder':'total ascending'}
            )
            st.plotly_chart(fig, use_container_width=True)

            st.dataframe(holdings_df[['symbol', 'description', 'weight']], use_container_width=True)
    elif st.session_state.etf_profile_data is not None:
        st.error(f"❌ No data found for the symbol")

# ==================== ETF OVERLAP ANALYSIS ====================
elif page == "📊 ETF Overlap Analysis":
    st.title("📊 ETF Overlap Analysis")

    st.markdown("""
    Compare two ETFs to see how much their holdings overlap.
    This helps you avoid redundancy in your portfolio.
    """)

    # Inicializa session state
    if 'overlap_result' not in st.session_state:
        st.session_state.overlap_result = None
    if 'overlap_etf_a_value' not in st.session_state:
        st.session_state.overlap_etf_a_value = None
    if 'overlap_etf_b_value' not in st.session_state:
        st.session_state.overlap_etf_b_value = None

    col1, col2, col3 = st.columns([2, 2, 1])

    with col1:
        etf_a = st.text_input("First ETF", value="SPY", key="overlap_etf_a")

    with col2:
        etf_b = st.text_input("Second ETF", value="VOO", key="overlap_etf_b")

    with col3:
        st.write("")
        st.write("")
        if st.button("📊 Compare", key="overlap_compare"):
            if etf_a and etf_b:
                try:
                    with st.spinner(f"Analyzing overlap between {etf_a} and {etf_b}..."):
                        calculator = OverlapCalculator(ALPHA_VANTAGE_API_KEY)
                        st.session_state.overlap_result = calculator.calculate_overlap(etf_a, etf_b)
                        st.session_state.overlap_etf_a_value = etf_a
                        st.session_state.overlap_etf_b_value = etf_b
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
                    st.session_state.overlap_result = None
            else:
                st.warning("⚠️ Please enter both ETF symbols")

    # Exibe resultado se existir
    if st.session_state.overlap_result:
        result = st.session_state.overlap_result
        etf_a_display = st.session_state.overlap_etf_a_value
        etf_b_display = st.session_state.overlap_etf_b_value

        # Métricas principais
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Overlap Weight", f"{result['overlap_weight']:.2f}%")
        with col2:
            st.metric(f"{etf_a_display} in {etf_b_display}", f"{result['overlap_a_in_b']:.2f}%")
        with col3:
            st.metric(f"{etf_b_display} in {etf_a_display}", f"{result['overlap_b_in_a']:.2f}%")
        with col4:
            st.metric("Average Overlap", f"{result['overlap_average']:.2f}%")

        # Gráfico de overlap
        st.subheader("📊 Overlap Visualization")

        fig = go.Figure()

        fig.add_trace(go.Bar(
            name=etf_a_display,
            x=[etf_a_display],
            y=[100],
            marker_color='lightblue'
        ))

        fig.add_trace(go.Bar(
            name=etf_b_display,
            x=[etf_b_display],
            y=[100],
            marker_color='lightgreen'
        ))

        fig.add_trace(go.Bar(
            name='Overlap',
            x=['Overlap'],
            y=[result['overlap_average']],
            marker_color='orange'
        ))

        fig.update_layout(
            title='ETF Composition Overlap',
            yaxis_title='Percentage (%)',
            height=400
        )

        st.plotly_chart(fig, use_container_width=True)

        # Top common holdings
        st.subheader("🏢 Top Common Holdings")

        common_df = pd.DataFrame(result['common_holdings'][:20])
        common_df = common_df.round(2)

        st.dataframe(common_df, use_container_width=True)

        # Summary
        st.info(f"""
        **Summary:**
        - Total holdings in {etf_a_display}: {result['total_holdings_a']}
        - Total holdings in {etf_b_display}: {result['total_holdings_b']}
        - Common holdings: {result['common_count']}
        - Average overlap: {result['overlap_average']:.2f}%
        """)

# ==================== PRICE ANALYSIS ====================
elif page == "💹 Price Analysis":
    st.title("💹 Price Analysis")

    # Inicializa session state
    if 'price_data' not in st.session_state:
        st.session_state.price_data = None

    col1, col2, col3 = st.columns([2, 1, 1])

    with col1:
        symbol = st.text_input("Enter Symbol", value="AAPL", key="price_symbol")

    with col2:
        outputsize = st.selectbox("Data Range", ["compact", "full"], key="price_range")

    with col3:
        st.write("")
        st.write("")
        if st.button("📈 Analyze", key="price_analyze"):
            try:
                with st.spinner(f"Loading price data for {symbol}..."):
                    st.session_state.price_data = api.get_time_series_daily(symbol, outputsize)
                    st.session_state.price_symbol = symbol
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
                st.session_state.price_data = None

    # Exibe dados se existirem
    if st.session_state.price_data and 'Time Series (Daily)' in st.session_state.price_data:
        data = st.session_state.price_data
        symbol = st.session_state.price_symbol

        df = pd.DataFrame.from_dict(data['Time Series (Daily)'], orient='index')
        df.index = pd.to_datetime(df.index)
        df = df.sort_index()

        # Converte para numérico
        for col in df.columns:
            df[col] = pd.to_numeric(df[col])

        df.columns = ['Open', 'High', 'Low', 'Close', 'Volume']

        # Métricas
        current_price = df['Close'].iloc[-1]
        prev_price = df['Close'].iloc[-2]
        change = current_price - prev_price
        change_pct = (change / prev_price) * 100

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Current Price", f"${current_price:.2f}", f"{change:.2f} ({change_pct:.2f}%)")
        with col2:
            st.metric("High (52w)", f"${df['High'].tail(252).max():.2f}")
        with col3:
            st.metric("Low (52w)", f"${df['Low'].tail(252).min():.2f}")
        with col4:
            st.metric("Avg Volume", f"{df['Volume'].tail(20).mean()/1e6:.2f}M")

        # Gráfico de candlestick
        st.subheader("📊 Price Chart")

        fig = go.Figure(data=[go.Candlestick(
            x=df.index,
            open=df['Open'],
            high=df['High'],
            low=df['Low'],
            close=df['Close']
        )])

        fig.update_layout(
            title=f'{symbol} Price Chart',
            yaxis_title='Price (USD)',
            xaxis_title='Date',
            height=500
        )

        st.plotly_chart(fig, use_container_width=True)

        # Volume
        st.subheader("📊 Volume")

        fig_vol = go.Figure(data=[go.Bar(
            x=df.index,
            y=df['Volume'],
            marker_color='lightblue'
        )])

        fig_vol.update_layout(
            title='Trading Volume',
            yaxis_title='Volume',
            xaxis_title='Date',
            height=300
        )

        st.plotly_chart(fig_vol, use_container_width=True)
    elif st.session_state.price_data is not None:
        st.error(f"❌ No data found")

# ==================== TECHNICAL INDICATORS ====================
elif page == "📈 Technical Indicators":
    st.title("📈 Technical Indicators")

    # Inicializa session state
    if 'tech_sma_data' not in st.session_state:
        st.session_state.tech_sma_data = None
    if 'tech_rsi_data' not in st.session_state:
        st.session_state.tech_rsi_data = None

    col1, col2 = st.columns([3, 1])

    with col1:
        symbol = st.text_input("Enter Symbol", value="AAPL", key="tech_symbol")

    with col2:
        st.write("")
        st.write("")
        analyze_button = st.button("📊 Analyze", key="tech_analyze")

    if analyze_button:
        st.session_state.tech_symbol = symbol

    if 'tech_symbol' in st.session_state:
        symbol = st.session_state.tech_symbol

        tab1, tab2 = st.tabs(["📈 SMA", "📊 RSI"])

        # SMA Tab
        with tab1:
            st.subheader("Simple Moving Average (SMA)")

            col1, col2, col3 = st.columns([2, 2, 1])
            with col1:
                sma_period = st.slider("SMA Period", 5, 200, 20, key="sma_period")
            with col2:
                sma_interval = st.selectbox("Interval", ["daily", "weekly", "monthly"], key="sma_interval")
            with col3:
                st.write("")
                st.write("")
                if st.button("Load SMA", key="load_sma"):
                    try:
                        with st.spinner("Loading SMA data..."):
                            st.session_state.tech_sma_data = api.get_sma(symbol, interval=sma_interval, time_period=sma_period)
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")
                        st.session_state.tech_sma_data = None

            if st.session_state.tech_sma_data and 'Technical Analysis: SMA' in st.session_state.tech_sma_data:
                sma_data = st.session_state.tech_sma_data
                df_sma = pd.DataFrame.from_dict(sma_data['Technical Analysis: SMA'], orient='index')
                df_sma.index = pd.to_datetime(df_sma.index)
                df_sma = df_sma.sort_index()
                df_sma['SMA'] = pd.to_numeric(df_sma['SMA'])

                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=df_sma.index,
                    y=df_sma['SMA'],
                    mode='lines',
                    name=f'SMA {sma_period}',
                    line=dict(color='blue', width=2)
                ))

                fig.update_layout(
                    title=f'{symbol} - SMA {sma_period}',
                    xaxis_title='Date',
                    yaxis_title='SMA Value',
                    height=500
                )

                st.plotly_chart(fig, use_container_width=True)

                st.dataframe(df_sma.tail(20), use_container_width=True)
            elif st.session_state.tech_sma_data is not None:
                st.error("❌ No SMA data available")

        # RSI Tab
        with tab2:
            st.subheader("Relative Strength Index (RSI)")

            col1, col2, col3 = st.columns([2, 2, 1])
            with col1:
                rsi_period = st.slider("RSI Period", 5, 50, 14, key="rsi_period")
            with col2:
                rsi_interval = st.selectbox("Interval", ["daily", "weekly", "monthly"], key="rsi_interval")
            with col3:
                st.write("")
                st.write("")
                if st.button("Load RSI", key="load_rsi"):
                    try:
                        with st.spinner("Loading RSI data..."):
                            st.session_state.tech_rsi_data = api.get_rsi(symbol, interval=rsi_interval, time_period=rsi_period)
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")
                        st.session_state.tech_rsi_data = None

            if st.session_state.tech_rsi_data and 'Technical Analysis: RSI' in st.session_state.tech_rsi_data:
                rsi_data = st.session_state.tech_rsi_data
                df_rsi = pd.DataFrame.from_dict(rsi_data['Technical Analysis: RSI'], orient='index')
                df_rsi.index = pd.to_datetime(df_rsi.index)
                df_rsi = df_rsi.sort_index()
                df_rsi['RSI'] = pd.to_numeric(df_rsi['RSI'])

                fig = go.Figure()

                fig.add_trace(go.Scatter(
                    x=df_rsi.index,
                    y=df_rsi['RSI'],
                    mode='lines',
                    name='RSI',
                    line=dict(color='purple', width=2)
                ))

                # Linhas de referência
                fig.add_hline(y=70, line_dash="dash", line_color="red", annotation_text="Overbought (70)")
                fig.add_hline(y=30, line_dash="dash", line_color="green", annotation_text="Oversold (30)")

                fig.update_layout(
                    title=f'{symbol} - RSI {rsi_period}',
                    xaxis_title='Date',
                    yaxis_title='RSI Value',
                    height=500,
                    yaxis=dict(range=[0, 100])
                )

                st.plotly_chart(fig, use_container_width=True)

                # Interpretação
                current_rsi = df_rsi['RSI'].iloc[-1]

                if current_rsi > 70:
                    st.warning(f"⚠️ RSI is {current_rsi:.2f} - **Overbought** territory")
                elif current_rsi < 30:
                    st.success(f"✅ RSI is {current_rsi:.2f} - **Oversold** territory")
                else:
                    st.info(f"ℹ️ RSI is {current_rsi:.2f} - **Neutral** territory")

                st.dataframe(df_rsi.tail(20), use_container_width=True)
            elif st.session_state.tech_rsi_data is not None:
                st.error("❌ No RSI data available")

# ==================== FUNDAMENTALS ====================
elif page == "💰 Fundamentals":
    st.title("💰 Company Fundamentals")

    # Inicializa session state
    if 'fund_data' not in st.session_state:
        st.session_state.fund_data = None

    col1, col2 = st.columns([3, 1])
    with col1:
        symbol = st.text_input("Enter Stock Symbol", value="AAPL", key="fund_symbol")
    with col2:
        st.write("")
        st.write("")
        if st.button("🔍 Search", key="fund_search"):
            try:
                with st.spinner(f"Loading data for {symbol}..."):
                    overview = api.get_company_overview(symbol)
                    income = api.get_income_statement(symbol)
                    balance = api.get_balance_sheet(symbol)
                    cashflow = api.get_cash_flow(symbol)

                    st.session_state.fund_data = {
                        'overview': overview,
                        'income': income,
                        'balance': balance,
                        'cashflow': cashflow,
                        'symbol': symbol
                    }
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
                st.session_state.fund_data = None

    if st.session_state.fund_data:
        overview = st.session_state.fund_data['overview']
        income = st.session_state.fund_data['income']
        balance = st.session_state.fund_data['balance']
        cashflow = st.session_state.fund_data['cashflow']
        symbol = st.session_state.fund_data['symbol']

        if not overview or 'Symbol' not in overview:
            st.error(f"❌ No data found for {symbol}")
        else:
            # Company Overview
            st.header(f"{overview.get('Name', symbol)}")

            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric("Market Cap", f"${float(overview.get('MarketCapitalization', 0))/1e9:.2f}B")
            with col2:
                st.metric("P/E Ratio", overview.get('PERatio', 'N/A'))
            with col3:
                st.metric("EPS", overview.get('EPS', 'N/A'))
            with col4:
                st.metric("Dividend Yield", f"{float(overview.get('DividendYield', 0))*100:.2f}%")

            # Tabs para diferentes relatórios
            tab1, tab2, tab3, tab4, tab5 = st.tabs([
                "📊 Overview", 
                "💵 Income Statement", 
                "📋 Balance Sheet",
                "💰 Cash Flow",
                "📈 Custom Chart"
            ])

            # TAB 1: Overview
            with tab1:
                col1, col2 = st.columns(2)

                with col1:
                    st.subheader("Company Information")
                    info_data = {
                        "Sector": overview.get('Sector', 'N/A'),
                        "Industry": overview.get('Industry', 'N/A'),
                        "Exchange": overview.get('Exchange', 'N/A'),
                        "Currency": overview.get('Currency', 'N/A'),
                        "Country": overview.get('Country', 'N/A'),
                    }
                    st.dataframe(pd.DataFrame(info_data.items(), columns=['Field', 'Value']), hide_index=True, use_container_width=True)

                with col2:
                    st.subheader("Key Metrics")
                    metrics_data = {
                        "52 Week High": f"${overview.get('52WeekHigh', 'N/A')}",
                        "52 Week Low": f"${overview.get('52WeekLow', 'N/A')}",
                        "50 Day MA": f"${overview.get('50DayMovingAverage', 'N/A')}",
                        "200 Day MA": f"${overview.get('200DayMovingAverage', 'N/A')}",
                        "Beta": overview.get('Beta', 'N/A'),
                    }
                    st.dataframe(pd.DataFrame(metrics_data.items(), columns=['Metric', 'Value']), hide_index=True, use_container_width=True)

                st.subheader("Description")
                st.write(overview.get('Description', 'No description available'))

            # TAB 2: Income Statement
            with tab2:
                if 'annualReports' in income and income['annualReports']:
                    df_income = pd.DataFrame(income['annualReports'])
                    df_income['fiscalDateEnding'] = pd.to_datetime(df_income['fiscalDateEnding'])
                    df_income = df_income.sort_values('fiscalDateEnding')

                    # Converte colunas numéricas
                    numeric_cols = ['totalRevenue', 'grossProfit', 'netIncome', 'operatingIncome', 'ebitda']
                    for col in numeric_cols:
                        if col in df_income.columns:
                            df_income[col] = pd.to_numeric(df_income[col], errors='coerce') / 1e9

                    # Gráfico
                    fig = go.Figure()

                    fig.add_trace(go.Bar(
                        x=df_income['fiscalDateEnding'],
                        y=df_income['totalRevenue'],
                        name='Total Revenue',
                        marker_color='lightblue'
                    ))

                    fig.add_trace(go.Bar(
                        x=df_income['fiscalDateEnding'],
                        y=df_income['netIncome'],
                        name='Net Income',
                        marker_color='green'
                    ))

                    fig.update_layout(
                        title='Revenue vs Net Income (Billions)',
                        xaxis_title='Fiscal Year',
                        yaxis_title='Amount (Billions USD)',
                        barmode='group',
                        height=400
                    )

                    st.plotly_chart(fig, use_container_width=True)

                    # Tabela
                    st.subheader("Annual Reports")
                    display_cols = ['fiscalDateEnding', 'totalRevenue', 'grossProfit', 'operatingIncome', 'netIncome', 'ebitda']
                    display_df = df_income[display_cols].copy()
                    display_df.columns = ['Date', 'Revenue (B)', 'Gross Profit (B)', 'Operating Income (B)', 'Net Income (B)', 'EBITDA (B)']
                    st.dataframe(display_df, hide_index=True, use_container_width=True)
                else:
                    st.warning("No income statement data available")

            # TAB 3: Balance Sheet
            with tab3:
                if 'annualReports' in balance and balance['annualReports']:
                    df_balance = pd.DataFrame(balance['annualReports'])
                    df_balance['fiscalDateEnding'] = pd.to_datetime(df_balance['fiscalDateEnding'])
                    df_balance = df_balance.sort_values('fiscalDateEnding')

                    # Converte colunas numéricas
                    numeric_cols = ['totalAssets', 'totalLiabilities', 'totalShareholderEquity']
                    for col in numeric_cols:
                        if col in df_balance.columns:
                            df_balance[col] = pd.to_numeric(df_balance[col], errors='coerce') / 1e9

                    # Gráfico
                    fig = go.Figure()

                    fig.add_trace(go.Bar(
                        x=df_balance['fiscalDateEnding'],
                        y=df_balance['totalAssets'],
                        name='Total Assets',
                        marker_color='blue'
                    ))

                    fig.add_trace(go.Bar(
                        x=df_balance['fiscalDateEnding'],
                        y=df_balance['totalLiabilities'],
                        name='Total Liabilities',
                        marker_color='red'
                    ))

                    fig.add_trace(go.Bar(
                        x=df_balance['fiscalDateEnding'],
                        y=df_balance['totalShareholderEquity'],
                        name='Shareholder Equity',
                        marker_color='green'
                    ))

                    fig.update_layout(
                        title='Assets, Liabilities &amp; Equity (Billions)',
                        xaxis_title='Fiscal Year',
                        yaxis_title='Amount (Billions USD)',
                        barmode='group',
                        height=400
                    )

                    st.plotly_chart(fig, use_container_width=True)

                    # Tabela
                    st.subheader("Annual Reports")
                    display_cols = ['fiscalDateEnding', 'totalAssets', 'totalLiabilities', 'totalShareholderEquity']
                    display_df = df_balance[display_cols].copy()
                    display_df.columns = ['Date', 'Total Assets (B)', 'Total Liabilities (B)', 'Shareholder Equity (B)']
                    st.dataframe(display_df, hide_index=True, use_container_width=True)
                else:
                    st.warning("No balance sheet data available")

            # TAB 4: Cash Flow
            with tab4:
                if 'annualReports' in cashflow and cashflow['annualReports']:
                    df_cashflow = pd.DataFrame(cashflow['annualReports'])
                    df_cashflow['fiscalDateEnding'] = pd.to_datetime(df_cashflow['fiscalDateEnding'])
                    df_cashflow = df_cashflow.sort_values('fiscalDateEnding')

                    # Converte colunas numéricas
                    numeric_cols = ['operatingCashflow', 'cashflowFromInvestment', 'cashflowFromFinancing']
                    for col in numeric_cols:
                        if col in df_cashflow.columns:
                            df_cashflow[col] = pd.to_numeric(df_cashflow[col], errors='coerce') / 1e9

                    # Gráfico
                    fig = go.Figure()

                    fig.add_trace(go.Bar(
                        x=df_cashflow['fiscalDateEnding'],
                        y=df_cashflow['operatingCashflow'],
                        name='Operating Cash Flow',
                        marker_color='green'
                    ))

                    fig.add_trace(go.Bar(
                        x=df_cashflow['fiscalDateEnding'],
                        y=df_cashflow['cashflowFromInvestment'],
                        name='Investing Cash Flow',
                        marker_color='blue'
                    ))

                    fig.add_trace(go.Bar(
                        x=df_cashflow['fiscalDateEnding'],
                        y=df_cashflow['cashflowFromFinancing'],
                        name='Financing Cash Flow',
                        marker_color='orange'
                    ))

                    fig.update_layout(
                        title='Cash Flow Statement (Billions)',
                        xaxis_title='Fiscal Year',
                        yaxis_title='Amount (Billions USD)',
                        barmode='group',
                        height=400
                    )

                    st.plotly_chart(fig, use_container_width=True)

                    # Tabela
                    st.subheader("Annual Reports")
                    display_cols = ['fiscalDateEnding', 'operatingCashflow', 'cashflowFromInvestment', 'cashflowFromFinancing']
                    display_df = df_cashflow[display_cols].copy()
                    display_df.columns = ['Date', 'Operating CF (B)', 'Investing CF (B)', 'Financing CF (B)']
                    st.dataframe(display_df, hide_index=True, use_container_width=True)
                else:
                    st.warning("No cash flow data available")

            # TAB 5: Custom Chart
            with tab5:
                st.subheader("📈 Create Your Custom Chart")
                st.write("Select metrics from different reports to compare over time")

                # Prepara dados disponíveis
                available_data = {}

                if 'annualReports' in income and income['annualReports']:
                    df_income_custom = pd.DataFrame(income['annualReports'])
                    df_income_custom['fiscalDateEnding'] = pd.to_datetime(df_income_custom['fiscalDateEnding'])
                    available_data['Income Statement'] = df_income_custom

                if 'annualReports' in balance and balance['annualReports']:
                    df_balance_custom = pd.DataFrame(balance['annualReports'])
                    df_balance_custom['fiscalDateEnding'] = pd.to_datetime(df_balance_custom['fiscalDateEnding'])
                    available_data['Balance Sheet'] = df_balance_custom

                if 'annualReports' in cashflow and cashflow['annualReports']:
                    df_cashflow_custom = pd.DataFrame(cashflow['annualReports'])
                    df_cashflow_custom['fiscalDateEnding'] = pd.to_datetime(df_cashflow_custom['fiscalDateEnding'])
                    available_data['Cash Flow'] = df_cashflow_custom

                if available_data:
                    # Seleção de métricas
                    col1, col2 = st.columns(2)

                    with col1:
                        # Métricas do Income Statement
                        income_metrics = {
                            'Total Revenue': 'totalRevenue',
                            'Gross Profit': 'grossProfit',
                            'Operating Income': 'operatingIncome',
                            'Net Income': 'netIncome',
                            'EBITDA': 'ebitda',
                            'Operating Expenses': 'operatingExpenses'
                        }

                        selected_income = st.multiselect(
                            "Income Statement Metrics",
                            options=list(income_metrics.keys()),
                            default=['Total Revenue', 'Net Income'],
                            key="custom_income"
                        )

                    with col2:
                        # Métricas do Balance Sheet
                        balance_metrics = {
                            'Total Assets': 'totalAssets',
                            'Total Liabilities': 'totalLiabilities',
                            'Shareholder Equity': 'totalShareholderEquity',
                            'Current Assets': 'totalCurrentAssets',
                            'Current Liabilities': 'totalCurrentLiabilities'
                        }

                        selected_balance = st.multiselect(
                            "Balance Sheet Metrics",
                            options=list(balance_metrics.keys()),
                            default=[],
                            key="custom_balance"
                        )

                    # Métricas do Cash Flow
                    cashflow_metrics = {
                        'Operating Cash Flow': 'operatingCashflow',
                        'Investing Cash Flow': 'cashflowFromInvestment',
                        'Financing Cash Flow': 'cashflowFromFinancing'
                    }

                    selected_cashflow = st.multiselect(
                        "Cash Flow Metrics",
                        options=list(cashflow_metrics.keys()),
                        default=[],
                        key="custom_cashflow"
                    )

                    # Criar gráfico customizado
                    if selected_income or selected_balance or selected_cashflow:
                        fig = go.Figure()

                        # Adiciona métricas do Income Statement
                        if 'Income Statement' in available_data:
                            df = available_data['Income Statement'].copy()
                            df = df.sort_values('fiscalDateEnding')

                            for metric_name in selected_income:
                                metric_col = income_metrics[metric_name]
                                if metric_col in df.columns:
                                    values = pd.to_numeric(df[metric_col], errors='coerce') / 1e9
                                    fig.add_trace(go.Scatter(
                                        x=df['fiscalDateEnding'],
                                        y=values,
                                        name=metric_name,
                                        mode='lines+markers'
                                    ))

                        # Adiciona métricas do Balance Sheet
                        if 'Balance Sheet' in available_data:
                            df = available_data['Balance Sheet'].copy()
                            df = df.sort_values('fiscalDateEnding')

                            for metric_name in selected_balance:
                                metric_col = balance_metrics[metric_name]
                                if metric_col in df.columns:
                                    values = pd.to_numeric(df[metric_col], errors='coerce') / 1e9
                                    fig.add_trace(go.Scatter(
                                        x=df['fiscalDateEnding'],
                                        y=values,
                                        name=metric_name,
                                        mode='lines+markers'
                                    ))

                        # Adiciona métricas do Cash Flow
                        if 'Cash Flow' in available_data:
                            df = available_data['Cash Flow'].copy()
                            df = df.sort_values('fiscalDateEnding')

                            for metric_name in selected_cashflow:
                                metric_col = cashflow_metrics[metric_name]
                                if metric_col in df.columns:
                                    values = pd.to_numeric(df[metric_col], errors='coerce') / 1e9
                                    fig.add_trace(go.Scatter(
                                        x=df['fiscalDateEnding'],
                                        y=values,
                                        name=metric_name,
                                        mode='lines+markers'
                                    ))

                        fig.update_layout(
                            title='Custom Financial Metrics Comparison',
                            xaxis_title='Fiscal Year',
                            yaxis_title='Amount (Billions USD)',
                            height=500,
                            hovermode='x unified'
                        )

                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.info("👆 Select at least one metric to create a chart")
                else:
                    st.warning("No financial data available for custom charts")

# ==================== NEWS ====================
elif page == "📰 News":
    st.title("📰 Market News &amp; Sentiment Analysis")

    # Inicializa session state
    if 'news_data' not in st.session_state:
        st.session_state.news_data = None

    # Função para converter sentimento em emoji
    def sentiment_to_emoji(score):
        if score is None:
            return "😐"
        score = float(score)
        if score >= 0.35:
            return "😊"
        elif score >= 0.15:
            return "🙂"
        elif score >= -0.15:
            return "😐"
        elif score >= -0.35:
            return "😟"
        else:
            return "😢"

    def sentiment_to_color(score):
        if score is None:
            return "gray"
        score = float(score)
        if score >= 0.15:
            return "green"
        elif score >= -0.15:
            return "orange"
        else:
            return "red"

    # Filtros
    with st.expander("🔍 Filters", expanded=True):
        col1, col2, col3 = st.columns(3)

        with col1:
            tickers_input = st.text_input(
                "Stock Symbols (comma separated)",
                value="AAPL,MSFT,GOOGL",
                help="Enter stock symbols separated by commas",
                key="news_tickers"
            )

        with col2:
            topics_options = [
                "blockchain",
                "earnings",
                "ipo",
                "mergers_and_acquisitions",
                "financial_markets",
                "economy_fiscal",
                "economy_monetary",
                "economy_macro",
                "energy_transportation",
                "finance",
                "life_sciences",
                "manufacturing",
                "real_estate",
                "retail_wholesale",
                "technology"
            ]

            selected_topics = st.multiselect(
                "Topics",
                options=topics_options,
                default=["technology", "financial_markets"],
                key="news_topics"
            )

        with col3:
            news_limit = st.slider(
                "Number of News",
                min_value=10,
                max_value=200,
                value=50,
                step=10,
                key="news_limit"
            )

        if st.button("🔍 Search News", use_container_width=True, key="news_search"):
            try:
                with st.spinner("Loading news..."):
                    # Prepara parâmetros
                    tickers = tickers_input if tickers_input else None
                    topics = ",".join(selected_topics) if selected_topics else None

                    # Busca notícias
                    st.session_state.news_data = api.get_news_sentiment(
                        tickers=tickers,
                        topics=topics,
                        limit=news_limit
                    )
            except Exception as e:
                st.error(f"❌ Error loading news: {str(e)}")
                st.session_state.news_data = None

    # Exibe notícias se existirem
    if st.session_state.news_data and 'feed' in st.session_state.news_data and st.session_state.news_data['feed']:
        news_data = st.session_state.news_data

        st.success(f"✅ Found {len(news_data['feed'])} news articles")

        # Estatísticas gerais
        col1, col2, col3, col4 = st.columns(4)

        sentiments = [float(item.get('overall_sentiment_score', 0)) for item in news_data['feed'] if item.get('overall_sentiment_score')]

        if sentiments:
            avg_sentiment = sum(sentiments) / len(sentiments)
            positive_count = sum(1 for s in sentiments if s > 0.15)
            neutral_count = sum(1 for s in sentiments if -0.15 <= s <= 0.15)
            negative_count = sum(1 for s in sentiments if s < -0.15)

            with col1:
                st.metric("Average Sentiment", f"{avg_sentiment:.3f}", 
                         delta=sentiment_to_emoji(avg_sentiment))
            with col2:
                st.metric("Positive News", positive_count, 
                         delta="😊")
            with col3:
                st.metric("Neutral News", neutral_count,
                         delta="😐")
            with col4:
                st.metric("Negative News", negative_count,
                         delta="😢")

        st.divider()

        # Filtros adicionais
        col1, col2 = st.columns([2, 1])
        with col1:
            sentiment_filter = st.selectbox(
                "Filter by Sentiment",
                options=["All", "Positive", "Neutral", "Negative"],
                key="news_sentiment_filter"
            )
        with col2:
            sort_by = st.selectbox(
                "Sort by",
                options=["Most Recent", "Most Relevant", "Sentiment (High to Low)", "Sentiment (Low to High)"],
                key="news_sort"
            )

        # Filtra notícias
        filtered_news = news_data['feed'].copy()

        if sentiment_filter != "All":
            if sentiment_filter == "Positive":
                filtered_news = [n for n in filtered_news if float(n.get('overall_sentiment_score', 0)) > 0.15]
            elif sentiment_filter == "Neutral":
                filtered_news = [n for n in filtered_news if -0.15 <= float(n.get('overall_sentiment_score', 0)) <= 0.15]
            elif sentiment_filter == "Negative":
                filtered_news = [n for n in filtered_news if float(n.get('overall_sentiment_score', 0)) < -0.15]

        # Ordena notícias
        if sort_by == "Most Recent":
            filtered_news.sort(key=lambda x: x.get('time_published', ''), reverse=True)
        elif sort_by == "Most Relevant":
            filtered_news.sort(key=lambda x: float(x.get('relevance_score', 0)), reverse=True)
        elif sort_by == "Sentiment (High to Low)":
            filtered_news.sort(key=lambda x: float(x.get('overall_sentiment_score', 0)), reverse=True)
        elif sort_by == "Sentiment (Low to High)":
            filtered_news.sort(key=lambda x: float(x.get('overall_sentiment_score', 0)))

        st.write(f"Showing {len(filtered_news)} articles")

        # Exibe notícias
        for idx, article in enumerate(filtered_news):
            sentiment_score = float(article.get('overall_sentiment_score', 0))
            sentiment_label = article.get('overall_sentiment_label', 'Neutral')

            with st.container():
                col1, col2 = st.columns([4, 1])

                with col1:
                    st.subheader(f"{idx+1}. {article.get('title', 'No title')}")

                    # Metadata
                    time_published = article.get('time_published', '')
                    if time_published:
                        try:
                            dt = datetime.strptime(time_published, '%Y%m%dT%H%M%S')
                            time_str = dt.strftime('%Y-%m-%d %H:%M')
                        except:
                            time_str = time_published
                    else:
                        time_str = "Unknown"

                    source = article.get('source', 'Unknown')
                    authors = article.get('authors', [])
                    author_str = ", ".join(authors) if authors else "Unknown"

                    st.caption(f"📅 {time_str} | 📰 {source} | ✍️ {author_str}")

                    # Summary
                    summary = article.get('summary', 'No summary available')
                    st.write(summary[:300] + "..." if len(summary) > 300 else summary)

                    # Tickers mencionados
                    ticker_sentiment = article.get('ticker_sentiment', [])
                    if ticker_sentiment:
                        ticker_tags = []
                        for ts in ticker_sentiment[:5]:  # Mostra até 5 tickers
                            ticker = ts.get('ticker', '')
                            relevance = float(ts.get('relevance_score', 0))
                            ticker_tags.append(f"`{ticker}` ({relevance:.2f})")
                        st.markdown("**Tickers:** " + " ".join(ticker_tags))

                    # Link
                    url = article.get('url', '')
                    if url:
                        st.markdown(f"[🔗 Read full article]({url})")

                with col2:
                    # Sentiment badge
                    sentiment_emoji = sentiment_to_emoji(sentiment_score)
                    sentiment_color = sentiment_to_color(sentiment_score)

                    st.markdown(f"""
                    <div style='text-align: center; padding: 20px; background-color: {sentiment_color}; border-radius: 10px; color: white;'>
                        <h1>{sentiment_emoji}</h1>
                        <h3>{sentiment_label}</h3>
                        <p style='font-size: 20px; margin: 0;'>{sentiment_score:.3f}</p>
                    </div>
                    """, unsafe_allow_html=True)

                    # Relevance score
                    relevance = float(article.get('relevance_score', 0))
                    st.metric("Relevance", f"{relevance:.2f}")

                st.divider()

    elif st.session_state.news_data is not None:
        st.warning("No news found for the selected filters")

    else:
        st.info("👆 Configure filters above and click 'Search News'")

        # Exemplo de uso
        with st.expander("ℹ️ How to use"):
            st.markdown("""
            ### News &amp; Sentiment Analysis

            This page uses Alpha Vantage's News Sentiment API to provide:

            1. **Real-time market news** from multiple sources
            2. **Sentiment analysis** for each article
            3. **Ticker-specific sentiment** scores
            4. **Topic filtering** (technology, earnings, IPO, etc.)

            #### Sentiment Score Guide:
            - **> 0.35**: Very Positive 😊
            - **0.15 to 0.35**: Positive 🙂
            - **-0.15 to 0.15**: Neutral 😐
            - **-0.35 to -0.15**: Negative 😟
            - **< -0.35**: Very Negative 😢

            #### Tips:
            - Enter multiple tickers separated by commas (e.g., AAPL,MSFT,GOOGL)
            - Select relevant topics to narrow down results
            - Use filters to find positive/negative news quickly
            - Check relevance scores to find most important articles
            """)

# ==================== ETF FINDER ====================
elif page == "🔎 Symbol Search":
    st.title("🔎 ETF Finder")

    st.markdown("""
    Find which major ETFs hold a specific stock and see their details.
    Search through the **100 most liquid ETFs** in the market.
    """)

    # Inicializa session state
    if 'etf_finder_results' not in st.session_state:
        st.session_state.etf_finder_results = None
    if 'etf_finder_prices' not in st.session_state:
        st.session_state.etf_finder_prices = {}

    col1, col2 = st.columns([3, 1])

    with col1:
        stock_symbol = st.text_input(
            "Enter Stock Symbol", 
            value="AAPL", 
            key="etf_finder_symbol",
            help="Enter a stock symbol to find which ETFs hold it"
        )

    with col2:
        st.write("")
        st.write("")
        if st.button("🔍 Find ETFs", key="etf_finder_search"):
            if stock_symbol:
                try:
                    # Aviso sobre o tempo
                    st.info(f"⏳ Searching {stock_symbol} in 100 ETFs... This will take approximately 20-30 minutes due to API rate limits (5 requests/minute).")

                    progress_bar = st.progress(0)
                    status_text = st.empty()

                    # Busca nos 100 ETFs
                    results = []
                    total_etfs = len(TOP_100_ETFS)

                    for idx, etf in enumerate(TOP_100_ETFS):
                        try:
                            status_text.text(f"Searching in {etf}... ({idx+1}/{total_etfs})")
                            progress_bar.progress((idx + 1) / total_etfs)

                            data = api.get_etf_profile(etf)

                            if 'holdings' in data and data['holdings']:
                                for holding in data['holdings']:
                                    if holding.get('symbol', '').upper() == stock_symbol.upper():
                                        results.append({
                                            'etf_symbol': etf,
                                            'etf_name': data.get('name', 'N/A'),
                                            'net_assets': data.get('net_assets', 0),
                                            'expense_ratio': data.get('net_expense_ratio', 0),
                                            'dividend_yield': data.get('dividend_yield', 0),
                                            'description': data.get('description', 'N/A'),
                                            'holding_weight': holding.get('weight', 0),
                                            'holding_shares': holding.get('shares', 0)
                                        })
                                        break
                        except Exception as e:
                            continue

                    progress_bar.empty()
                    status_text.empty()

                    st.session_state.etf_finder_results = results
                    st.session_state.etf_finder_symbol = stock_symbol

                    # Busca preços dos ETFs encontrados
                    if results:
                        st.info("📊 Fetching current prices...")
                        st.session_state.etf_finder_prices = {}
                        for result in results:
                            try:
                                etf_sym = result['etf_symbol']
                                price_data = api.get_time_series_daily(etf_sym, outputsize='compact')
                                if 'Time Series (Daily)' in price_data:
                                    latest_date = list(price_data['Time Series (Daily)'].keys())[0]
                                    latest_price = float(price_data['Time Series (Daily)'][latest_date]['4. close'])
                                    st.session_state.etf_finder_prices[etf_sym] = latest_price
                            except:
                                st.session_state.etf_finder_prices[etf_sym] = None

                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
                    st.session_state.etf_finder_results = None
            else:
                st.warning("⚠️ Please enter a stock symbol")

    # Função auxiliar para converter valores
    def safe_float(value, default=0):
        try:
            if value is None or value == '' or value == 'None':
                return default
            return float(value)
        except (ValueError, TypeError):
            return default

    # Exibe resultados se existirem
    if st.session_state.etf_finder_results is not None:
        results = st.session_state.etf_finder_results
        stock_symbol = st.session_state.etf_finder_symbol

        if len(results) > 0:
            # Ordena por market cap (net assets)
            results_sorted = sorted(results, key=lambda x: safe_float(x['net_assets'], 0), reverse=True)

            # Pega os top 5
            top_5 = results_sorted[:5]

            st.success(f"✅ Found {len(results)} ETFs holding {stock_symbol}. Showing **Top 5 by Market Cap**:")

            # Exibe cada ETF
            for idx, etf in enumerate(top_5, 1):
                with st.container():
                    # Cabeçalho com ranking
                    col_rank, col_title = st.columns([1, 11])
                    with col_rank:
                        st.markdown(f"### #{idx}")
                    with col_title:
                        st.subheader(f"{etf['etf_symbol']} - {etf['etf_name']}")

                    # Métricas principais
                    col1, col2, col3, col4, col5 = st.columns(5)

                    with col1:
                        price = st.session_state.etf_finder_prices.get(etf['etf_symbol'])
                        if price:
                            st.metric("💵 Price", f"${price:.2f}")
                        else:
                            st.metric("💵 Price", "N/A")

                    with col2:
                        net_assets = safe_float(etf['net_assets'])
                        if net_assets > 0:
                            st.metric("💰 Market Cap", f"${net_assets/1e9:.2f}B")
                        else:
                            st.metric("💰 Market Cap", "N/A")

                    with col3:
                        div_yield = safe_float(etf['dividend_yield'])
                        if div_yield > 0:
                            st.metric("📊 Dividend Yield", f"{div_yield*100:.2f}%")
                        else:
                            st.metric("📊 Dividend Yield", "N/A")

                    with col4:
                        expense = safe_float(etf['expense_ratio'])
                        if expense > 0:
                            st.metric("💸 Expense Ratio", f"{expense*100:.2f}%")
                        else:
                            st.metric("💸 Expense Ratio", "N/A")

                    with col5:
                        weight = safe_float(etf['holding_weight'])
                        if weight > 0:
                            st.metric(f"📈 {stock_symbol} Weight", f"{weight*100:.2f}%")
                        else:
                            st.metric(f"📈 {stock_symbol} Weight", "N/A")

                    # Descrição
                    if etf['description'] and etf['description'] != 'N/A':
                        with st.expander("📄 Description"):
                            st.write(etf['description'])

                    st.divider()

            # Tabela comparativa dos Top 5
            st.subheader("📊 Top 5 Comparison Table")

            comparison_data = []
            for etf in top_5:
                comparison_data.append({
                    'Rank': f"#{top_5.index(etf) + 1}",
                    'ETF': etf['etf_symbol'],
                    'Name': etf['etf_name'][:30] + '...' if len(etf['etf_name']) > 30 else etf['etf_name'],
                    'Price': f"${st.session_state.etf_finder_prices.get(etf['etf_symbol'], 0):.2f}" if st.session_state.etf_finder_prices.get(etf['etf_symbol']) else "N/A",
                    'Market Cap': f"${safe_float(etf['net_assets'])/1e9:.2f}B",
                    'DY': f"{safe_float(etf['dividend_yield'])*100:.2f}%",
                    'Fee': f"{safe_float(etf['expense_ratio'])*100:.2f}%",
                    f'{stock_symbol} Weight': f"{safe_float(etf['holding_weight'])*100:.2f}%"
                })

            df_comparison = pd.DataFrame(comparison_data)
            st.dataframe(df_comparison, use_container_width=True, hide_index=True)

            # Mostrar todos os ETFs encontrados (se mais de 5)
            if len(results) > 5:
                with st.expander(f"📋 View all {len(results)} ETFs holding {stock_symbol}"):
                    all_data = []
                    for idx, etf in enumerate(results_sorted, 1):
                        all_data.append({
                            'Rank': f"#{idx}",
                            'ETF': etf['etf_symbol'],
                            'Name': etf['etf_name'][:40] + '...' if len(etf['etf_name']) > 40 else etf['etf_name'],
                            'Market Cap': f"${safe_float(etf['net_assets'])/1e9:.2f}B",
                            f'{stock_symbol} Weight': f"{safe_float(etf['holding_weight'])*100:.2f}%"
                        })

                    df_all = pd.DataFrame(all_data)
                    st.dataframe(df_all, use_container_width=True, hide_index=True)

        else:
            st.warning(f"❌ No ETFs found holding {stock_symbol}")
            st.info("💡 Try searching for a more popular stock (e.g., AAPL, MSFT, GOOGL, NVDA)")

    else:
        st.info("👆 Enter a stock symbol and click 'Find ETFs' to see which major ETFs hold it")

        # Informações sobre a busca
        with st.expander("ℹ️ About this search"):
            st.markdown(f"""
            ### How it works:

            This tool searches through the **{len(TOP_100_ETFS)} most liquid ETFs** in the market to find which ones hold your selected stock.

            #### ETF Categories Covered:
            """)

            for category, etfs in ETF_CATEGORIES.items():
                st.markdown(f"**{category}:** {len(etfs)} ETFs")

            st.markdown("""
            #### ⏱️ Search Time:
            - Due to API rate limits (5 requests/minute), searching all 100 ETFs takes approximately **20-30 minutes**
            - The search runs in the background and shows progress
            - Results are cached, so you can navigate away and come back

            #### 📊 Results Show:
            - **Top 5 ETFs** by market capitalization
            - Current price, market cap, dividend yield, expense ratio
            - Weight of your stock in each ETF
            - Full description of each ETF
            - Comparison table for easy analysis
            """)

        # Exemplos
        with st.expander("💡 Popular Stocks to Try"):
            col1, col2, col3 = st.columns(3)

            with col1:
                st.markdown("""
                **Technology:**
                - AAPL (Apple)
                - MSFT (Microsoft)
                - GOOGL (Google)
                - NVDA (NVIDIA)
                - TSLA (Tesla)
                - META (Meta)
                - AMZN (Amazon)
                """)

            with col2:
                st.markdown("""
                **Finance:**
                - JPM (JPMorgan)
                - BAC (Bank of America)
                - WFC (Wells Fargo)
                - GS (Goldman Sachs)
                - MS (Morgan Stanley)
                - C (Citigroup)
                """)

            with col3:
                st.markdown("""
                **Healthcare:**
                - JNJ (Johnson & Johnson)
                - UNH (UnitedHealth)
                - PFE (Pfizer)
                - ABBV (AbbVie)
                - TMO (Thermo Fisher)
                - LLY (Eli Lilly)
                """)

