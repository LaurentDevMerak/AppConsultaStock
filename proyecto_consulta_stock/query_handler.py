import pandas as pd

def fetch_stock_data(conn, filters=None):
    """
    Ejecuta una consulta SQL para obtener el stock en piezas y cajas por Código.
    Maneja errores comunes y retorna un DataFrame.
    """
    # Consulta SQL base
    query = """
        SELECT 
            F_STO.ARTSTO AS Código, 
            SUM(F_STO.ACTSTO) AS Pzs, 
            IIF(F_ART.UPPART = 0 OR F_ART.UPPART IS NULL, 0, 
                ROUND(SUM(F_STO.ACTSTO) / F_ART.UPPART)) AS Cajas
        FROM 
            F_STO
        INNER JOIN 
            F_ART ON F_STO.ARTSTO = F_ART.CODART
        GROUP BY 
            F_STO.ARTSTO, F_ART.UPPART
    """

    # Agregar filtros dinámicamente si existen
    if filters:
        # Cambiar filtros para usar alias (Código) en lugar de columna original (ARTSTO)
        column_map = {"Código": "Código", "Pzs": "Pzs", "Cajas": "Cajas"}
        additional_conditions = " AND ".join(
            [f"{column_map.get(key, key)} LIKE '%{value}%'" for key, value in filters.items()]
        )
        # Usar el alias en el WHERE
        query = f"SELECT * FROM ({query}) AS SubQuery WHERE {additional_conditions}"

    try:
        print(f"Ejecutando consulta:\n{query}")
        # Ejecutar la consulta y convertir el resultado en un DataFrame
        df = pd.read_sql(query, conn)
        if df.empty:
            print("Consulta ejecutada, pero no se encontraron resultados.")
        return df
    except Exception as e:
        print(f"Error al ejecutar la consulta: {e}")
        return pd.DataFrame()

if __name__ == "__main__":
    import pyodbc
    from db_connector import connect_to_database

    # Ruta de prueba de la base de datos
    database_path = r"S:\Software DELSOL\FACTUSOL\Datos\FS\PUE2025.accdb"

    # Establecer conexión
    connection = connect_to_database(database_path)
    if connection:
        print("Consultando datos...")

        # Prueba sin filtros
        df = fetch_stock_data(connection)
        print("Consulta sin filtros:")
        print(df)

        # Prueba con filtros
        filters = {"Código": "LV227"}
        df_filtered = fetch_stock_data(connection, filters)
        print("Consulta con filtros:")
        print(df_filtered)

        # Cerrar conexión
        connection.close()
    else:
        print("No se pudo establecer la conexión.")






