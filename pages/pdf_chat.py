import streamlit as st
import fitz #pymupdf
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings, GoogleGenerativeAI, HarmCategory, HarmBlockThreshold
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_community.chat_message_histories import StreamlitChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory



def set_chain(model, retriever):

    prompt = ChatPromptTemplate.from_template('''
    次の知識を用いて、できる限り知識に忠実にユーザーからの質問に日本語で詳しく答えてください
    また知識にない場合は、「テキストには記述がありません」と答えてください
    {context}
    
    {history}
    ----------------------------------------------------------------
    ユーザーからの質問
    {question}
    ''')

    chain = (
                {
            "context": lambda x: retriever.get_relevant_documents(x["question"]),
            "question": RunnablePassthrough(),
            "history": RunnablePassthrough()
        }
        | prompt 
        | model 
        | StrOutputParser()
    )
    

    return chain


model = GoogleGenerativeAI(model='gemini-1.5-flash-latest',
            safety_settings={
                HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE
            })

uploaded_byte_data = st.file_uploader('ファイルをアップロード', type='pdf')

# アップロードした場合の処理
if uploaded_byte_data and 'pdfvecotors' not in st.session_state:
    pdf_data = fitz.open(stream=uploaded_byte_data.read())

    # アップロードしたpdfのテキストをpdf_txt: strに代入
    pdf_txt = ''
    # pdf_data: fitz.Document
    for pdf_page in pdf_data:
        # pdf_page: fitz.Page　
        pdf_txt += pdf_page.get_text()


    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500, # チャンクの最大サイズ (文字数)
        chunk_overlap=0, # チャンク間の重複 (文字数)
    )

    pdf_text_list = text_splitter.split_text(pdf_txt)

    with st.spinner('テキストをvector storeに保存'):
        st.session_state.pdfvecotors = FAISS.from_texts(
            pdf_text_list,
            GoogleGenerativeAIEmbeddings(model='models/text-embedding-004')
        )

pdf_question = st.chat_input('pdfに質問')
if pdf_question:
    # ファイルがアップロードされてる場合の判定
    if 'pdfvecotors' in st.session_state:
        with st.spinner('....'):

            retriever = st.session_state.pdfvecotors.as_retriever(
                search_type="similarity",
                # 文書を何個取得するか (default: 4)
                search_kwargs={"k":10}
            )

            # チャット履歴を使用してチェーンを実行
            base_chain = set_chain(model, retriever)
            message_history = StreamlitChatMessageHistory(key="langchain_messages")
            chain_with_history = RunnableWithMessageHistory(
                base_chain,
                lambda session_id: message_history,
                input_messages_key="question",
                history_messages_key="history",
            )



            response = chain_with_history.invoke(
                {"question": pdf_question, "history": message_history.messages},
               config={"configurable": {"session_id": "pdf_chat"}},
            )

            st.write(response)


            # チャット履歴を表示
            for message in st.session_state.langchain_messages:
                with st.chat_message(message.type):
                    st.markdown(message.content)

    else:
        st.error("PDFファイルがアップロードされていません。")
    


clear_button = st.button('保存文書削除')
if clear_button:
    # st.session_state: dict[str, Any]
    if 'pdfvecotors' in st.session_state:
        st.write(st.session_state.pdfvecotors)
        st.write('--------------------------------')
        del st.session_state['pdfvecotors']  # キー自体を削除
    st.write(st.session_state)


clear_button = st.button('会話履歴削除')
if clear_button:
    # st.session_state: dict[str, Any]
    if 'langchain_messages' in st.session_state:
        st.write('--------------------------------')
        del st.session_state['langchain_messages']  # キー自体を削除
    # st.write(st.session_state)





    


