import unicodedata
import pandas as pd
import plotly.graph_objects as go
import datetime
import streamlit as st
import yfinance as yf


default_start_date = datetime.datetime.now() - datetime.timedelta(days=365)

def get_data(ticker, start_date=default_start_date):
    # df = pdr.DataReader(ticker, data_source='stooq', start=start_d).sort_index()
    df = yf.download(tickers=ticker, start=start_date)
    return df

def calculate_year_to_date_return(df):
    """
    年初来の騰落率を計算する関数

    Args:
        df (pd.DataFrame): 株価データのDataFrame

    Returns:
        float: 年初来の騰落率
    """
    # 現在の年を取得
    current_year = df.index[-1].year
    # 現在の年の最初の有効なインデックスを取得
    first_valid_index_of_current_year = df[f'{current_year}':].first_valid_index()
    # 現在の年の最初のデータを取得
    first_data_of_current_year = df.loc[first_valid_index_of_current_year]
    # 年初来の騰落率を計算
    year_to_date_return = ((df.iloc[-1] - first_data_of_current_year) / first_data_of_current_year)['Adj Close'] * 100

    return year_to_date_return

def main():

    with st.sidebar:
        st.title("Stock")  # サイドバーにタイトルを追加
        default_ticker = st.radio(
            'exampl tickers',
            ['^SPX', 'TECL', '^DJI', '^IXIC']
        )

        cnn_link = 'https://edition.cnn.com/markets/fear-and-greed'
        st.markdown(f'links <br>[fear and greed]({cnn_link})', unsafe_allow_html=True)


    input_start_date  = st.date_input(
        "When\'s sart date",
        value=default_start_date
    )

    st.write('start date:', default_start_date)

    input_ticker = st.text_input('please input ticker:')

    # input_tickerがあればそれを、なければdefault_tickerを使用
    raw_ticker = input_ticker or default_ticker

    if raw_ticker:
        ticker = unicodedata.normalize('NFKC', raw_ticker)
        ticker_df = get_data(ticker)

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

        #年初来上昇率表示
        year_to_date_return = calculate_year_to_date_return(ticker_df)
        st.markdown(f'### 年初来{year_to_date_return:.2f}%')

        # 同ページ内でplotlyチャートを描画
        st.plotly_chart(fig)

        # 対象tickerの価格データ（新しい順）に表示
        sorted_ticker_df = ticker_df.sort_values(by='Date', ascending=False)
        st.write(sorted_ticker_df)


if __name__ == "__main__":
    main()