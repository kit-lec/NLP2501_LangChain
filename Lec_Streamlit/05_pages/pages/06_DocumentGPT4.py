import streamlit as st
import time

st.set_page_config(
    page_title="DocumentGPT4",
    page_icon="👀",
)

st.title("Document GPT4")

# session_state 는 여러번 재실행(refresh) 해도 기존 상태값(데이터)가 보존될수 있도록 해준다.
#   보존되는 데이터는 key-value 형태로 session에 저장됨

if 'messages' not in st.session_state:  # session 에 'messages' key 값이 없었다면
    st.session_state['messages'] = []   # 새로 생성

st.write(st.session_state['messages'])  # 확인용.  session 의 messages key 값

message = st.chat_input(placeholder="Send a message to AI")

def send_message(message, role):
    with st.chat_message(role):
        st.write(message)
        st.session_state['messages'].append({'message': message, 'role': role})
    
    # st.write(messages)

if message:
    send_message(message, 'human')
    time.sleep(2)
    send_message(f'You said: {message}', 'ai')
