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

import streamlit as st

# ────────────────────────────────────────
# 🎃 LLM 로직
# ────────────────────────────────────────
llm = ChatOpenAI(
    temperature=0.1
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
                "context": retriever | RunnableLambda(format_docs),

                # ④ chain 의 input 이 question 값에도 전달된다. 
                "question": RunnablePassthrough()
            }
            # ⑤ 위 'context' 와 'question' 이 prompt 에 전달되어 prompt 포맷팅
            | prompt
            # ⑥ 위에서 완성된 prompt 로 llm 호출
            | llm
        )
        response = chain.invoke(message)  # ① 사용자 입력 message 는 chain 의 input 이 된다
        # ⑦ ↑ llm 호출 결과가 chain.invoke() 의 리턴값

        send_message(response.content, "ai")


else:
    st.session_state['messages'] = []  # 초깃값, file 이 없거나 삭제되면(None) 초기화 한다.










