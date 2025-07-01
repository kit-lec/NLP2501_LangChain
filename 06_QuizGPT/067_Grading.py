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
import json
from langchain_core.output_parsers.base import BaseOutputParser

import streamlit as st

# ────────────────────────────────────────
# 🎃 LLM 로직
# ────────────────────────────────────────

class JsonOutputParser(BaseOutputParser):
    # text <- LLM 의 호출결과가 전달될거다
    def parse(self, text):  
        # 앞, 뒤의 문자열 제거
        text = text.replace("```", "").replace("json", "")
        # 파이썬 객체 <- JSON
        return json.loads(text)

output_parser = JsonOutputParser()

llm = ChatOpenAI(
    temperature=0.1,
    model='gpt-3.5-turbo-1106',
    streaming=True,
    callbacks=[StreamingStdOutCallbackHandler()],
)


def format_docs(docs):
    return "\n\n".join(document.page_content for document in docs)

question_prompt = ChatPromptTemplate.from_messages([
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
question_chain = {"context": format_docs} | question_prompt | llm

# 만들어진 퀴즈 문제를 받아서 json 처럼 format 해줄 system prompt 를 만들자.
# 그렇게 함으로 파이썬에서 더욱 빠르게 처리해서 UI를 씌우기 간편해질거다.

formatting_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
    You are a powerful formatting algorithm.
     
    You format exam questions into JSON format.
    Answers with (o) are the correct ones.
     
    Example Input:

    Question: What is the color of the ocean?
    Answers: Red|Yellow|Green|Blue(o)
         
    Question: What is the capital or Georgia?
    Answers: Baku|Tbilisi(o)|Manila|Beirut
         
    Question: When was Avatar released?
    Answers: 2007|2001|2009(o)|1998
         
    Question: Who was Julius Caesar?
    Answers: A Roman Emperor(o)|Painter|Actor|Model
   
     
    Example Output:
     
    ```json
    {{ "questions": [
            {{
                "question": "What is the color of the ocean?",
                "answers": [
                        {{
                            "answer": "Red",
                            "correct": false
                        }},
                        {{
                            "answer": "Yellow",
                            "correct": false
                        }},
                        {{
                            "answer": "Green",
                            "correct": false
                        }},
                        {{
                            "answer": "Blue",
                            "correct": true
                        }},
                ]
            }},
            {{
                "question": "What is the capital or Georgia?",
                "answers": [
                        {{
                            "answer": "Baku",
                            "correct": false
                        }},
                        {{
                            "answer": "Tbilisi",
                            "correct": true
                        }},
                        {{
                            "answer": "Manila",
                            "correct": false
                        }},
                        {{
                            "answer": "Beirut",
                            "correct": false
                        }},
                ]
            }},
            {{
                "question": "When was Avatar released?",
                "answers": [
                        {{
                            "answer": "2007",
                            "correct": false
                        }},
                        {{
                            "answer": "2001",
                            "correct": false
                        }},
                        {{
                            "answer": "2009",
                            "correct": true
                        }},
                        {{
                            "answer": "1998",
                            "correct": false
                        }},
                ]
            }},
            {{
                "question": "Who was Julius Caesar?",
                "answers": [
                        {{
                            "answer": "A Roman Emperor",
                            "correct": true
                        }},
                        {{
                            "answer": "Painter",
                            "correct": false
                        }},
                        {{
                            "answer": "Actor",
                            "correct": false
                        }},
                        {{
                            "answer": "Model",
                            "correct": false
                        }},
                ]
            }}
        ]
     }}
    ```
    Your turn!

    Questions: {context}


            """,
        )
    ]
)

formatting_chain = formatting_prompt | llm


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

@st.cache_resource(show_spinner="Making Quiz...")
def run_quiz_chain(_docs, topic):
    chain = {"context": question_chain} | formatting_chain | output_parser
    return chain.invoke(_docs)

@st.cache_resource(show_spinner="Searching Wikipedia...")
def wiki_search(term):
    retriever = WikipediaRetriever(top_k_results=5)
    docs = retriever.invoke(term)    
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
    topic = None 

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
            docs = wiki_search(topic)


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

    response = run_quiz_chain(docs, topic if topic else file.name)

    # form 작성
    #   key= : 페이지 내의 form 식별자.
    with st.form(key="questions_form"):
        for question in response['questions']:
            # 일단 질문만 출력
            st.write(question['question'])
            # 사지선다 항목 출력
            value = st.radio(label="Select an option", 
                     options=[answer['answer'] for answer in question['answers']],
                     index=None)  # 디폴트 체크 제거
            
            # st.write(value) # 확인용
            # st.success(value)  # alert 표시 확인용
            # st.error(value)

            # answer 들을 출력해보자
            # st.json(question['answers'])  # object -> JSON 출력
            # st.json({"answer": value, "correct": True,})

            # 정답 판정
            # st.write({"answer": value, "correct": True,} in question['answers'])

            if {"answer": value, "correct": True,} in question['answers']:
                st.success("Correct!")
            elif value is not None:
                st.error("Wrong!")

        # form '안' 에 submit 버튼이 필요하다
        button = st.form_submit_button()
        










