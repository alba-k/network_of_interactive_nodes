# api/run_server.py

from flask import Flask, jsonify, request
import logging
import json
from uuid import uuid4

# --- Imports del CORE (Servidor) ---
# Importamos el orquestador principal
from core.full_node import FullNode 
from core.models.block import Block # Asumido
from core.models.transaction import Transaction # Asumido
from core._____.consensus_rules import ProofOfWork # Asumido: Usamos PoW como consenso inicial

# --- Placeholder para Serialización (Usamos un método de Block simple) ---
# En un proyecto real, se usaría BlockSerializer
class BlockSerializer:
    @staticmethod
    def to_dict(block: Block) -> dict:
        # Simplificado para fines de demostración
        return {
            'index': block.index,
            'timestamp': block.timestamp,
            'transactions': [Transaction.to_dict(tx) for tx in block.transactions], # Asume Transaction tiene to_dict
            'proof': block.proof,
            'previous_hash': block.previous_hash,
            'hash': block.hash or 'pending'
        }
# ------------------------------------------------------------------------

# 1. Configuración del Logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# 2. Inicialización de la Aplicación Flask
app = Flask(__name__)

# 3. Inicialización del FullNode (Inyección de Dependencia)
# NOTA: Debes asegurarte de que ProofOfWork y Blockchain estén implementados correctamente en core/.
pow_consensus = ProofOfWork(difficulty=4)
full_node = FullNode(consensus=pow_consensus) # <--- Instancia del FullNode

# 4. Endpoints de la API
# =====================================================================

@app.route('/mine', methods=['GET'])
def mine():
    """
    1. GET /mine: Intenta minar un nuevo bloque.
    Llama a full_node.mine_block().
    """
    # Usamos la dirección pública del propio nodo para recibir la recompensa.
    miner_address = full_node.wallet.public_key_hex
    
    new_block = full_node.mine_block(miner_address)

    if new_block is None:
        response = {
            'message': 'No se pudo minar el bloque (ej. no hay transacciones válidas o la dificultad es muy alta).',
        }
        return jsonify(response), 500
    
    response = {
        'message': 'Nuevo Bloque Forjado',
        'block': BlockSerializer.to_dict(new_block),
    }
    return jsonify(response), 200

# ---------------------------------------------------------------------

@app.route('/transactions/new', methods=['POST'])
def new_transaction():
    """
    2. POST /transactions/new: Añade una nueva transacción a la Mempool.
    Llamado por el IoTClient.
    """
    # El body debe contener el JSON serializado de la transacción (sender, recipient, amount, signature, etc.)
    values = request.get_json()
    
    # Validar que los campos requeridos estén en el JSON
    required_fields = ['sender', 'recipient', 'amount', 'signature']
    if not all(field in values for field in required_fields):
        return 'Faltan valores en el cuerpo de la petición.', 400

    # Delega la validación y adición a la Mempool al FullNode
    success = full_node.new_transaction(values)

    if success:
        response = {'message': 'Transacción añadida con éxito a la Mempool.'}
        return jsonify(response), 201
    else:
        response = {'message': 'Transacción rechazada (firma inválida o duplicada).'}
        return jsonify(response), 406 # Not Acceptable

# ---------------------------------------------------------------------

@app.route('/chain', methods=['GET'])
def get_chain():
    """
    3. GET /chain: Retorna la cadena completa.
    Llama a full_node.get_full_chain().
    """
    chain_data = [BlockSerializer.to_dict(b) for b in full_node.get_full_chain()]
    
    response = {
        'chain': chain_data,
        'length': len(chain_data),
    }
    return jsonify(response), 200

# ---------------------------------------------------------------------

@app.route('/nodes/resolve', methods=['GET'])
def resolve_conflicts():
    """
    4. GET /nodes/resolve: Inicia el algoritmo de Consenso P2P.
    Llama a full_node.resolve_conflicts().
    """
    replaced = full_node.resolve_conflicts()

    if replaced:
        message = 'La cadena fue reemplazada por la cadena más larga.'
    else:
        message = 'La cadena es autoritaria y no fue reemplazada.'

    response = {
        'message': message,
        'chain': [BlockSerializer.to_dict(b) for b in full_node.get_full_chain()]
    }
    return jsonify(response), 200

# ---------------------------------------------------------------------

if __name__ == '__main__':
    # Usamos un puerto basado en el ID del nodo para simular diferentes nodos.
    # Usar un puerto fijo (ej: 5000) si solo se ejecuta una instancia.
    port = 5000 
    logging.info(f"Iniciando FullNode en el puerto {port}")
    app.run(host='0.0.0.0', port=port)