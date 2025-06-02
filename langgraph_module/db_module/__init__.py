from .postgresql import get_postgres_connection
from .neo4j import get_neo4j_driver

print(">>> db_module/__init__.py loaded!")

__all__ = [
    "get_postgres_connection",
    "get_neo4j_driver"
]