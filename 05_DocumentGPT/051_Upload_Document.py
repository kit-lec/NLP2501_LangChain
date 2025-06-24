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


def embed_file(file):
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
"""
)


file = st.file_uploader(
    label="Upload a .txt .pdf or .docx file",
    type=["pdf", "txt", "docx"],
)

if file:
    # st.write(file)  # 확인용
    # ↑ 나중에 이 파일을 UnstructuredFileLoader 에게 파일 위치를 넘겨야 함

    # file_content = file.read()   
    # st.write(file_content) # 확인용.

    # --------------------------------------------------
    retriever = embed_file(file)


    # ---------------
    # 확인: retriever 동작
    docs = retriever.invoke("ministry of truth") # -> List[Document]
    st.write(docs)












