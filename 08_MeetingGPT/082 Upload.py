import os
import time

print(f'✅ {os.path.basename( __file__ )} 실행됨 {time.strftime('%Y-%m-%d %H:%M:%S')}') # 실행파일명, 현재시간출력
print(f'\tOPENAI_API_KEY={os.getenv("OPENAI_API_KEY")[:20]}...') # OPENAI_API_KEY 필요!
#─────────────────────────────────────────────────────────────────────────────────────────
import streamlit as st
import subprocess
import math
from pydub import AudioSegment
import glob
import openai

from langchain_openai.chat_models.base import ChatOpenAI
from langchain_core.prompts.chat import ChatPromptTemplate
from langchain_community.document_loaders.text import TextLoader
from langchain_text_splitters.character import RecursiveCharacterTextSplitter

from langchain_community.vectorstores.faiss import FAISS
from langchain.embeddings.cache import CacheBackedEmbeddings
from langchain_openai.embeddings.base import OpenAIEmbeddings
from langchain.storage.file_system import LocalFileStore

file_dir = os.path.dirname(os.path.realpath(__file__)) # *.py 파일의 '경로'만
# ./cache  ← 업로드한 비디오 와 변환한 mp3
# ./cache/chunks ← 분할된 mp3 파일들 저장
upload_dir = os.path.join(file_dir, '.cache/chunks')
if not os.path.exists(upload_dir):
    os.makedirs(upload_dir)

# 🐕‍🦺학습용: transcript 한번했으면 중복해서 실행하지 않기
has_transcript = os.path.exists(os.path.join(file_dir, r'.cache/podcast.txt'))    

# 오디오 추출함수
# 업로드한 video(mp4)에서 오디오(mp3) 추출하여 동일 경로에 저장.
@st.cache_resource()
def extract_audio_from_video(video_path):    
    if has_transcript: return   # 🐕‍🦺학습용    
    audio_path = video_path.replace("mp4", "mp3")  
    command = [
        "ffmpeg",
        "-i",
        video_path,
        "-vn",
        audio_path,
        "-y",  # -y 옵션이 있어야 yes / no 물어볼시 yes 자동선택하고 넘어가게 된다.
        ]
    subprocess.run(command)

# audio_path : 원본 오디오 경로
# chunk_size : minute
# chunks_folder: chunk 들을 저장할 폴더
@st.cache_resource()
def cut_audio_in_chunks(audio_path, chunk_size, chunks_folder):
    if has_transcript: return   # 🐕‍🦺학습용      
    track = AudioSegment.from_mp3(audio_path)
    chunk_len = chunk_size * 60 * 1000
    chunks = math.ceil(len(track) / chunk_len)
    for i in range(chunks):
        start_time = i * chunk_len
        end_time = (i + 1) * chunk_len

        chunk = track[start_time:end_time]

        exp_path = os.path.join(chunks_folder, f"chunk_{i}.mp3")
        chunk.export(exp_path, format="mp3")


# chunk_folder :
# destination : 녹취록이 들어간 텍스트 파일이 저장될 디렉토리
@st.cache_resource()
def transcribe_chunks(chunk_folder, destination):
    if has_transcript: return   # 🐕‍🦺학습용      
    files = glob.glob(os.path.join(chunk_folder, "chunk*.mp3"))
    files.sort()
    for file in files:
        with open(file, "rb") as audio_file, open(destination, "a") as text_file:# append mode
            print(file, '녹취록 가져오는중...', end='')
            # 각 chunk 별로 녹취록 작성.
            transcript = openai.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                language="en"
            )
           
            text_file.write(transcript.text) # 곧바로 텍스트 파일에 저장


# ────────────────────────────────────────
# ⭕ Streamlit 로직
# ────────────────────────────────────────
st.set_page_config(
    page_title="MeetingGPT",
    page_icon="🎤",
)
st.markdown(
    """
# MeetingGPT
           
Welcome to MeetingGPT, upload a video and I will give you a transcript, a summary and a chat bot to ask any questions about it.

Get started by uploading a video file in the sidebar.
"""
)

with st.sidebar:
    video = st.file_uploader(
        label="Video",
        type=["mp4", "avi", "mkv", "mov"],
    )

if video:
    with st.status("Loading video..."):
        # 업로드한 video  파일 저장
        video_content = video.read()
        video_path = os.path.join(file_dir, rf'.cache/{video.name}')
        audio_path = video_path.replace('mp4', 'mp3')
        with open(video_path, 'wb') as f:
            f.write(video_content)

    with st.status("Extracting audio..."):
        # 저장된 video 파일 -> mp3 오디오 파일로 변환저장
        extract_audio_from_video(video_path)

    # mp3 오디오 파일 잘라내기
    chunks_folder = os.path.join(file_dir, r'.cache/chunks')
    with st.status("Cutting audio segments..."):
        cut_audio_in_chunks(audio_path, 10, chunks_folder)

    # 녹취록 파일 생성
    transcript_path = video_path.replace('mp4', 'txt')
    with st.status("Transcribing Audio"):
        transcribe_chunks(chunks_folder, transcript_path)





















