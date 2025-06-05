import streamlit as st
import time

st.set_page_config(
    page_title="DocumentGPT3",
    page_icon="👀",
)

st.title("Document GPT3")

messages = []  # list 로 message 들을 담아 나아가면 되지 않나?

message = st.chat_input(placeholder="Send a message to AI")

def send_message(message, role):
    with st.chat_message(role):
        st.write(message)
        messages.append({'message': message, 'role': role})
    
    st.write(messages)

if message:
    send_message(message, 'human')
    time.sleep(2)
    send_message(f'You said: {message}', 'ai')

# <확인>
# message 를 입력하면,  추가 되는것이 아니라, update 가 된다..

# 사용자가 무엇을 입력해도 비워지지 않고 남아있어야 한다!  어케 하나?
# 코드가 다시 실행되더라도 말이다.

# refresh 되더라도 상태값을 기억하도록
# streamlit 에서는 session state 제공.

# session state 는 여러번 재실행해도 data 가 보존될수 있도록 해준다.