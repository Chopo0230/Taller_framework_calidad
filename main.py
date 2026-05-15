from src.migracion_mongo import migrar_a_mongo
from src.generador_datos import poblar_datos
from src.validator import validar_datos
from src.executor_sql import ejecutar_objetos_sql

poblar_datos()
validar_datos()
ejecutar_objetos_sql()
migrar_a_mongo()