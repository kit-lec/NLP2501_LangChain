import streamlit as st

st.set_page_config(
    page_title="DocumentGPT",
    page_icon="👀",
)


st.title("DocumentGPT")

# chat_message()  : chat message container 생성
#             human 혹은 AI 모두에게서 받을수 있다.
#     매개변수는 'user', 'assistant', 'ai', 'human' 중 하나

with st.chat_message(name='human'):
    st.write('Hellooooooo')

with st.chat_message(name='ai'):
    st.write('How are you?')

st.chat_input(placeholder="Send a message to AI")

import time
with st.status("Embedding file...", expanded=True) as status:
    time.sleep(3)
    st.write("Getting the file")
    time.sleep(3)
    st.write("Embedding the file")
    time.sleep(3)
    st.write("Caching the file")

    status.update(label="Error", state="error")








