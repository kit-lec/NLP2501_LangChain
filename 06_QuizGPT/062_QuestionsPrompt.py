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

from langchain_core.callbacks.streaming_stdout import StreamingStdOutCallbackHandler

import streamlit as st

# ────────────────────────────────────────
# 🎃 LLM 로직
# ────────────────────────────────────────

llm = ChatOpenAI(
    temperature=0.1,
    model='gpt-3.5-turbo-1106',
    streaming=True,
    callbacks=[StreamingStdOutCallbackHandler()],
)





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


def format_docs(docs):
    return "\n\n".join(document.page_content for document in docs)

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

    else:
        topic = st.text_input("Search Wikipedia...")
        if topic:
            retriever = WikipediaRetriever(top_k_results=5)

            with st.status("Searching Wikipedia..."):
                docs = retriever.invoke(topic)


# 문서(docs) 가 존재한다면
if not docs:
    st.markdown(
        """
Welcome to QuizGPT.
            
I will make a quiz from Wikipedia articles or files you upload to test your knowledge and help you study.
            
Get started by uploading a file or searching on Wikipedia in the sidebar.
    """
    )
else:
    prompt = ChatPromptTemplate.from_messages([
        ("system", """
    You are a helpful assistant that is role playing as a teacher.
         
    Based ONLY on the following context make 10 questions to test the user's knowledge about the text.
   
    Each question should have 4 answers, three of them must be incorrect and one should be correct.
         
    Use (o) to signal the correct answer.
         
    Question examples:
         
    Question: What is the color of the ocean?
    Answers: Red|Yellow|Green|Blue(o)
         
    Question: What is the capital or Georgia?
    Answers: Baku|Tbilisi(o)|Manila|Beirut
         
    Question: When was Avatar released?
    Answers: 2007|2001|2009(o)|1998
         
    Question: Who was Julius Caesar?
    Answers: A Roman Emperor(o)|Painter|Actor|Model
         
    Your turn!
         
    Context: {context}

         """),


    ])

    # chain 생성
    chain = {"context": format_docs} | prompt | llm

    # ↓ 버튼을 누르면 quiz 가 생성되게 해보기
    start = st.button("Generate Quiz")
    if start:
        chain.invoke(docs)










