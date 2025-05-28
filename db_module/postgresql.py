import psycopg2

def get_postgres_connection(host:str, dbname:str, user:str, password:str, port:int) -> psycopg2.extensions.connection:
    try:
        connection = psycopg2.connect(
                        host=host, 
                        dbname=dbname, 
                        user=user, 
                        password=password, 
                        port=port
                    )
        return connection
    except Exception as e:
        print(f"Error connecting to PostgreSQL database: {e}")
        return None