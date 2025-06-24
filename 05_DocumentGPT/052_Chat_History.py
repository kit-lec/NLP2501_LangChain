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

import streamlit as st

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

# ------------------------------------------------------------------------
# 사용자가 메세지를 보내거나 UI  에 새로운 데이터가 생길때 마다,
# Streamlit 은 *.py 파일을 위에서 아래 방향으로 실행한다.
# 그 말은 embed_file() 도 다시 호출된다는 말이다.  
# 파일이 변경되지 않았슴에도 이 모든 과정을 다시 또 한다는 것은 매우 비효율적이다. (시간! 비용!)

# @st.cache_resource
# def embed_file(file매개변수) 
#   https://docs.streamlit.io/develop/api-reference/caching-and-state/st.cache_resource
#  
#   최초 embed_file(file) 호출시 실행될것이다.  그리고 리턴값을 cache 해둔다.
#   그러나 두번째 호출시에는 만약 이 매개변수 file 이 동일하다면  
#                          (즉 유저가 다른 파일을 올리지 않았다면)
#   Streamlit 은 이 함수의 호출을 재실행하지 않는다.
#   대신에! 기존에 리턴했던 cache 되었던 값을 다시 리턴된다!
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


# 메세지 보내는 함수 작성
def send_message(message, role, save=True):
    with st.chat_message(role):
        st.markdown(message)
    if save:
        st.session_state['messages'].append({'message': message, 'role': role})

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

    # message = st.chat_input("") # @st.cache_resource 확인용

    send_message('준비되었습니다. 질문해보세요!', 'ai', save=False)
    paint_history()

    # human message
    message = st.chat_input("업로드한 file에 대해 질문을 남겨보세요...")
    if message:
        send_message(message, 'human')
        # 임시로 ai 메세지도 띄어보자. (확인용)
        # send_message(f'{message}에 대한 답변입니다', 'ai')


else:
    st.session_state['messages'] = []  # 초깃값, file 이 없거나 삭제되면(None) 초기화 한다.










