import json
import datetime
from pymongo import MongoClient
from pymongo.errors import BulkWriteError
from src.conexion_postgres import conectar_postgres


def cargar_mapping():
    with open("config/mapping_mongo.json", "r", encoding="utf-8") as f:
        return json.load(f)


def conectar_mongo():
    cliente = MongoClient("mongodb://localhost:27017/")
    cliente.server_info()  # lanza error si no conecta
    db = cliente["biblioteca_mongo"]
    return cliente, db


def transformar_fila(fila: tuple, columnas: list, field_map: dict) -> dict:
    """Convierte una fila de PG en documento MongoDB usando el mapeo."""
    fila_dict = dict(zip(columnas, fila))
    doc = {}
    for col_pg, campo_mongo in field_map.items():
        valor = fila_dict.get(col_pg)
        # Convertir fechas a string ISO para que MongoDB las acepte
        if isinstance(valor, (datetime.date, datetime.datetime)):
            valor = valor.isoformat()
        doc[campo_mongo] = valor
    return doc


def migrar_tabla(cursor, mongo_db, nombre_clave: str, config: dict) -> dict:
    """Migra una sola tabla de PG a una colección de MongoDB."""
    tabla     = config["source_table"]
    coleccion = config["mongo_collection"]
    field_map = config["fields"]

    print(f"  → Migrando '{tabla}' → colección '{coleccion}' ...", end=" ", flush=True)

    # Extraer datos de PostgreSQL
    try:
        cursor.execute(f'SELECT * FROM public."{tabla}"')
        filas = cursor.fetchall()
        columnas = [desc[0] for desc in cursor.description]
    except Exception as e:
        print(f"ERROR al leer PG: {e}")
        return {"estado": "ERROR_PG", "registros_pg": 0, "insertados": 0}

    if not filas:
        print("sin registros.")
        return {"estado": "OMITIDO", "registros_pg": 0, "insertados": 0}

    # Transformar filas a documentos
    documentos = [transformar_fila(f, columnas, field_map) for f in filas]

    # Insertar en MongoDB (drop previo para migración limpia/idempotente)
    col = mongo_db[coleccion]
    col.drop()

    try:
        resultado = col.insert_many(documentos, ordered=False)
        insertados = len(resultado.inserted_ids)
        print(f"{insertados}/{len(filas)} documentos insertados.")
        return {"estado": "OK", "registros_pg": len(filas), "insertados": insertados}
    except BulkWriteError as bwe:
        insertados = bwe.details.get("nInserted", 0)
        print(f"PARCIAL — {insertados}/{len(filas)} insertados.")
        return {"estado": "PARCIAL", "registros_pg": len(filas), "insertados": insertados}
    except Exception as e:
        print(f"ERROR al insertar en Mongo: {e}")
        return {"estado": "ERROR_MG", "registros_pg": len(filas), "insertados": 0}


def generar_reporte_mongo(reporte: dict):
    """Agrega el resultado de la migración al log existente."""
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    total_pg = sum(v["registros_pg"] for v in reporte.values())
    total_mg = sum(v["insertados"]   for v in reporte.values())

    lineas = [
        "\n" + "=" * 55,
        "  FASE D: REPORTE DE MIGRACIÓN A MONGODB",
        f"  Fecha: {ts}",
        "=" * 55,
    ]

    for nombre, datos in reporte.items():
        lineas.append(
            f"  {nombre:20s} | {datos['estado']:8s} | "
            f"PG={datos['registros_pg']:4d} | MG={datos['insertados']:4d}"
        )

    lineas += [
        "-" * 55,
        f"  Total extraídos de PostgreSQL : {total_pg}",
        f"  Total insertados en MongoDB   : {total_mg}",
        f"  Registros con error           : {total_pg - total_mg}",
        "=" * 55,
    ]

    contenido = "\n".join(lineas)
    print(contenido)

    # Agrega al mismo log que usa validator.py
    with open("logs/reporte_calidad.log", "a", encoding="utf-8") as log:
        log.write(contenido + "\n")

    print("\n[LOG] Reporte de migración agregado a logs/reporte_calidad.log")


def migrar_a_mongo():
    print("\n--- Migración automática a MongoDB ---")

    # Cargar mapeo
    mapping = cargar_mapping()

    # Conectar bases de datos
    try:
        mongo_cliente, mongo_db = conectar_mongo()
        print("  Conexión a MongoDB exitosa.")
    except Exception as e:
        print(f"  ERROR conectando a MongoDB: {e}")
        print("  Verifica que MongoDB esté corriendo en localhost:27017")
        return

    conexion_pg = conectar_postgres()
    cursor      = conexion_pg.cursor()

    reporte = {}

    # Migrar cada colección definida en el JSON
    for nombre_clave, config in mapping["collections"].items():
        reporte[nombre_clave] = migrar_tabla(cursor, mongo_db, nombre_clave, config)

    cursor.close()
    conexion_pg.close()
    mongo_cliente.close()

    generar_reporte_mongo(reporte)
    print("\nMigración a MongoDB completada.")