from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_google_genai import GoogleGenerativeAI, HarmCategory, HarmBlockThreshold
from langchain_community.document_loaders import YoutubeLoader
from pytube import YouTube
import pytube.exceptions as pytube_exceptions

import streamlit as st
import traceback
import requests

st.title('動画要約')

summarize_prompt = '''
800字程度で以下の動画内容を要約してください

------------------------------------------------
{content}
------------------------------------------------

'''

script_prompt = '''
以下の音声スクリプトを以下のような5分都度の形式で"日本語で"出力してください


00:00-05:00
text

05:00-10:00
text

さらに音声スクリプトが続く場合同様の形式で最後まで

------------------------------------------------
音声スクリプト
{content}
------------------------------------------------

'''

model = GoogleGenerativeAI(model='gemini-1.5-flash-exp-0827',
            safety_settings={
                HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE
            })


def get_content_from_url(url):
    try:
        # まず、YouTubeオブジェクトを作成
        yt = YouTube(url, timeout=30)
        
        # タイトルを取得（エラーハンドリング付き）
        try:
            title = yt.title
        except pytube_exceptions.PytubeError:
            print(f'PytubeError: {str(e)}')
            title = 'タイトル不明'
        
        # YoutubeLoaderを使用してコンテンツを取得
        loader = YoutubeLoader.from_youtube_url(
            youtube_url=url,
            add_video_info=False,  # ビデオ情報の追加を無効化
            language=['en', 'ja']
        )
        
        docs = loader.load()
        
        if docs:
            content = docs[0].page_content
            return f'Title: {title}\n\n{content}'
        else:
            return 'コンテンツなし'
    
    except pytube_exceptions.PytubeError as e:
        print(f'PytubeError: {str(e)}')
        return '動画の内容を取得できませんでした'
    except Exception as e:
        print(f'Unexpected error: {str(e)}')
        return 'エラーが発生しました'


url = st.text_input('URL:')
if url:
    st.spinner('Loading...')
    content = get_content_from_url(url)
    prompt = ChatPromptTemplate.from_messages(
        ('human', summarize_prompt)
    )

    content = get_content_from_url(url)

    chain = prompt | model | StrOutputParser()


    prompt = ChatPromptTemplate.from_messages(
        ('human', script_prompt)
    )
    script_chain = prompt | model | StrOutputParser()

    st.write_stream(chain.stream({'content': content}))
    st.markdown("## Original Text")
    st.write_stream(script_chain.stream({'content': content}))

    