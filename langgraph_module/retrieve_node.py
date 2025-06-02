import requests
from . import db_module
from datetime import datetime
from langchain_core.messages import AIMessage
from prompt_template import SEARCH_RESULT
from collections import defaultdict
from config_loader import CONFIG

REFERENCE_DATA_CNT = CONFIG["REFERENCE_DATA_CNT"]
# postgresql
conn = db_module.get_postgres_connection(
    CONFIG["postgresql"]["host"],
    CONFIG["postgresql"]["database"],
    CONFIG["postgresql"]["user"],
    CONFIG["postgresql"]["password"],
    CONFIG["postgresql"]["port"]
)
# neo4j
driver = db_module.get_neo4j_driver(
    CONFIG["neo4j"]["uri"],
    auth=(CONFIG["neo4j"]["user"], CONFIG["neo4j"]["password"])
)

async def graph_search(state):
    """
    cypher_agent가 생성한 cypher 쿼리를 실행, 검색된 결과로 Reference Data를 생성

    Args:
        state (dict): langgraph의 state
    
    Returns:
        dict: 답변을 위한 Reference Data
    """
    graph_search_time = datetime.now()
    last_message = state["messages"][-1].content

    try:
        records, summary, _ = driver.execute_query(
            f"{last_message}",
            database_="neo4j"
        )
    except Exception as e:
        state["time_logger"].info(f"[{state['sid']}]-2_e.graph search time : {datetime.now() - graph_search_time}")
        return {"messages" : [AIMessage(str(e))], "status" : ["02000"]}

    status_code = summary.gql_status_objects[0].gql_status
    # 상태 코드 확인 조회 결과 없음
    if status_code[:2] == "02":
        state["time_logger"].info(f"[{state['sid']}]-2_e.graph search time : {datetime.now() - graph_search_time}")
        return {"messages" : [AIMessage("No results found. Change the WHERE clause.")], "status" : [str(status_code)]}
    # neo4j return 타입이 다른 경우
    if not isinstance(records[0][0], str) or not isinstance(records[0][1], str): 
        state["time_logger"].info(f"[{state['sid']}]-2_e.graph search time : {datetime.now() - graph_search_time}")
        return {"messages" : [AIMessage("The return type does not match.")], "status" : ["02000"]}

    ut_list = []
    for record in records:
        ut_list.append(f"'{record[1]}'")

    with conn.cursor() as cur:
        cur.execute(f"""
            SELECT B.title, B.abstract, A.social_issue, A.solution, A.rel_solve, A.rel_cause, B.doi 
            FROM wos_ent as A INNER JOIN wos_meta as B on A.uid = B.uid
            WHERE A.uid in ({",".join(ut_list)})
            """)
        rows = cur.fetchall()

    index = 1
    result_dict = defaultdict(list)
    result_dict["ut_list"] = ut_list
    str_list = []
    for row in rows:
        if len(str_list) >= REFERENCE_DATA_CNT: break
        if not records[0][0] in [r for r in row[2]]: continue

        str_relation = []
        if row[4]:
            for r in row[4] : str_relation.append(f"'{r[1]}' can be solved by '{r[0]}'")
        if row[5]:
            for r in row[5] : str_relation.append(f"'{r[1]}' is caused by '{r[0]}'")

        str_format = SEARCH_RESULT.format(
            number = str(index),
            title = row[0],
            abstract = row[1],
            social_issue = ",".join([f"'{r}'" for r in row[2]]),
            solution = ",".join([f"'{r}'" for r in row[3]]),
            relations = "\n".join(str_relation)
        )
        str_list.append(str_format)
        result_dict["reference"] += [{"number": str(index), "title": row[0], "abstract": row[1], "doi": row[6]}]
        index += 1
    result_dict["pp_data"] = [{"title": r[0], "abstract": r[1], "social_issue": r[2],
                            "solution": r[3], "rel_solve": r[4], "rel_cause": r[5], "doi": r[6]} for r in rows]  

    if not str_list : return {"messages" : [AIMessage("Change the target node of n.entity in the WHERE clause.")], "status" : ["02000"]}
    
    # 화면에서 참조 데이터 표시를 위해 socket.io를 통해 전송
    await state["sio"].emit("reference_data", result_dict, to=state['sid'])

    state["time_logger"].info(f"[{state['sid']}]-2_1.graph search time : {datetime.now() - graph_search_time}")
    return {"messages" : [AIMessage("\n".join(str_list))], "status" : [str(status_code)]}

async def vector_search(state):
    """
    neo4j vector search와 postgresql에서 검색된 결과로 Reference Data를 생성

    Args:
        state (dict): langgraph의 state
    
    Returns:
        dict: 답변을 위한 Reference Data
    """
    vector_search_time = datetime.now()
    first_message = state["messages"][0].content

    # 임베딩 요청
    response = requests.post(
        "http://192.168.2.105:9001/embed",
        headers={"Content-Type": "application/json"},
        json={"text": first_message}
    )
    if response.status_code == 200:
        embedding = response.json()["embedding"]
    else:
        raise Exception(f"Failed to get embedding: {response.text}")

    query = """
    WITH $vector AS queryVector
    CALL db.index.vector.queryNodes('paper_embedding_index', 1000, queryVector)
    YIELD node AS paper
    RETURN paper.uid
    """
    records, _, _ = driver.execute_query(
        query,
        database_="neo4j",
        parameters_={"vector": embedding}
    )

    ut_list = []
    for record in records:
        uid = record[0]
        ut_list.append(f"'{uid}'")

    with conn.cursor() as cur:
        cur.execute(f"""
            SELECT B.title, B.abstract, A.social_issue, A.solution, A.rel_solve, A.rel_cause, B.doi 
            FROM wos_ent as A INNER JOIN wos_meta as B on A.uid = B.uid
            WHERE A.uid in ({",".join(ut_list)})
            """)
        rows = cur.fetchall()

    result_dict = defaultdict(list)
    result_dict["ut_list"] = ut_list
    str_list = []
    for i, row in enumerate(rows[:REFERENCE_DATA_CNT]):
        str_relation = []
        if row[4]:
            for r in row[4] : str_relation.append(f"'{r[1]}' can be solved by '{r[0]}'")
        if row[5]:
            for r in row[5] : str_relation.append(f"'{r[1]}' is caused by '{r[0]}'")

        str_format = SEARCH_RESULT.format(
            number = str(i+1),
            title = row[0],
            abstract = row[1],
            social_issue = ",".join([f"'{r}'" for r in row[2]]),
            solution = ",".join([f"'{r}'" for r in row[3]]),
            relations = "\n".join(str_relation)
        )
        str_list.append(str_format)
        result_dict["reference"] += [{"number": str(i+1), "title": row[0], "abstract": row[1], "doi": row[6]}]
    result_dict["pp_data"] = [{"title": r[0], "abstract": r[1], "social_issue": r[2],
                               "solution": r[3], "rel_solve": r[4], "rel_cause": r[5], "doi": r[6]} for r in rows]    
    
    # 화면에서 참조 데이터 표시를 위해 socket.io를 통해 전송
    await state["sio"].emit("reference_data", result_dict, to=state["sid"])
    state["time_logger"].info(f"[{state['sid']}]-2_2.vector search time : {datetime.now() - vector_search_time}")
    
    return {"messages" : [AIMessage("\n".join(str_list))]}