from faker import Faker
from src.conexion_postgres import conectar_postgres
import random

fake = Faker("es_CO")

def poblar_datos():
    conexion = conectar_postgres()
    cursor = conexion.cursor()

    cursor.execute("""
        TRUNCATE TABLE
            auditoria_prestamos,
            prestamo_detalle,
            prestamos,
            resenas,
            inventario,
            sedes,
            libros,
            usuarios,
            editoriales,
            categorias,
            autores
        RESTART IDENTITY CASCADE;
    """)

    for _ in range(250):
        cursor.execute(
            "INSERT INTO Autores(nombre) VALUES(%s)",
            (fake.name(),)
        )

    categorias = ["Tecnologia", "Base de Datos", "Programacion", "IA", "Redes"]

    for categoria in categorias:
        cursor.execute(
            "INSERT INTO Categorias(nombre) VALUES(%s)",
            (categoria,)
        )

    for _ in range(50):
        cursor.execute(
            "INSERT INTO Editoriales(nombre) VALUES(%s)",
            (fake.company(),)
        )

    for i in range(250):
        nombre = fake.name()
        correo = f"usuario{i + 1}@biblioteca.com"

        cursor.execute("""
            INSERT INTO Usuarios(nombre, correo)
            VALUES(%s, %s)
        """, (nombre, correo))

    for _ in range(250):
        cursor.execute("SELECT id_autor FROM Autores ORDER BY RANDOM() LIMIT 1")
        id_autor = cursor.fetchone()[0]

        cursor.execute("SELECT id_categoria FROM Categorias ORDER BY RANDOM() LIMIT 1")
        id_categoria = cursor.fetchone()[0]

        cursor.execute("SELECT id_editorial FROM Editoriales ORDER BY RANDOM() LIMIT 1")
        id_editorial = cursor.fetchone()[0]

        cursor.execute("""
            INSERT INTO Libros(
                titulo,
                fecha_publicacion,
                id_autor,
                id_categoria,
                id_editorial
            )
            VALUES(%s, %s, %s, %s, %s)
        """, (
            fake.sentence(nb_words=4),
            fake.date_between(start_date="-30y", end_date="today"),
            id_autor,
            id_categoria,
            id_editorial
        ))

    for _ in range(20):
        cursor.execute("""
            INSERT INTO Sedes(nombre, ubicacion)
            VALUES(%s, %s)
        """, (
            fake.city(),
            fake.address()
        ))

    for _ in range(250):
        cursor.execute("SELECT id_sede FROM Sedes ORDER BY RANDOM() LIMIT 1")
        id_sede = cursor.fetchone()[0]

        cursor.execute("SELECT id_libro FROM Libros ORDER BY RANDOM() LIMIT 1")
        id_libro = cursor.fetchone()[0]

        cursor.execute("""
            INSERT INTO Inventario(id_sede, id_libro, cantidad_total)
            VALUES(%s, %s, %s)
        """, (
            id_sede,
            id_libro,
            random.randint(1, 30)
        ))

    for _ in range(250):
        cursor.execute("SELECT id_usuario FROM Usuarios ORDER BY RANDOM() LIMIT 1")
        id_usuario = cursor.fetchone()[0]

        estado = random.choice(["ACTIVO", "DEVUELTO", "RETRASADO"])

        cursor.execute("""
            INSERT INTO Prestamos(id_usuario, fecha_salida, estado)
            VALUES(%s, %s, %s)
            RETURNING id_prestamo
        """, (
            id_usuario,
            fake.date_between(start_date="-60d", end_date="today"),
            estado
        ))

        id_prestamo = cursor.fetchone()[0]

        cursor.execute("SELECT id_libro FROM Libros ORDER BY RANDOM() LIMIT 1")
        id_libro = cursor.fetchone()[0]

        cursor.execute("""
            INSERT INTO Prestamo_Detalle(id_prestamo, id_libro)
            VALUES(%s, %s)
        """, (
            id_prestamo,
            id_libro
        ))

    for _ in range(250):
        cursor.execute("SELECT id_usuario FROM Usuarios ORDER BY RANDOM() LIMIT 1")
        id_usuario = cursor.fetchone()[0]

        cursor.execute("SELECT id_libro FROM Libros ORDER BY RANDOM() LIMIT 1")
        id_libro = cursor.fetchone()[0]

        cursor.execute("""
            INSERT INTO Resenas(id_usuario, id_libro, comentario, calificacion)
            VALUES(%s, %s, %s, %s)
        """, (
            id_usuario,
            id_libro,
            fake.text(max_nb_chars=120),
            random.randint(1, 5)
        ))

    conexion.commit()
    cursor.close()
    conexion.close()

    print("Datos generados correctamente")