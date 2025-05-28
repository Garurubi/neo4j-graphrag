import socketio
import uvicorn
import openai
from datetime import datetime
from logger_setup import setup_logger
from prompt_template import TRANSLATE_ENGLISH
from langchain_core.messages import HumanMessage
from langgraph_module.workflow import app
from config_loader import CONFIG

MODEL_NAME = CONFIG["MODEL_NAME"]

# vllm을 통한 llm 연결
client = openai.Client(
    api_key=CONFIG["openai"]["api_key"], 
    base_url=CONFIG["openai"]["base_url"]
)
# main logger
sever_logger = setup_logger("server")
# time logger
time_logger = setup_logger("time")

async def run_workflow(query:str, sid:str, sio:socketio.AsyncServer) -> None:
    """
    한국어 질의를 영문으로 번역하고, 답변을 스트리밍으로 전송하는 함수

    Args:
        query (str): 한국어 질의
        sid (str): socket session id
        sio (socketio.AsyncServer): socketio 서버 인스턴스
    """
    translate_time = datetime.now()
    prompt = TRANSLATE_ENGLISH.format(korean_query=query)
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        max_tokens=8192
    )
    translate_query = response.choices[0].message.content
    time_logger.info(f"[{sid}]-1.Translate time : {datetime.now() - translate_time}")

    inputs = {
        "messages": [
            HumanMessage(translate_query)
        ],
        "sid" : sid,
        "sio": sio,
        "server_logger" : sever_logger,
        "time_logger" : time_logger,
        "model_client" : client,
        "model_name" : MODEL_NAME
    }

    # langgraph의 ainvoke를 통해 workflow 실행
    result = await app.ainvoke(inputs)

    # langgraph의 ainvoke의 최종 결과를 받아서 LLM에게 답변 요청
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {
                "role": "user",
                "content": result["messages"][-1].content
            }
        ],
        stream=True,
        max_tokens=8192
    )
    time_logger.info(f"[{sid}]-3.time to first token time : {datetime.now() - translate_time}")

    # 스트리밍 응답을 한 줄씩 출력
    for chunk in response:
        await sio.emit("generate_text", {"gen_text": chunk.choices[0].delta.content}, to=sid)

sio = socketio.AsyncServer(async_mode="asgi", cors_allowed_origins="*")
socket = socketio.ASGIApp(sio)

@sio.event
async def connect(sid, environ):
    print(f"Connect: {sid}")

@sio.event
async def disconnect(sid):
    print(f"Disconnect: {sid}")

@sio.event
async def query(sid, query):
    s_query = datetime.now()
    await run_workflow(query, sid, sio)
    await sio.disconnect(sid)
    print(f"[total time : {datetime.now() - s_query}]")

if __name__ == "__main__":
    uvicorn.run(socket, host="172.17.0.2", port=9301)