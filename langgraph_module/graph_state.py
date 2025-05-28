from typing import Annotated, Sequence, TypedDict
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages
import operator
import socketio
import logging
import openai

class AgentState(TypedDict):
    """
    messages : input query 부터 과정중에 생성한 텍스트
    status : cypher 쿼리 실행 결과 상태
    sid : socket session id
    sio : socketio.AsyncServer 인스턴스
    server_logger : 서버 로깅을 위한 logger 인스턴스
    time_logger : 시간 측정을 위한 logger 인스턴스
    model_client : LLM 클라이언트 인스턴스
    model_name : LLM 모델 이름
    """
    messages : Annotated[Sequence[BaseMessage], add_messages]
    status : Annotated[Sequence[str], operator.add]
    sid : str
    sio : socketio.AsyncServer
    server_logger : logging.Logger
    time_logger : logging.Logger
    model_client : openai.OpenAI
    model_name : str