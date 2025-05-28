import openai
from langchain_core.messages import AIMessage
from datetime import datetime
from prompt_template import CYPHER_QUERY, GENERATE_PROMPT

async def cypher_agent(state):
    """
    질의를 통해 llm으로 cypher 쿼리를 생성

    Args:
        state (dict): langgraph의 state
    
    Returns:
        dict: cypher 쿼리
    """
    cypher_agent_time = datetime.now()
    user_input = state["messages"][0].content
    state["server_logger"].info(f"User input: {user_input}")

    prompt = CYPHER_QUERY.format(query=user_input)
    response = state["model_client"].chat.completions.create(
        model=state["model_name"],
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        max_tokens=8192
    )
    gen_text = response.choices[0].message.content
    state["server_logger"].info(f"Cypher query: {gen_text}")

    state["time_logger"].info(f"[{state['sid']}]-2.cypher agent time : {datetime.now() - cypher_agent_time}")
    return {"messages" : [AIMessage(gen_text)]}

def generate_prompt(state):
    """
    검색 결과를 받아 최종 답변을 위한 프롬프트 생성

    Args:
        state (dict): langgraph의 state

    Returns:
        dict: 최종 답변을 위한 프롬프트
    """

    first_message = state["messages"][0].content
    last_message = state["messages"][-1].content
    prompt = GENERATE_PROMPT.format(
        input_query = first_message,
        search_result = last_message
    )
    
    return {"messages" : [AIMessage(prompt)]}

