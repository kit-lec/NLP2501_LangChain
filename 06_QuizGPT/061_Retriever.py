import os
import time

print(f'✅ {os.path.basename( __file__ )} 실행됨 {time.strftime('%Y-%m-%d %H:%M:%S')}') # 실행파일명, 현재시간출력
print(f'\tOPENAI_API_KEY={os.getenv("OPENAI_API_KEY")[:20]}...') # OPENAI_API_KEY 필요!


# v0.3
from langchain_community.document_loaders.unstructured import UnstructuredFileLoader
from langchain_text_splitters.character import CharacterTextSplitter

from langchain_openai.chat_models.base import ChatOpenAI
from langchain_core.prompts.chat import ChatPromptTemplate

from langchain_community.retrievers.wikipedia import WikipediaRetriever


import streamlit as st

# ────────────────────────────────────────
# 🎃 LLM 로직
# ────────────────────────────────────────



# ────────────────────────────────────────
# 🍇 file load & cache
# ────────────────────────────────────────

file_dir = os.path.dirname(os.path.realpath(__file__))
upload_dir = os.path.join(file_dir, '.cache/quiz_files')
if not os.path.exists(upload_dir):
    os.makedirs(upload_dir)

# split_file()
# vector, embedding 필요없다. 오로지 문서가 필요하고,
# 그 문서들을 split 까지만 해두면 된다.
@st.cache_resource(show_spinner="Loading file...")
def split_file(file):
    file_content = file.read()
    file_path = os.path.join(upload_dir, file.name)

    with open(file_path, "wb") as f:
        f.write(file_content)

    splitter = CharacterTextSplitter.from_tiktoken_encoder(
        separator="\n",
        chunk_size=600,
        chunk_overlap=100,
    )

    loader = UnstructuredFileLoader(file_path)

    docs = loader.load_and_split(text_splitter=splitter)    
    return docs

# ────────────────────────────────────────
# ⭕ Streamlit 로직
# ────────────────────────────────────────

st.set_page_config(
    page_title="QuizGPT",
    page_icon="👩‍🌾",
)

st.title("QuizGPT")

with st.sidebar:
    docs = None  # 읽어들인 문서들

    choice = st.selectbox(
        label="Choose what you want to use.",
        options=(
            "File",
            "Wikipedia Article",
        ),
    )
    if choice == "File":
        file = st.file_uploader(
            "Upload a .docx , .txt or .pdf file",
            type=["pdf", "txt", "docx"],            
        )
        if file:
            docs = split_file(file)

            st.write(len(docs), '개의 Document 로 split') # 확인용
            st.write(docs)  # 확인용

    else:
        topic = st.text_input("Search Wikipedia...")
        # WikipediaRetriever 사용
        if topic:
            # tok_k_results= : retriever 결과중 첫 k개
            retriever = WikipediaRetriever(top_k_results=5)

            with st.status("Searching Wikipedia..."):
                docs = retriever.invoke(topic) # -> List[Document]

                st.write(len(docs), "개의 문서 retrieve") # 확인용
                st.write(docs) # 확인용












