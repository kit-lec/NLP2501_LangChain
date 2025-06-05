print('✅ 실행됨')

import os
import requests
from dotenv import load_dotenv
import json
import configparser
import streamlit as st

print(f'✅ {os.path.basename( __file__ )} 실행됨')
load_dotenv()  #
print(f'\tCLOVASTUDIO_TEST_API_KEY={os.getenv("CLOVASTUDIO_TEST_API_KEY")[:20]}')

api_key = os.getenv("CLOVASTUDIO_TEST_API_KEY")

class CompletionExecutor:
    def __init__(self, host, api_key, request_id):
        self._host = host
        self._api_key = api_key
        self._request_id = request_id

    def execute(self, completion_request):
        headers = {
            'Authorization': self._api_key,
            'X-NCP-CLOVASTUDIO-REQUEST-ID': self._request_id,
            'Content-Type': 'application/json; charset=utf-8',
            'Accept': 'text/event-stream'
        }

        with requests.post(self._host + '/testapp/v3/chat-completions/HCX-005',
                           headers=headers, json=completion_request, stream=True) as r:
            
            # 응답이 id > event > data > id > event > data ... 
            
            event_type = ""
            for line in r.iter_lines():
                if line:
                    decoded_line = line.decode("utf-8")
                    print('🧡', decoded_line)

                    if decoded_line.startswith('event'):
                        event_type = decoded_line.split(":")[1]
                    elif event_type.startswith('result') and decoded_line.startswith('data'):
                        result_answer = json.loads(decoded_line[len("data:"):])['message']['content']
        
        return result_answer


st.title('MBTI 대백과사전')
question = st.text_input(
    '질문',
    placeholder='질문을 입력해 주세요',
)


if question:
    completion_executor = CompletionExecutor(
        host='https://clovastudio.stream.ntruss.com',
        api_key=f'Bearer {api_key}',
        request_id='6dd87e139db746a1bc5988d577c0ea21'
    )

    preset_text = [{"role":"system","content":"- MBTI에 대한 지식을 기반으로, MBTI 질문에 답해보세요.\n- 예제의 형식을 참고하여 질문에 대한 답을 간단히 하세요.\n\n질문: ESFJ는 문제에 봉착했을때 어떻게 대응하는가?\n답: 현실적인 해결 방법을 찾기 위해 노력합니다.\n###\n질문: ISFJ는 연인에게 어떻게 대하는 편인가?\n답: 섬세하고 다정하게 케어해주는 편입니다.\n####\n질문: INTP는 사람들이 많은 곳에 가면 어떻게 행동하는가?\n답: 주변의 상황을 파악하기 위해 관찰하는 편입니다.\n###\n질문: ESFJ는 충동적인 선택을 많이 하는 편인가?\n답: 아니다. 계획적으로 움직이는 편입니다."},{"role":"user","content":"ESTP는 학업에 어떤 자세로 임하는가?\n"},{"role":"assistant","content":"즉각적이고 실용적인 방식으로 접근하며, 이론보다는 경험을 중시해 직접 참여하면서 배우는 것을 선호합니다. 또한, 새로운 도전을 즐기고 위험을 감수하는 경향이 있어 실험적이거나 활동적인 학습 방식을 좋아할 수 있습니다. 다만 장기적인 목표 설정이나 계획 수립에는 약점이 있을 수 있으므로 이를 보완하려는 노력이 필요합니다."},{"role":"user","content":"ENFP 의 성격은 어떻습니까?"},{"role":"assistant","content":"ENFP의 성격은 다음과 같습니다.\n\n1. 창의적이고 호기심이 많습니다.\n2. 개방적이고 융통성이 있으며 적응력이 뛰어납니다.\n3. 열정적이며 활기차고 에너지가 넘칩니다.\n4. 타인의 감정을 잘 이해하며 공감능력이 좋습니다.\n5. 즉흥적이고 자유로운 영혼으로 모험심이 강합니다.\n6. 이상주의적 성향이 강해 자신의 가치관과 신념에 따라 행동합니다.\n7. 직관력이 뛰어나며 미래에 대한 통찰력이 있습니다.\n8. 종종 특이한 아이디어나 관점을 제시하기도 합니다.\n9. 인간관계를 중요시 여기며 상대방을 진심으로 대합니다.\n10. 감정 기복이 심하고 변덕스러울 때가 있습니다.\n\n이러한 특징들은 ENFP 유형의 대표적인 경향이지만 개인의 경험과 환경에 따라 차이가 있을 수 있다는 점 유의하시기 바랍니다. 더불어 MBTI 검사는 성격 유형을 완벽하게 나타내지 않으므로 이를 절대화하지 않고 참고용으로만 활용하시는 것이 바람직합니다."},
                   {
                       'role': 'user',
                       'content': f'{question}'
                   }]

    request_data = {
        'messages': preset_text,
        'topP': 0.8,
        'topK': 0,
        'maxTokens': 512,
        'temperature': 0.5,
        'repetitionPenalty': 1.1,
        'stop': ['###'],
        'includeAiFilters': True,
        'seed': 0
    }

    print('💦', preset_text)
    result_text = completion_executor.execute(request_data)

    st.markdown(result_text)