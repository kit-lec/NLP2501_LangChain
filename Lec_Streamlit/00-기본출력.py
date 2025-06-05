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

# Chart elements
#  그래프, 차트 그리기
#  https://docs.streamlit.io/develop/api-reference/charts


import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# 한글폰트 설정
from matplotlib import font_manager, rc
import platform
try : 
    if platform.system() == 'Windows':
    # 윈도우인 경우
        font_name = font_manager.FontProperties(fname="c:/Windows/Fonts/malgun.ttf").get_name()
        rc('font', family=font_name)
    else:    
    # Mac 인 경우
        rc('font', family='AppleGothic')
except : 
    pass
plt.rcParams['axes.unicode_minus'] = False   

st.title('Chart 그리기')

# -------------------------------------------------
# st.dataframe()
# DataFrame 을 interactive table 로 그린다.
data = pd.DataFrame({
    '이름': ['영식', '철수', '영희'],
    '나이': [22, 31, 25],
    '몸무게': [75.5, 80.2, 55.1]
})

st.dataframe(data, use_container_width=True)

# -------------------------------------------------
# st.pyplot(figure)
#  matplotlib.pyplot.fiture 를 그린다.
#  시각화 라이브러리로 matplotlib 이나 seaborn 을 사용하게 될텐데.
#  이 경우 pyplot() 을 사용하여 그리면 된다.
fig, ax = plt.subplots()
ax.bar(data['이름'], data['나이'])
st.pyplot(fig)

barplot = sns.barplot(x='이름', y='나이', hue='이름', data=data, 
            ax=ax, palette='Set2', legend=False)

fig = barplot.get_figure()

st.pyplot(fig)

#############
# matplotlit 의 gallery 에 많은 예제들 
# https://matplotlib.org/stable/gallery/index.html
# 

# 그 중에 하나 예시를 가져와보자.
# Stacked bar chart 
# https://matplotlib.org/stable/gallery/lines_bars_and_markers/bar_stacked.html#sphx-glr-gallery-lines-bars-and-markers-bar-stacked-py

species = (
    "Adelie\n $\\mu=$3700.66g",
    "Chinstrap\n $\\mu=$3733.09g",
    "Gentoo\n $\\mu=5076.02g$",
)
weight_counts = {
    "Below": np.array([70, 31, 58]),
    "Above": np.array([82, 37, 66]),
}
width = 0.5

fig, ax = plt.subplots()
bottom = np.zeros(3)

for boolean, weight_count in weight_counts.items():
    p = ax.bar(species, weight_count, width, label=boolean, bottom=bottom)
    bottom += weight_count

ax.set_title("Number of penguins with above average body mass")
ax.legend(loc="upper right")

st.pyplot(fig)

##### Barcode 생성예제
# https://matplotlib.org/stable/gallery/images_contours_and_fields/barcode_demo.html


code = np.array([
    1, 0, 1, 0, 1, 1, 1, 0, 1, 1, 0, 0, 0, 1, 0, 0, 1, 0, 1, 0, 0, 1, 1, 1,
    0, 0, 0, 1, 0, 1, 1, 0, 0, 0, 0, 1, 0, 1, 0, 0, 1, 1, 0, 0, 1, 0, 1, 0,
    1, 0, 1, 0, 0, 0, 0, 1, 0, 1, 1, 1, 0, 1, 0, 0, 1, 1, 0, 1, 1, 0, 0, 1,
    1, 0, 0, 1, 1, 0, 1, 0, 1, 1, 1, 0, 0, 1, 0, 0, 0, 1, 0, 0, 1, 0, 1])

pixel_per_bar = 4
dpi = 100

fig = plt.figure(figsize=(len(code) * pixel_per_bar / dpi, 2), dpi=dpi)
ax = fig.add_axes([0, 0, 1, 1])  # span the whole figure
ax.set_axis_off()
ax.imshow(code.reshape(1, -1), cmap='binary', aspect='auto',
          interpolation='nearest')

st.pyplot(fig)

