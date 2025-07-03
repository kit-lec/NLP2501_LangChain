import os
import time

print(f'✅ {os.path.basename( __file__ )} 실행됨 {time.strftime('%Y-%m-%d %H:%M:%S')}') # 실행파일명, 현재시간출력
print(f'\tOPENAI_API_KEY={os.getenv("OPENAI_API_KEY")[:20]}...') # OPENAI_API_KEY 필요!

import streamlit as st
from langchain_community.document_loaders.sitemap import SitemapLoader
from langchain_text_splitters.character import RecursiveCharacterTextSplitter
from langchain_community.vectorstores.faiss import FAISS
from langchain_openai.embeddings.base import OpenAIEmbeddings
from langchain_core.runnables.passthrough import RunnablePassthrough
from langchain_core.runnables.base import RunnableLambda
from langchain_openai.chat_models.base import ChatOpenAI
from langchain_core.prompts.chat import ChatPromptTemplate

llm = ChatOpenAI(
    temperature=0.1
)

answers_prompt = ChatPromptTemplate.from_template("""
    Using ONLY the following context answer the user's question. If you can't just say you don't know, don't make anything up.
                                                 
    Then, give a score to the answer between 0 and 5.

    If the answer answers the user question the score should be high, else it should be low.

    Make sure to always include the answer's score even if it's 0.

    Context: {context}
                                                 
    Examples:
                                                 
    Question: How far away is the moon?
    Answer: The moon is 384,400 km away.
    Score: 5
                                                 
    Question: How far away is the sun?
    Answer: I don't know
    Score: 0
                                                 
    Your turn!

    Question: {question}
""")

def get_answers(inputs):
    docs = inputs['docs']  
    question = inputs['question']

    # 모든 docuemnt 를 각각 처리해 줄 chain 을 만들어 보자
    answers_chain = answers_prompt | llm

    # answers = []
    # for doc in docs:  # 각각의 Document 마다
    #     result = answers_chain.invoke({
    #         'question': question,
    #         'context': doc.page_content,   # 아직은 meta data 는 건네지 않았다.
    #     })
    #     answers.append(result.content)

    # return [
    #     answers_chain.invoke({
    #         'question': question,
    #         'context': doc.page_content,   # 아직은 meta data 는 건네지 않았다.
    #     }).content
    #     for doc in docs
    # ]

    # 이 리턴 값을 다음 chain 에 전달해야 하는데...
    # '어떠한 형식' 으로 전달할지 정의해야 한다.
    
    # 다음과 같은 형식으로 리턴해볼거다    
    # {
    #     answer: from the llm,
    #     source: doc.metadata   <- Document 의 meta data 포함
    #     date: doc.lastmod  <- Document 의 마지막 수정날짜 정보도 필요.
    # }

    # 이 리턴값이 choose_answer() 의 입력으로 전달 
    return {
        "question": question,
        "answers": [
            {
                'answer': answers_chain.invoke({
                    'question': question,
                    'context': doc.page_content,   
                }).content,
                'source': doc.metadata['source'],  # 출처 url
                'date': doc.metadata['lastmod'],   # 마지막 수정일시
            }
            for doc in docs
        ]
    }


choose_prompt = ChatPromptTemplate.from_messages([
    ('system', """
            Use ONLY the following pre-existing answers to answer the user's question.

            Use the answers that have the highest score (more helpful) and favor the most recent ones.

            Cite sources and return the sources as it is. Do not change them. Keep it as a link

            Answers: {answers}
     """),
    ('human', "{question}")
])

    
# 모든 answer 와 사용자 question 을 '입력' 받아
# 선택된 최종 answer '출력'
def choose_answer(inputs):
    answers = inputs['answers']
    question = inputs['question']
    choose_chain = choose_prompt | llm

    # 기존의 answers (List[Dict]) 를 prompt string 으로 만들어서 전달해 주어야 한다.
    condensed = "\n\n".join(
        f"{answer['answer']}\n\nSource:{answer['source']}\n\nDate:{answer['date']}\n"
        for answer in answers
    )

    # st.write(condensed)  # 확인용!

    return choose_chain.invoke({
        "question": question,
        "answers": condensed,
    })

    

# document 전체 HTML 을 가진 Beautiful soup object 값이 전달된다
# 여기서 검색(search) 하거나, HTML element 들을 제거할수 있다.
def parse_page(soup):
    # <header> 와 <footer> 제거
    header = soup.find('header')
    footer = soup.find('footer')

    # decompose()  해당 요소를 HTML 문서에저 제거.
    if header:
        header.decompose()

    if footer:
        footer.decompose()
        
    # <header> 와 <footer> 제거된 나머지 HTML text 리턴
    return (str(soup.get_text())
            # 공백문자, 불필요한 UI 제거(치환)
            .replace(r"\n", " ")
            .replace("\xa0", " ")
            .replace("Try Claude", " ")
            )

@st.cache_resource(show_spinner="Fetching URL...")
def load_website(url):
    splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
        chunk_size=1000,
        chunk_overlap=200,
    )

    loader = SitemapLoader(
        url,
        filter_urls=[            
            r"^(.*\/news\/).*",  
            # r"^(.*\/pricing).*",  
        ],
        parsing_function=parse_page, 
    )
    loader.requests_per_second = 1
    loader.max_depth=1 
    loader.headers = {'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36'}
    docs = loader.load_and_split(text_splitter=splitter)
    vector_store = FAISS.from_documents(
        documents=docs,
        # ★명심. cache 를 만들때..
        #   다른 sitemap 에서 얻은 각각의 URL 마다 별도의 cache를 만들어야 한다
        embedding=OpenAIEmbeddings(),
    )

    return vector_store.as_retriever()

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
    # 사용자가 URL 을 입력하면, 거기에 XML sitemap 이 포함되는지 확인할거다.
    # 포함되지 않다면 error 를 보여줘서 application 의 출돌을 미리 방지하자.
    if ".xml" not in url:
        with st.sidebar:
            st.error("Please write down a Sitemap url")
    
    else:
        retriever = load_website(url)
        query = st.text_input('Ask a question to the website')

        # Map Re-Rank Chain 만들기. 두개의 chain 이 필요하다
        # 1.첫번째 chain
        #   모든 개별 Document 에 대한 답변 생성 및 채점 담당
        # 2.두번째 chain
        #   모든 답변을 가진 마지막 시점에 실행된다
        #   점수가 제일 높고 + 가장 최신 정보를 담고 있는 답변들 고른다       

        # ----------
        # 🟡 첫번째 chain
        #    retreiver 에 의해 리턴된 List[Document] 와 사용자가 입력한 question 필요
        #    이는 chain 의 입력값들이다.

        if query:
            chain = {
                'docs': retriever,
                'question': RunnablePassthrough(),
            } | RunnableLambda(get_answers) | RunnableLambda(choose_answer)

            result = chain.invoke(query)
            st.markdown(result.content.replace("$", "\$"))












