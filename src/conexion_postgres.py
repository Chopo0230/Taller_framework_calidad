import psycopg2

def conectar_postgres():

    conexion = psycopg2.connect(
        host="localhost",
        database="biblioteca_framework",
        user="postgres",
        password="Admin123*"
    )

    return conexion