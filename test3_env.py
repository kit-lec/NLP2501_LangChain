import os
print(f'✅ {os.path.basename( __file__ )} 실행됨')  # os.path.absname() 은 전체경로

from dotenv import load_dotenv
print(load_dotenv())  # 정상적으로 환경변수 읽어오면 True 리턴.

print('\t', os.getenv('OPENAI_API_KEY')[:20])
print(f'\tLANGCHAIN_API_KEY={os.getenv('LANGCHAIN_API_KEY')[:20]}...')
