def check_cypher_query(state):
    """
    cypher query가 정상적으로 실행이 되었는지 검증
    정상이면 generate 호출
    Error가 발생되면 vector_search 호출

    Args:
        state (dict): langgraph의 state

    Returns:
        str: 'success' or 'error'
    """

    last_status = state["status"][-1][:2]

    if last_status == "02" :
        return "error"
    else :
        return "success"