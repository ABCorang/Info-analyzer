from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_google_genai import GoogleGenerativeAI, HarmCategory, HarmBlockThreshold
from langchain_community.document_loaders import YoutubeLoader
from pytube import YouTube
import pytube.exceptions as pytube_exceptions
from youtube_processing.youtube_info import get_transcript_from_video_id, convert_format, retrive_text_from_list

import streamlit as st
import traceback
import requests

st.title('動画要約')
selected_lang = st.radio('言語を選択', ['ja', 'en']) # 選択肢を修正

summarize_prompt = '''
800字程度で以下の動画内容を要約してください

------------------------------------------------
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


id = st.text_input('youtube video id:')
if id:
    st.spinner('Loading...')
    transcripts_list = get_transcript_from_video_id(id, selected_lang)
    prompt = ChatPromptTemplate.from_messages(
        ('human', summarize_prompt)
    )


    content = retrive_text_from_list(transcripts_list)
    transcripts = convert_format(transcripts_list)

    chain = prompt | model | StrOutputParser()


    st.write_stream(chain.stream({'content': content}))
    st.markdown("## Original Text")
    st.write_stream(transcripts)

    