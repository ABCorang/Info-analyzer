import unicodedata
import pandas as pd
import plotly.graph_objects as go
import datetime
import streamlit as st
import yfinance as yf


default_start_date = datetime.datetime.now() - datetime.timedelta(days=730)

def get_data(ticker, start_date=None):

    if start_date is None:
        df = yf.Ticker(ticker)
    else:
        df = yf.Ticker(ticker)
        df = df.history(start=start_date)
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
    year_to_date_return = ((df.iloc[-1] - first_data_of_current_year) / first_data_of_current_year)['Close'] * 100

    return year_to_date_return


def calculate_investment_results(ticker, df, investment_amount=1000):
    """積立投資と一括投資の結果を計算する関数。"""
    investment_df = df.copy() 
    investment_df['periodic_investment'] = investment_amount# 定期投資額
    investment_df['cumulative_investment'] = investment_df['periodic_investment'].cumsum()# 累積投資額
    investment_df['cumulative_units'] = (investment_df['periodic_investment'] / investment_df[f'{ticker}_jpy']).cumsum()# 累積投資単位数


    # 一括買い
    lump_sum_result = (investment_df['cumulative_investment'].iloc[-1] / investment_df[f'{ticker}_jpy'].iloc[0]) * investment_df[f'{ticker}_jpy'].iloc[-1]
    # 積立買い
    dollar_cost_averaging_result = investment_df[f'{ticker}_jpy'].iloc[-1] * investment_df['cumulative_units'].iloc[-1]

    return lump_sum_result, dollar_cost_averaging_result



def main():

    with st.sidebar:
        st.title("Stock")  # サイドバーにタイトルを追加
        default_ticker = st.radio(
            'exampl tickers',
            ['^SPX', 'TECL', '^DJI', '^IXIC']
        )

        #リンク
        cnn_link = 'https://edition.cnn.com/markets/fear-and-greed'
        st.markdown(f'links <br>[fear and greed]({cnn_link})', unsafe_allow_html=True)

        st.markdown('毎日積立シミュレーション')
        selected_num = st.slider('毎日積み立てる額を選択', 0, 10**4, 1000)
        st.write(selected_num,'(円)')

 
    input_start_date  = st.date_input(
        "When\'s sart date",
        value=default_start_date
    )

    st.write('start date:', input_start_date)

    input_ticker = st.text_input('please input ticker:')

    # input_tickerがあればそれを、なければdefault_tickerを使用
    raw_ticker = input_ticker or default_ticker

    if raw_ticker:
        ticker = unicodedata.normalize('NFKC', raw_ticker)
        ticker_df = get_data(ticker, start_date=input_start_date)


        target_days = pd.date_range(start=ticker_df.index[0], end=ticker_df.index[-1], freq='D')
        
        # 対象期間からdf上にない(=休業日)日付を取り出したリスト
        clsoed_days_list = [d for d in target_days if not d in ticker_df.index]
        # 空のFigureオブジェクトを作成
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

        st.markdown('---')
        # ドル円データを取得(円換算用
        usdjpy = yf.download("JPY=X", start=input_start_date)
        combined_df = pd.concat([ticker_df['Close'], usdjpy['Close']], axis=1)
        combined_df.columns = [f'{ticker}', 'usdjpy']
        combined_df = combined_df.dropna()
        combined_df[f'{ticker}_jpy'] = combined_df[f'{ticker}'] * combined_df['usdjpy']
        # 投資結果を計算
        lump_sum_result, dollar_cost_averaging_result = calculate_investment_results(ticker, combined_df, investment_amount=selected_num)
        st.write(f"一括投資結果: {lump_sum_result:,.0f}円")
        st.write(f"積立投資結果: {dollar_cost_averaging_result:,.0f}円")
        st.write(combined_df)


if __name__ == "__main__":
    main()