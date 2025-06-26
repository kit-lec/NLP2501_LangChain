import os
import time

print(f'✅ {os.path.basename( __file__ )} 실행됨 {time.strftime('%Y-%m-%d %H:%M:%S')}') # 실행파일명, 현재시간출력
print(f'\tOPENAI_API_KEY={os.getenv("OPENAI_API_KEY")[:20]}...') # OPENAI_API_KEY 필요!


# v0.3
from langchain_community.document_loaders.unstructured import UnstructuredFileLoader
from langchain.embeddings.cache import CacheBackedEmbeddings
from langchain_openai.embeddings.base import OpenAIEmbeddings
from langchain.storage.file_system import LocalFileStore
from langchain_text_splitters.character import CharacterTextSplitter
from langchain_community.vectorstores.faiss import FAISS
from langchain_core.prompts.chat import ChatPromptTemplate
from langchain_openai.chat_models.base import ChatOpenAI
from langchain_core.runnables.base import RunnableLambda
from langchain_core.runnables.passthrough import RunnablePassthrough
# LangChain 의 context 안에 있는 callback handler 는
# 기본적으로 LLM 의 event 를 listen 하는 class 다. 가령.
# ex) LLM 이 무언가를 만들기 시작할때,  작업을 끝낼 때,  LLM 이 글자를 생성하거나,  
#     streaming 할때, LLM 에 에러가 발생할때.. 등등
# callback handler 를 사용하여 log 를 작성하거나 analytics 등으로 보내는 등의 유용한 동작을 구현해볼수 있다.

from langchain_core.callbacks.base import BaseCallbackHandler  # 이를 상속하여 CallbackHandler 구현

import streamlit as st

# ────────────────────────────────────────
# 🎃 LLM 로직
# ────────────────────────────────────────

class ChatCallbackHandler(BaseCallbackHandler):
    # CallbackHandler 는 event 들을 listen 하는 여러 함수들이 있다.
    # on_xxx() 으로 시작하는 함수들을 오버라이딩 하여 구현한다
    #    ex) LLM 상에서 발생한 event 를 다루는 함수들
    #       chain, retriever, 혹은 agent 에 대한 함수들도 있다.
    #    이벤트핸들러 함수 참조: https://python.langchain.com/api_reference/core/callbacks/langchain_core.callbacks.base.BaseCallbackHandler.html#langchain_core.callbacks.base.BaseCallbackHandler
    
    # ↓ on_llm_start() : LLM 작업 시작할때 호출
    #   많은 argument 들이 있지만 이번예제에선 걍 *args, **kwargs 로 받아낸다.  
    def on_llm_start(self, *args, **kwargs):
        print('🟨 llm_start')
        # 화면에 출력할 '메세지' 준비.  처음에는 empty
        self.message = ""

        # token 텍스트 들로 채워나갈 메세지 박스
        self.message_box = st.empty()  # <- 무언가를 담을 수 있는 빈 위젯 
        

    # ↓ on_llm_end() : LLM 작업 종료할때 호출
    def on_llm_end(self, *args, **kwargs):
        print('🟥 llm_end')
        # LLM 답변이 끝나면, 메세지를 저장하면 된다.
        save_message(self.message, "ai")

    # ↓ on_llm_new_token() : LLM이 생성해내는 새로운 token 마다 호출
    def on_llm_new_token(self, token, *args, **kwargs):
        print('🟪 llm_new_token', token)
        self.message += token  # 기존 message 에 token 추가
        self.message_box.markdown(self.message) # empty 박스에 markdown 을 넣어줄수 있다.


llm = ChatOpenAI(
    temperature=0.1,
    streaming=True,

    # callback 추가. 이를 통해 LLM에서 어떤 event 들이 일어나는지 알수 있다.
    callbacks=[
        ChatCallbackHandler(),
    ],
)

# retriever 의 결과(List[Document])를 받아 원하는 포맷(str)으로 리턴해주는 함수
# chain 의 RunnableLambda() 에 전달할 함수로 사용할거다.
def format_docs(docs):
    return '\n\n'.join(document.page_content for document in docs)


prompt = ChatPromptTemplate.from_messages([
    ("system",

     """
        Answer the question using ONLY the following context.
        If you don't know the answer just say you don't know. DON'T make anything up.            

        Context: {context}
     """),

    ("human", "{question}"),
])


# ────────────────────────────────────────
# 🍇 file load & cache
# ────────────────────────────────────────

# 업로드할 파일, 임베딩 벡터를 저장할 경로, 미리 생성해두기
upload_dir = r'./.cache/files'
embedding_dir = r'./.cache/embeddings'
if not os.path.exists(upload_dir):
    os.makedirs(upload_dir)
