from src.conexion_postgres import conectar_postgres

def ejecutar_objetos_sql():
    conexion = conectar_postgres()
    cursor = conexion.cursor()

    print("\n--- Vista de libros prestados ---")

    cursor.execute("""
        SELECT *
        FROM vista_libros_prestados
        LIMIT 10;
    """)

    resultados = cursor.fetchall()

    for fila in resultados:
        print(fila)

    print("\n--- Calculo de multa ---")

    cursor.execute("""
        SELECT calcular_multa('2024-01-01');
    """)

    multa = cursor.fetchone()[0]
    print(f"Multa calculada: {multa}")

    print("\n--- Auditoria de prestamos activos ---")

    cursor.execute("""
        CALL auditar_prestamos();
    """)

    conexion.commit()

    cursor.execute("""
        SELECT COUNT(*)
        FROM Auditoria_Prestamos;
    """)

    total_auditoria = cursor.fetchone()[0]
    print(f"Registros de auditoria generados: {total_auditoria}")

    cursor.close()
    conexion.close()

    print("\nObjetos SQL ejecutados correctamente")