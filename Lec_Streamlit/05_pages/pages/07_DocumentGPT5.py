import streamlit as st
import time

st.set_page_config(
    page_title="DocumentGPT5",
    page_icon="👀",
)

st.title("Document GPT5")

if 'messages' not in st.session_state:
    st.session_state['messages'] = [] 

# st.write(st.session_state['messages'])

message = st.chat_input(placeholder="Send a message to AI")

def send_message(message, role, save=True):
    with st.chat_message(role):
        st.write(message)
    if save:
        st.session_state['messages'].append({'message': message, 'role': role})
    
for msg in st.session_state['messages']:
    send_message(msg['message'], msg['role'], save=False)

if message:
    send_message(message, 'human')
    time.sleep(2)
    send_message(f'You said: {message}', 'ai')


    # session_state 에 있는 내용을 sidebar 에 그려보자
    with st.sidebar:
        st.write(st.session_state)
