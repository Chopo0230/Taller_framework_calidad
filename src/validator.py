import json

from src.conexion_postgres import conectar_postgres

def validar_datos():

    # LEER JSON
    with open("config/config_calidad.json", "r") as archivo:

        reglas = json.load(archivo)

    conexion = conectar_postgres()
    cursor = conexion.cursor()

    errores = []

    # ==========================
    # VALIDAR USUARIOS
    # ==========================
    cursor.execute("""
        SELECT id_usuario, nombre, correo
        FROM Usuarios
    """)

    usuarios = cursor.fetchall()

    for usuario in usuarios:

        id_usuario = usuario[0]
        correo = usuario[2]

        if reglas["correo_debe_contener"] not in correo:

            errores.append(
                f"Usuario {id_usuario} tiene correo invalido"
            )

    # ==========================
    # VALIDAR LIBROS
    # ==========================
    cursor.execute("""
        SELECT id_libro, titulo
        FROM Libros
    """)

    libros = cursor.fetchall()

    for libro in libros:

        id_libro = libro[0]
        titulo = libro[1]

        if len(titulo) < reglas["longitud_min_titulo"]:

            errores.append(
                f"Libro {id_libro} tiene titulo muy corto"
            )

    # ==========================
    # GENERAR LOG
    # ==========================
    with open(
        "logs/reporte_calidad.log",
        "w",
        encoding="utf-8"
    ) as log:

        if len(errores) == 0:

            log.write(
                "VALIDACION EXITOSA\n"
            )

        else:

            for error in errores:

                log.write(error + "\n")

    print(
        f"Validacion completada. "
        f"Errores encontrados: {len(errores)}"
    )

    cursor.close()
    conexion.close()