if not os.path.exists(embedding_dir):
    os.makedirs(embedding_dir)

@st.cache_resource(show_spinner="Embedding file...")
def embed_file(file):
    print('👿 embed_file() 호출')
    file_content = file.read()  # 업로드한 파일 읽어오기
    file_path = os.path.join(upload_dir, file.name)  # 업로드한 파일이 저장될 경로
    # st.write(file_content, file_path) # 확인용    

    # 업로드한 파일 저장
    with open(file_path, "wb") as f:
        f.write(file_content)  

    # 업로드된 '각각의 파일' 별로 embedding cache 디렉토리를 지정하여 준비
    cache_dir = LocalFileStore(os.path.join(embedding_dir, file.name))

    splitter = CharacterTextSplitter.from_tiktoken_encoder(
        separator='\n',
        chunk_size=600,
        chunk_overlap=100,
    )

    # 업로드된 파일을 로드 & split
    loader = UnstructuredFileLoader(file_path)
    docs = loader.load_and_split(text_splitter=splitter)

    # embeddings 생성하기 + cache 하기
    embeddings = OpenAIEmbeddings()
    cached_embeddings = CacheBackedEmbeddings.from_bytes_store(embeddings, cache_dir)

    # 위 embeddings 을 vector store 에 넣기
    vectorstore = FAISS.from_documents(docs, cached_embeddings)

    # retriever 얻기
    retriever = vectorstore.as_retriever()
    return retriever


# ────────────────────────────────────────
# ⭕ Streamlit 로직
# ────────────────────────────────────────

st.set_page_config(
    page_title = "DocumentGPT",
    page_icon = "📃",
)

st.title("Document GPT")

st.markdown(
    """
안녕하세요!
이 챗봇을 사용하여 여러분이 업로드한 파일에 대해 AI에게 물어보세요!

← sidebar 에 파일을 업로드 해두세요.
"""
)

# message 저장 메소드 따로 작성
def save_message(message, role):
    st.session_state['messages'].append({'message': message, 'role': role})

# 메세지 보내는 함수 작성
def send_message(message, role, save=True):
    with st.chat_message(role):
        st.markdown(message)
    if save:
        save_message(message, role)        

# 메세지(chat) 히스토리 그리는 함수
def paint_history():
    for message in st.session_state['messages']:  # message 는 {'message': message, 'role': role}
        send_message(
            message['message'],
            message['role'],
            save=False,
        )

with st.sidebar:
    file = st.file_uploader(
        label="Upload a .txt .pdf or .docx file",
        type=["pdf", "txt", "docx"],
    )

if file:
    retriever = embed_file(file)

    send_message('준비되었습니다. 질문해보세요!', 'ai', save=False)
    paint_history()

    message = st.chat_input("업로드한 file에 대해 질문을 남겨보세요...")
    if message:
        send_message(message, 'human')

        # 사용자가 어떤 질문(message)를 하면, retriever 를 invoke 할거고
        # retriever 는 우리에게 관련된 문서(들)을 줄거다
        # docs = retriever.invoke(message)
        # st.write(docs)  # 확인용.
        # docs = '\n\n'.join(document.page_content for document in docs)
        # prompt 완성하기
        # prompt = prompt.format_messages(context = docs, question=message)
        # st.write(prompt)  # 확인용
        # response = llm.invoke(prompt)
        # st.write(response)  # 확인용

        chain = (
            {
                # ② chain 의 input 을 이용해 retriever 를 자동으로 invoke => 결과 List[Document]
                # ③ 위 결과를 우리가 원하는 포맷(str)으로 변환하는 함수(format_docs)의 입력으로 전달. 
                #   함수의 리턴값이 'context' 값에 저장
                "context": retriever | RunnableLambda(format_docs),

                # ④ chain 의 input 이 'question' 값에도 전달된다. 
                "question": RunnablePassthrough()
            }
            # ⑤ 위 'context' 와 'question' 이 prompt 에 전달되어 prompt 포맷팅
            | prompt
            # ⑥ 위에서 완성된 prompt 로 llm 호출
            | llm
        )
        
        with st.chat_message("ai"):
            # with 블록 내부에서 chain 을 invoke 하면
            #   => CallbackHandler 가  message_box = st.empty() 를 호출할때,
            #     message_box 가 업데이트 할때도 AI가 한것처럼 보이게 된다.
            chain.invoke(message)
            

        


else:
    st.session_state['messages'] = []  # 초깃값, file 이 없거나 삭제되면(None) 초기화 한다.










