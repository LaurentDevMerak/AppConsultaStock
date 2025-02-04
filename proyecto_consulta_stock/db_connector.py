import pyodbc

def connect_to_database(database_path):
    """
    Conecta a una base de datos Access (.accdb).
    Maneja errores comunes y retorna la conexión.
    """
    try:
        connection_string = f"DRIVER={{Microsoft Access Driver (*.mdb, *.accdb)}};DBQ={database_path};"
        conn = pyodbc.connect(connection_string)
        print(f"Conexión exitosa a la base de datos: {database_path}")
        return conn
    except pyodbc.InterfaceError:
        print("Error: No se pudo encontrar el controlador ODBC.")
        return None
    except pyodbc.DatabaseError as e:
        print(f"Error al conectar a la base de datos: {e}")
        return None

if __name__ == "__main__":
    # Ruta de prueba para la base de datos
    test_database_path = r"S:\Software DELSOL\FACTUSOL\Datos\FS\PUE2025.accdb"

    print("Probando conexión a la base de datos...")
    connection = connect_to_database(test_database_path)

    if connection:
        print("Conexión establecida exitosamente.")
        cursor = connection.cursor()
        # Listado de tablas para comprobación
        print("Tablas disponibles en la base de datos:")
        try:
            tables = cursor.tables(tableType="TABLE")
            for table in tables:
                print(f" - {table.table_name}")
        except Exception as e:
            print(f"Error al enumerar tablas: {e}")
        connection.close()
    else:
        print("No se pudo establecer la conexión con la base de datos.")




