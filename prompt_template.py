# 프롬프트 템플릿 정의
CYPHER_QUERY = """Task: Generate a Cypher statement for querying a Neo4j graph database from reference properties.
Schema:
Node properties:
Social {{entity: STRING}}
Solution {{entity: STRING}}
Paper {{uid: STRING}}

The relationships:
(:Social)-[:Cause]->(:Social)
(:Solution)-[:Solve]->(:Social)
(:Social)-[:Reference]->(:Paper)
(:Solution)-[:Reference]->(:Paper)

Examples (optional):
examples = [
    "USER INPUT: 'What are the solutions to the social issue of water pollution?' QUERY: MATCH (a:Social)<-[:Solve]-(b:Solution)-[:Reference]->(c:Paper) WHERE a.entity = 'water pollution' RETURN a.entity, c.uid",
    "USER INPUT: 'What social issues are caused by cancer?' QUERY: MATCH (a:Social)-[:Cause]->(b:Social)-[:Reference]->(c:Paper) WHERE a.entity = 'cancer' RETURN a.entity, c.uid",
    "USER INPUT: 'What are the causes of climate change?' QUERY: MATCH (a:Social)<-[:Cause]-(b:Social)-[:Reference]->(c:Paper) WHERE a.entity = 'climate change' RETURN a.entity, c.uid",
    "USER INPUT: 'How can we solve the problem of income inequality?' QUERY: MATCH (a:Social)<-[:Solve]-(b:Solution)-[:Reference]->(c:Paper) WHERE a.entity = 'income inequality' RETURN a.entity, c.uid"
]

Input:
{query}

Do not use any properties or relationships not included in the schema.
Do not include triple backticks ``` or any additional text except the generated Cypher statement in your response.

Cypher query:
"""

SEARCH_RESULT = """### Paper {number}:
- **Title**: {title}
- **Abstract**: {abstract}

### Identified Entities:
- **Social Issue**: {social_issue}
- **Solution**: {solution}

### Relationships:
{relations}
-----
"""

GENERATE_PROMPT = """Instruction:
Generate an answer to input query by referring to the information. Answer the question by referencing the provided social issues and their relationships as supporting evidence.
Your answer must be written in Korean.
1. Problem Definition
Provide a brief background on the question to clearly explain what the issue is.
2. Classification of Key Causes and Factors
Categorize the social issues and their causes presented in the provided data (search_result) and explain each in detail.
3.Detailed Explanation with Supporting Evidence
When answering the input query, utilize the reference material as supporting evidence and provide a detailed explanation for each point.
4. Conclusion and Proposed Solutions
Draw a conclusion regarding the question and, if necessary, suggest potential solutions or key takeaways.

Reference:
{search_result}

Input: 
{input_query}
"""

TRANSLATE_ENGLISH = """지시사항: 
아래 텍스트를 영어로 번역해줘. 번역된 텍스트만 출력해줘.

{korean_query}
"""