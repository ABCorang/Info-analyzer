import unicodedata
import pandas as pd
import plotly.graph_objects as go
import datetime
import streamlit as st
import yfinance as yf


with st.sidebar:
    st.title("Stock")  # サイドバーにタイトルを追加
    default_ticker = st.radio(
        'exampl tickers',
        ['^SPX', 'TECL', '^DJI', '^IXIC']
    )

start_date = st.date_input(
    "When\'s sart date",
    datetime.datetime.now() - datetime.timedelta(days=365)
)

st.write('start date:', start_date)

def get_data(ticker, start_d=None):
    # df = pdr.DataReader(ticker, data_source='stooq', start=start_d).sort_index()
    df = yf.download(tickers=ticker, start=start_date)
    return df

input_ticker = st.text_input('please input ticker:')

# input_tickerがあればそれを、なければdefault_tickerを使用
raw_ticker = input_ticker or default_ticker

if raw_ticker:
    ticker = unicodedata.normalize('NFKC', raw_ticker)
    ticker_df = get_data(ticker, start_d=start_date)

    target_days = pd.date_range(start=ticker_df.index[0], end=ticker_df.index[-1], freq='D')
    
    # 対象期間からdf上にない(=休業日)日付を取り出したリスト
    clsoed_days_list = [d for d in target_days if not d in ticker_df.index]

    data = [
        go.Candlestick(yaxis="y1", x=ticker_df.index, open=ticker_df["Open"], high=ticker_df["High"], low=ticker_df["Low"], close=ticker_df["Close"]),
        go.Bar(yaxis="y3", x=ticker_df.index, y=ticker_df["Volume"], name= "Volume", marker={ "color": "slategray" } ) 
    ]

    layout = {
        "height": 700,
        "xaxis" : { "rangeslider": { "visible": False } }, # rangesliderを表示しない
        "yaxis1": { "domain": [.30, 1.0], "title": "価格（円）", "side": "left", "tickformat": "," },
        "yaxis2": { "domain": [.20, .30] },
        "yaxis3": { "domain": [.00, .20], "title": "Volume", "side": "right" },
        "plot_bgcolor":"light blue"
    }


    fig = go.Figure(layout=layout, data=data)
    # 不要な日付を非表示にする
    fig.update_xaxes(rangebreaks=[dict(values=clsoed_days_list)])
    # ボタンを押した場合別画面チャートを開く
    if st.button('open another chart'):
        fig.show()
    # 同ページ内でチャートを描画
    st.plotly_chart(fig)
    # 対象tickerの価格データ（新しい順）に表示
    sorted_ticker_df = ticker_df.sort_values(by='Date', ascending=False)
    st.write(sorted_ticker_df)
