# 확인용
# 제대로 import 여부 + version 체크
import sys
print(sys.version)

import streamlit as st
print('streamlit', st.__version__)

import langchain
print('langchain', langchain.__version__)


import langchain_core
print('langchain_core', langchain_core.__version__)

from langchain_core.messages.human import HumanMessage
from langchain_core.messages.system import SystemMessage
from langchain_core.messages.ai import AIMessage

from langchain_core.callbacks.base import BaseCallbackHandler
from langchain_core.callbacks.streaming_stdout import StreamingStdOutCallbackHandler

from langchain_core.prompts.prompt import PromptTemplate
from langchain_core.prompts.chat import ChatPromptTemplate
from langchain_core.prompts.chat import ChatMessagePromptTemplate
from langchain_core.prompts.chat import MessagesPlaceholder

from langchain_core.output_parsers.base import BaseOutputParser
from langchain_core.output_parsers import StrOutputParser

from langchain_core.prompts.few_shot import FewShotPromptTemplate
from langchain_core.prompts.few_shot import FewShotChatMessagePromptTemplate

from langchain_core.example_selectors.length_based import LengthBasedExampleSelector
from langchain_core.example_selectors.base import BaseExampleSelector

from langchain_core.prompts.loading import load_prompt

from langchain_core.prompts.pipeline import PipelinePromptTemplate

from langchain_core.globals import set_llm_cache
from langchain_core.caches import InMemoryCache
from langchain_core.globals import set_debug

from langchain_core.runnables.base import Runnable
from langchain_core.runnables.passthrough import RunnablePassthrough
from langchain_core.runnables.base import RunnableLambda

from langchain_core.tools.base import BaseTool
from langchain_core.tools.simple import Tool
from langchain_core.tools.structured import StructuredTool

# langchain_community
import langchain_community
print("langchain_community", langchain_community.__version__)

from langchain_community.cache import SQLiteCache
from langchain_community.llms.loading import load_llm
from langchain_community.document_loaders.text import TextLoader
from langchain_community.document_loaders.pdf import PyPDFLoader
from langchain_community.document_loaders.unstructured import UnstructuredFileLoader
from langchain_community.document_loaders.chromium import AsyncChromiumLoader
from langchain_community.document_loaders.sitemap import SitemapLoader  # USER_AGENT environment variable not set, consider setting it to identify your requests.
from langchain_community.document_loaders.csv_loader import CSVLoader

from langchain_community.document_transformers.html2text import Html2TextTransformer

from langchain_community.vectorstores.chroma import Chroma
from langchain_community.vectorstores.faiss import FAISS

from langchain_community.retrievers.wikipedia import WikipediaRetriever

from langchain_community.utilities.duckduckgo_search import DuckDuckGoSearchAPIWrapper
from langchain_community.utilities.sql_database import SQLDatabase

from langchain_community.agent_toolkits.sql.base import create_sql_agent
from langchain_community.agent_toolkits.sql.toolkit import SQLDatabaseToolkit

import langchain_unstructured
print("langchain_unstructured", langchain_unstructured.__version__)
from langchain_unstructured import UnstructuredLoader

import langchain_openai
print('langchain_openai', langchain_openai.__all__)
from langchain_openai.chat_models.base import ChatOpenAI
from langchain_openai.llms.base import OpenAI
from langchain_openai.embeddings.base import OpenAIEmbeddings



# lanchain.memory
# 대부분 0.3.1 부터 deprecated 됨. LangGraph 로의 사용을 권하고 있슴.

from langchain.memory.buffer import ConversationBufferMemory
from langchain.memory.buffer_window import ConversationBufferWindowMemory
from langchain.memory.summary import ConversationSummaryMemory
from langchain.memory.summary_buffer import ConversationSummaryBufferMemory
from langchain_community.memory.kg import ConversationKGMemory

from langchain.chains.llm import LLMChain
from langchain.chains.retrieval_qa.base import RetrievalQA

from langchain.embeddings.cache import CacheBackedEmbeddings

from langchain.storage.file_system import LocalFileStore

from langchain_community.llms import GPT4All

from langchain_text_splitters.character import RecursiveCharacterTextSplitter
from langchain_text_splitters.character import CharacterTextSplitter

import langchain_huggingface
print('langchain_huggingface', langchain_huggingface.__all__)
from langchain_huggingface import HuggingFaceEndpoint
from langchain_huggingface import HuggingFacePipeline

import tiktoken
print('tiktoken', tiktoken.__version__)

#
import langchain_ollama
print('langchain_ollama', langchain_ollama.__version__)
from langchain_ollama.chat_models import ChatOllama
from langchain_ollama.embeddings import OllamaEmbeddings


from langchain.agents.initialize import initialize_agent
from langchain.agents.agent_types import AgentType

from langchain_core.tools.simple import Tool
from langchain_core.tools.base import BaseTool

# 12
from pydantic import BaseModel

# 13
import fastapi
print('fastapi', fastapi.__version__)

import pinecone
print('pinecone', pinecone.__version__)
from langchain_pinecone.vectorstores import PineconeVectorStore






