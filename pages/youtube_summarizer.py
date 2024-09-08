from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_google_genai import GoogleGenerativeAI, HarmCategory, HarmBlockThreshold
from youtube_processing.youtube_info import get_transcript_from_video_id, convert_format, retrive_text_from_list
import streamlit as st
import typing

st.title('動画要約')
selected_type = st.radio('モードを選択', ['normal', 'explain', 'detail']) 
selected_lang = st.radio('言語を選択', ['ja', 'en']) # 選択肢を修正

def set_prompt(type: str = 'normal') -> ChatPromptTemplate:
    if type == 'normal':
        instruction_text = \
        '''
        1600字程度で以下の動画内容を日本語で要約してください
        ------------------------------------------------
        {content}
        ------------------------------------------------
        '''
    elif type == 'explain':
        instruction_text = \
        '''
        3000字程度で以下の動画内容を日本語で詳説してください
        ------------------------------------------------
        {content}
        ------------------------------------------------
        '''
    else:
        instruction_text = \
        '''
        8000字程度で以下の動画内容を日本語で詳説してください
        ------------------------------------------------
        {content}
        ------------------------------------------------
        '''

    
    prompt = ChatPromptTemplate.from_messages(
        ('human', instruction_text)
    )

    return prompt




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

    prompt = set_prompt(selected_type)


    content = retrive_text_from_list(transcripts_list)
    transcripts = convert_format(transcripts_list)

    chain = prompt | model | StrOutputParser()


    st.write_stream(chain.stream({'content': content}))
    if selected_type == 'normal':
        st.markdown("## Original Text")
        st.write_stream(transcripts)

    