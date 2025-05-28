from neo4j import GraphDatabase

def get_neo4j_driver(uri:str, auth:tuple[str, str]) -> GraphDatabase.driver:
    driver = GraphDatabase.driver(uri, auth=auth)
    return driver