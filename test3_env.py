import os
print(f'✅ {os.path.basename( __file__ )} 실행됨')  # os.path.absname() 은 전체경로

print('\t', os.getenv('OPEN_API_KEY')[:20])
