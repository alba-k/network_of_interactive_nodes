# clients/admin_dashboard/app.py
from flask import Flask, render_template, jsonify, request
import requests
from typing import List, Dict, Any, Union # <--- Importaciones para el Tipado
from network_config import NODES

app = Flask(__name__)

# --- RUTA PRINCIPAL (VISTA) ---
@app.route('/')
def index():
    return render_template('admin.html')

# --- API INTERNA: Escanear la red ---
@app.route('/api/scan')
def scan_network():
    """Consulta el estado de todos los nodos en la lista."""
    
    # [CORRECCIÓN 1] Definimos explícitamente que esto es una lista de diccionarios
    results: List[Dict[str, Any]] = []
    
    for node in NODES:
        try:
            # Construir URL del nodo
            base_url = f"http://{node['ip']}:{node['port']}"
            
            # Consultamos la salud y los peers con timeout corto
            health = requests.get(f"{base_url}/health", timeout=1).json()
            peers = requests.get(f"{base_url}/api/peers", timeout=1).json()
            
            node_data: dict[str, Any] = {
                "online": True,
                "name": node['name'],
                "url": base_url,
                "role": health.get('role', 'UNKNOWN'),
                "height": health.get('height', 0),
                "peers": peers.get('peers_count', 0),
                "mempool": health.get('mempool_size', 0)
            }
            results.append(node_data)
        except:
            # Si el nodo no responde (OFFLINE)
            offline_data:  dict[str, Any] = {
                "online": False,
                "name": node['name'],
                "url": f"http://{node['ip']}:{node['port']}",
                "role": "OFFLINE",
                "height": 0,
                "peers": "-",
                "mempool": "-"
            }
            results.append(offline_data)
            
    return jsonify(results)

# --- API INTERNA: Enviar comandos (Botones) ---
@app.route('/api/control', methods=['POST'])
def control_node():
    """Reenvía la orden de Start/Stop al nodo correspondiente."""
    
    # [CORRECCIÓN 2] Aseguramos que 'data' sea un diccionario y no None
    data: Union[Dict[str, Any], None] = request.get_json()
    
    if not data:
        return jsonify({"status": "error", "message": "No data received"}), 400

    target_url = data.get('url')
    action = data.get('action') # 'start' o 'stop'
    
    if not target_url or not action:
        return jsonify({"status": "error", "message": "Missing url or action"}), 400

    try:
        # Llamamos al endpoint del nodo (APIManager)
        endpoint = f"{target_url}/api/control/mining/{action}"
        # Enviamos el POST al nodo real
        response = requests.post(endpoint, timeout=2)
        
        # Devolvemos la respuesta del nodo al frontend
        return jsonify(response.json())
        
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

if __name__ == '__main__':
    print("🚀 ORQUESTADOR LISTO EN: http://127.0.0.1:5050")
    app.run(port=5050, host='0.0.0.0', debug=True)