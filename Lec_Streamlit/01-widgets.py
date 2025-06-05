# Streamlit 의 data flow 와 data 가 처리되는 방식

# Streamlit 에선 'data 가 변경'될때 마다 python 파일 '전체'가 다시 실행된다. (py 파일 위에서부터 아래까지 전부 다시 실행)
# 가령 사용자가 무언가를 입력하거나 slider 를 드래그 해서 data 가 변경될때마다 ..

from datetime import datetime
today = datetime.today().strftime("%H:%M:%S")  # 이 '코드가 실행되는 시점'의 시간이 계산된다.
print(f'✅ 실행됨 {today}')
import streamlit as st

st.title(today)  # 확인해보자, 새로고침도.
# ↓ 브라우저에서 아래의 selectbox 의 내용(data)을 '변경'만 해도 위 시간이 변경된다.  (다시 파이썬 파일이 실행된다!)

model = st.selectbox("Choose LLM model", ("GPT-3-turbo", "GPT-4o"))
st.markdown(f'model: :green[{model}]')

name = st.text_input("What is your name?")
st.markdown(f'name: :green[{name}]')

st.slider(label="temperature", min_value=0.1, max_value=1.0)

if model == "GPT-3-turbo":
    st.write("cheap")
else:
    st.write("expensive")
    country = st.text_input("국적이 뭡니까?")
    st.write(country)

st.markdown("---")

button = st.button('버튼을 눌러보세요') # bool 리턴

if button:
    st.write(':blue[버튼]이 눌렸스빈다 :sparkles:')

agree = st.checkbox('동의하십니까?')
if agree:
    st.write('동의 해주셔서 감사합니다 :100:')

mbti = st.radio(
    label='당신의 MBTI는?',
    options=('ISTJ', 'ENFP', '선택지 없슴')
)

if mbti == 'ISTJ':
    st.write('당신은 :blue[현실주의자] 이시네요')
elif mbti == 'ENFP':
    st.write('당신은 :green[활동가] 이시네요')
else:
    st.write("당신에 대해 :red[알고 싶어요]:grey_exclamation:")

# ---------------------------------------------------
# st.selectbox() => 선택한 option 객체,  혹은 None 리턴
# 선택 박스
mbti = st.selectbox(
    label='당신의 MBTI는 무엇입니까?',
    options=('ISTJ', 'ENFP', '선택지 없음'),
    index=2,
)

if mbti == 'ISTJ':
    st.write('당신은 :blue[현실주의자] 이시네요')
elif mbti == 'ENFP':
    st.write('당신은 :green[활동가] 이시네요')
else:
    st.write("당신에 대해 :red[알고 싶어요]:grey_exclamation:")


options = st.multiselect(  # => list 리턴
    label='당신이 좋아하는z과일은 뭔가요?',
    options=['망고', '오렌지', '사과', '바나나'],
    default=['망고', '오렌지']
)

st.write(f'당신의 선택은: :red[{options}] 입니다.')

values = st.slider(
    label='범위의 값을 다음과 같이 지정할 수 있어요:sparkles:',
    min_value=0.0,
    max_value=100.0,
    value=(25.0, 75.0)
)
st.write('선택 범위:', values)

from datetime import datetime as dt
import datetime

# datetime 을 slider 구간에 사용 가능
start_time = st.slider(
    label="언제 약속을 잡는 것이 좋을까요?",
    min_value=dt(2020, 1, 1, 0, 0), 
    max_value=dt(2020, 1, 7, 23, 0),
    value=dt(2020, 1, 3, 12, 0),
    step=datetime.timedelta(hours=1),  # 한번 움직일때마다 움직이는 양.
    format="MM/DD/YY - HH:mm")
st.write("선택한 약속 시간:", start_time)

# ---------------------------------------------------
# st.text_input => str 리턴
# 텍스트 입력.  (입력후  ENTER 하면 리턴값)
title = st.text_input(
    label='가고 싶은 여행지가 있나요?',
    placeholder="여행지를 입력하세요",

)
st.write(f'당신이 선택한 여행지: :violet[{title}]')


num = st.number_input(
    label='나이를 입력해주세요',
    min_value=10,
    max_value=100,
    value=30,
    step=5,
)
st.write('입력한 나이는: ', num)


# ------------------------------
#  파일 업로드

import time
import pandas as pd

# 파일 업로더 위젯
st.markdown('---')
st.title('파일 업로드:sparkles:')

# ----------------------------------------------
# st.file_uploader() => None | UploadedFile | list of UploadedFile 리턴
# 파일 업로드 버튼 (업로드 기능)

file = st.file_uploader(
    label="파일 선택(csv or excel)",
    type=['csv', 'xls', 'xlsx'],
)

time.sleep(2)

if file is not None:
    ext = file.name.split('.')[-1]  # 확장자 가져오기
    if ext == 'csv':
        df = pd.read_csv(file)
        st.dataframe(df)

    elif 'xls' in ext:   # 'xls' 혹은 'xlsx'
        df = pd.read_excel(file, engine='openpyxl')
        st.dataframe(df)

















