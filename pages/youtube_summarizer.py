from langchain_core.prompts import ChatPromptTemplate
from langchain_community.document_loaders import YoutubeLoader
from langchain_core.output_parsers import StrOutputParser
from langchain_google_genai import GoogleGenerativeAI, HarmCategory, HarmBlockThreshold


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

model = GoogleGenerativeAI(model='gemini-1.5-flash-latest',
            safety_settings={
                HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE
            })


def get_content_from_url(url):
    loader = YoutubeLoader.from_youtube_url(youtube_url=url,
                                   add_video_info=True,
                                   language=['en', 'ja'])
    
    # list of `Document` (page_content, metadata)
    docs = loader.load() 
    try:
        if docs:
            content = docs[0].page_content
            try:
                title = docs[0].metadata['title']
            except (KeyError, pytube_exceptions.PytubeError):
                title = 'タイトル不明'

            return f'Title: {title}\n\n{content}'
        else:
            return f'なし'
    
    except pytube_exceptions.PytubeError as e:
        # エラーをログに記録
        print(f"PytubeError: {str(e)}")
        return '動画の内容を取得できませんでした'
    except Exception as e:
        # その他の予期しないエラーをキャッチ
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

    