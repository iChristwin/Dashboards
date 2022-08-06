import streamlit as st  # For dashboard-ing
import pandas as pd  # For data management
import plotly.graph_objects as go
import requests

st.set_page_config(page_title='BAR.', layout="wide")

st.sidebar.title('Side Panel')

PAIRS = ['EUR/USD', 'GBP/JPY', 'EUR/AUD']
INTERVAL = ['1min', '5min', '15min', '30min', '45min', '1h', '2h', '4h', '1day', '1week', '1month']
default_interval = INTERVAL.index('4h')


col_1, col_2 = st.sidebar.columns(2)
with col_1:
    pair = st.selectbox('Select Pair', PAIRS)
with col_2:
    interval = st.selectbox('Select Interval', INTERVAL, index=default_interval)


api_key = st.secrets['DATA_API_KEY']
timezone = "Africa/Lagos"
no_candles = 200

series_url = f'https://api.twelvedata.com/time_series?symbol={pair}' \
             f'&interval={interval}&apikey={api_key}&outputsize={no_candles}' \
             f'&timezone{timezone}'


@st.cache
def get_data():
    response = requests.get(series_url)
    data = pd.DataFrame(response.json()['values'])

    cols = data.columns.drop('datetime')
    data[cols] = data[cols].apply(pd.to_numeric, errors='coerce')
    return data


def plot_chart(upper, lower):
    time_range = [df.datetime.iloc[0], df.datetime.iloc[-1]]
    candles = go.Candlestick(
        x=df['datetime'], open=df['open'], high=df['high'],
        low=df['low'], close=df['close'], name=pair
    )

    chart = go.Figure(data=[candles])
    chart.update_layout(xaxis_rangeslider_visible=False)
    chart.add_trace(go.Line(x=time_range, y=[upper, upper], name='upper',
                            line=dict(color='blue', width=.5))
                    )
    chart.add_trace(go.Line(x=time_range, y=[lower, lower], name='lower',
                            line=dict(color='indigo', width=.5, dash='dashdot'))
                    )
    # chart.update_layout(width=1000, height=500)
    # chart.update_layout(xaxis_showgrid=False, yaxis_showgrid=False)
    return chart


df = get_data()
last_price = df.close.iloc[0]
st.title(f'{pair} at {last_price}')

_upper = df['open'].mean()
_lower = _upper - (df['open'].std() / 7)

expander = st.sidebar.expander("Subscribe to a price alert")
with expander:
    upper = st.number_input('Upper', value=_upper)
    lower = st.number_input('Lower', value=_lower)
    email = st.text_input('Subscriber Gmail (gmail only)')

fig = plot_chart(upper, lower)
st.plotly_chart(fig, use_container_width=True)

