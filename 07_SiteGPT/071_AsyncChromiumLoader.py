import os
import time

print(f'✅ {os.path.basename( __file__ )} 실행됨 {time.strftime('%Y-%m-%d %H:%M:%S')}') # 실행파일명, 현재시간출력
print(f'\tOPENAI_API_KEY={os.getenv("OPENAI_API_KEY")[:20]}...') # OPENAI_API_KEY 필요!

import streamlit as st
# Chromium 의 headless instance 를 사용하여 HTML 페이지를 스크레이핑
from langchain_community.document_loaders.chromium import AsyncChromiumLoader
import asyncio  # 비동기 통신을 위한 모듈
# Set the event loop policy for Windows 
# (AsyncChromiumLoader 사용하여 페이지 요청시 Windows 환경에선 필요한 설정인듯.)
if hasattr(asyncio, "WindowsProactorEventLoopPolicy"):
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())


from langchain_community.document_transformers.html2text import Html2TextTransformer
# HTML 을 받아서 Text 로 변환(transform) 해주는 객체
html2text_transformer = Html2TextTransformer()



# ────────────────────────────────────────
# ⭕ Streamlit 로직
# ────────────────────────────────────────
st.set_page_config(
    page_title="SiteGPT",
    page_icon="🖥️",
)

st.title("SiteGPT")

with st.sidebar:
    url = st.text_input(
        "Write down a URL",
        placeholder="https://example.com",
    )


st.markdown(
"""
    Ask questions about the content of a website.
           
    Start by writing the URL of the website on the sidebar.
"""
)


if url:
    loader = AsyncChromiumLoader(
        urls = [url], 
        user_agent='Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36',
    )
    docs = loader.load() # urls 의 HTML 페이지들을 load 하여 List[Document] 로 리턴
    # st.write(docs) # 확인용

    transformed = html2text_transformer.transform_documents(docs)  # -> Sequence[Document] 리턴
    st.write(transformed)  # 확인용



