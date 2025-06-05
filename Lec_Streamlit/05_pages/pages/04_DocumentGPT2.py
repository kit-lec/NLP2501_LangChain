import streamlit as st
import time

st.set_page_config(
    page_title="DocumentGPT2",
    page_icon="👀",
)

st.title("Document GPT2")

message = st.chat_input(placeholder="Send a message to AI")

def send_message(message, role):
    with st.chat_message(role):
        st.write(message)

if message:
    send_message(message, 'human')
    time.sleep(2)
    send_message(f'You said: {message}', 'ai')


# message 입력하면 2초뒤에 AI 가 대답하는 듯
# 그러나, 이후 또 message 를 입력하면 기존의 입력된 message 가 replace 된다
# 즉, message 에 대한 history 가 없는 상태다.
#  왜? message  를 입력할때마다 모든 파이썬 코드가 재 실행되기 때문이다.

# 그래서 message 들을 보관하는 일종의 시스템이 있어야 한다.
# 메세지를 추가할때 마다 그 message 를 저장해야 한다.    