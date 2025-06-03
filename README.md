# neo4j-graphrag

neo4j와postgresql을 통해 질의에 적합한 자료를 찾고 llm을 통한 응답 및 답변에 참고한 자료를 출력하는 코드

## 프로젝트 구조

```
.
├── langgraph_module/
│   ├── db_module/              # DB 연결 및 처리 모듈
│   │   ├── __init__.py         # db_module 초기화
│   │   ├── neo4j.py            # Neo4j 관련 기능
│   │   └── postgresql.py       # PostgreSQL 관련 기능
│   ├── conditional_edge.py # 조건부 엣지
│   ├── generate_node.py    # llm을 통한 생성하는 노드
│   ├── graph_state.py      # langgraph AgentState 정의
│   ├── retrieve_node.py    # neo4j, postgresql 조회 노드
│   └── workflow.py         # langgraph compile 
│   ├── log/                # log 파일 저장 폴더
│   ├── config.yaml         # 환경 설정 파일
│   ├── config_loader.py        # config.yaml 로드 모듈
│   ├── logger_setup.py         # logger 설정 모듈
│   ├── prompt_template.py      # 프롬프트 템플릿 정의
│   └── socket_server.py        # 소켓 서버 실행
```
## Workflow
![image](https://github.com/user-attachments/assets/c81107a4-e721-4ffa-a051-b8174a536b3f)

1. **사용자 질의 영문번역**
  - 데이터가 영문이기에 사용자 질의를 영문으로 번역(sLLM 활용으로 언어 혼동을 통한 성능저하 방지) 
2. **Cypher query 생성**
  - 주어진 질의를 통해 neo4j에 관련 데이터를 조회할 cypher query를 llm을 통해 생성
3. **neo4j 조회**
  - 생성된 cypher query를 통해 neo4j에 데이터 조회  
4. **neo4j 조회 결과 검증**
  - 조회된 값이 없거나, 에러 발생 등의 상황에 대한 처리
    - 정상적으로 조회가 된다면 해당 데이터를 통해 답변 생성으로 이동
    - 조회 결과에 문제가 있다면 벡터 검색으로 이동
5. **벡터 검색**
  - 주어진 질의를 임베딩해 cos similarity로 top-k개의 데이터를 검색
6. **답변 생성**
  - 먼저 검색된 데이터 k개를 socket을 통해 응답
  - 이후 생성되는 답변을 streaming 처리해 응답 
