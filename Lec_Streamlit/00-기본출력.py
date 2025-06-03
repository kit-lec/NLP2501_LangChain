import streamlit as st
import numpy as np
import pandas as pd

import os
from dotenv import load_dotenv

print(f'✅ {os.path.basename( __file__ )} 실행됨')
load_dotenv()  #
print(f'\tOPENAI_API_KEY={os.getenv("OPENAI_API_KEY")[:20]}')

# 서버 실행
# > streamlit run ******.py
#    ※ 초반에 email 물어보면 걍 엔터 치세요.

# 서버 종료
# 터미널창에서 user break (CTRL + C) 연타
# user break 되지 않으면 terminal 종료(kill) 하세요

st.title("기본 출력")

# 특수 이모티콘 삽입 예시
# emoji: https://streamlit-emoji-shortcodes-streamlit-app-gwckff.streamlit.app/
st.title('스마일 :sunglasses:')

st.header('헤더 입력 :sparkles:')

st.subheader('이것은 subheader 입니다')

st.caption('캡션입니다')

# 코드 표시
sample_code = '''
def function():
    print('hello, world')
'''
st.code(sample_code, language='python')

st.text('일반적인 텍스트 출력')

st.markdown('streamlit 은 **마크다운 문법 지원** 합니다')
st.markdown('텍스트 색상을 :green[초록색], :blue[파란색] 설정가능.')
st.markdown(r':green[$\sqrt{x^2+y^2}=1$] :pencil:')

# <hr> 같은 가로선 그리기
st.markdown("---")

st.title("Dataframe, Metric")

# DataFrame 생성
dataframe = pd.DataFrame({
    'first column': [1, 2, 3, 4],
    'second column': [10, 20, 30, 40],
})

# DataFrame
st.dataframe(dataframe, use_container_width=True)

# table
st.table(dataframe)

st.metric(label="온도", value="10°C", delta="1.2°C")
st.metric(label="삼성전자", value="61,000 원", delta="-1,200 원")

st.markdown('---')

st.write('hello')
st.write([1, 2, 3, 4])
st.write({'x': 100})

import re

st.write(re.Pattern)


# Streamlit 의 magic!

re.Match

[100, 200, 300, 400]

{'name': "John", 'age': 34}