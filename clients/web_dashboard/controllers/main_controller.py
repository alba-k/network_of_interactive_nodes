# clients/web_dashboard/controllers/main_controller.py
from flask import Blueprint, render_template, request, jsonify
from services.gateway_connector import GatewayConnector

class MainController:
    def __init__(self, gateway: GatewayConnector):
        self._gateway = gateway
        self.blueprint = Blueprint('main', __name__)
        self._setup_routes()

    def _setup_routes(self):
        self.blueprint.add_url_rule('/', view_func=self.index)
        # Rutas API internas del Dashboard (Puente hacia el Nodo)
        self.blueprint.add_url_rule('/api/status', view_func=self.status)
        self.blueprint.add_url_rule('/api/chain', view_func=self.chain)
        self.blueprint.add_url_rule('/api/mempool', view_func=self.mempool)
        self.blueprint.add_url_rule('/api/send', view_func=self.send_data, methods=['POST'])

    def index(self):
        return render_template('dashboard.html')

    def status(self):
        # Combinamos salud básica + conteo de peers en una sola respuesta para la UI
        health = self._gateway.get_node_status()
        peers = self._gateway.get_peers_data()
        health.update(peers) # Fusionar diccionarios
        return jsonify(health)

    def chain(self):
        return jsonify(self._gateway.get_chain_data())

    def mempool(self):
        return jsonify(self._gateway.get_mempool_data())

    def send_data(self):
        data = request.json
        if not data: return jsonify({"error": "No data"}), 400
        result = self._gateway.submit_data(data.get('type'), data.get('content'))
        return jsonify(result)