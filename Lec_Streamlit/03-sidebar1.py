from datetime import datetime
today = datetime.today().strftime("%H:%M:%S")
print(f'✅ 실행됨 {today}')

import streamlit as st

st.title('sidebar')

with st.sidebar:
    st.title('sidebar title')
    st.text_input('xxxx')
    "Hello everyone!"


tab_one, tab_two, tab_three = st.tabs(["One", "Two", "Three"])

with tab_one:
    st.write("alpha")

with tab_two:
    st.write("bravo")

with tab_three:
    st.write("charlie")

col1, col2, col3 = st.columns(3)
col1.metric(label="USD", value='1,458원', delta='-12.00원')
col2.metric(label="일본JPY(100엔)", value="958.63 원", delta="-7.44 원")

with col3:
    st.metric(label="유럽연합EUR", value="1,335.82 원", delta="11.44 원")