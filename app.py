from flask import Flask, request, jsonify, render_template
from flask_caching import Cache
from db_connector import connect_to_database
from query_handler import fetch_stock_data
from concurrent.futures import ThreadPoolExecutor
import pandas as pd
import hashlib

app = Flask(__name__)

# Configurar la caché en memoria (puede cambiarse a Redis o archivo si es necesario)
app.config["CACHE_TYPE"] = "simple"
app.config["CACHE_DEFAULT_TIMEOUT"] = 600  # 10 minutos de caché
cache = Cache(app)

# Diccionario de bases de datos por sucursal
DATABASES = {
    "Komerco": r"Z:\KOM2025.accdb",
    "Fray Servando": r"U:\FRA2025.accdb",
    "Argentina": r"X:\ARG2025.accdb",
    "Peña": r"V:\AYN2025.accdb",
    "Venustiano": r"Y:\VCZ2025.accdb",
    "Puebla 5NTE": r"S:\Software DELSOL\FACTUSOL\Datos\FS\PUE2025.accdb",
    "Puebla 10PTE": r"C:\Users\Admin\Komerco Hodiau\Sucursales Gallos BI - Factusol\P10\PTE2025.accdb"
}


@app.route("/")
def index():
    """Cargar la página principal con el formulario de búsqueda."""
    return render_template("index.html")


def generate_cache_key(codigo):
    """
    Genera un identificador único para cada consulta de stock.
    Usamos un hash para evitar problemas con caracteres especiales.
    """
    return hashlib.md5(codigo.encode()).hexdigest()


@app.route("/consultar", methods=["POST"])
def consultar():
    """
    Recibe el código del producto y consulta en todas las bases de datos con caché.
    """
    codigo = request.form.get("codigo", "").strip()

    if not codigo:
        return jsonify({"error": "Ingresa un código de producto válido."}), 400

    cache_key = generate_cache_key(codigo)  # Generar clave única para la caché

    # Verificar si ya hay un resultado en la caché
    cached_data = cache.get(cache_key)
    if cached_data:
        print(f"✅ Respuesta obtenida de caché para código: {codigo}")
        return jsonify(cached_data)

    results = []

    # Consultar las bases en paralelo
    with ThreadPoolExecutor() as executor:
        futures = [
            executor.submit(fetch_data_from_db, store_name, db_path, codigo)
            for store_name, db_path in DATABASES.items()
        ]
        results = [future.result() for future in futures if not future.result().empty]

    if not results:
        return jsonify({"error": f"No se encontraron resultados para el código '{codigo}'"}), 404

    final_df = pd.concat(results, ignore_index=True)

    # Convertir DataFrame a JSON y almacenar en caché
    data = final_df.to_dict(orient="records")
    cache.set(cache_key, data)  # Almacenar la respuesta en caché

    return jsonify(data)


def fetch_data_from_db(store_name, db_path, codigo):
    """
    Función que consulta una base de datos específica y retorna un DataFrame.
    """
    conn = connect_to_database(db_path)
    if not conn:
        return pd.DataFrame()

    filters = {"Código": codigo}
    df = fetch_stock_data(conn, filters)
    conn.close()

    if not df.empty:
        df["Sucursal"] = store_name
    return df


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

