import streamlit as st

st.set_page_config(
    page_title= "GPT Home",  # 페이지 타이틀 설정
    page_icon="😎",  # 페이지 아이콘 (적절한 이모지로 설정) 브라우저 탭에 표시될거다.

)

st.title("GPT home")

# ./pages 라는 폴더를 만들어야 한다 


# 마크다운 위젯
st.markdown(
    """
### GPT 홈페이지!

- [ ] [DocumentGPT](/DocumentGPT)
- [ ] [PrivateGPT](/PrivateGPT)
- [ ] [DocumentGPT1](/DocumentGPT1)
- [ ] [DocumentGPT2](/DocumentGPT2)
- [ ] [DocumentGPT3](/DocumentGPT3)
- [ ] [DocumentGPT4](/DocumentGPT4)
- [ ] [DocumentGPT5](/DocumentGPT5)
- [ ] [DocumentGPT99](/DocumentGPT99)
"""
)
