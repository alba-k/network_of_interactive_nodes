# clients/web_dashboard/services/gateway_connector.py
import requests
import base64
import time
from typing import Dict, Any

class GatewayConnector:
    def __init__(self, gateway_url: str):
        self._gateway_url = gateway_url

    def _get_request(self, endpoint: str) -> Dict[str, Any]:
        """Helper genérico para peticiones GET seguras."""
        try:
            response = requests.get(f"{self._gateway_url}{endpoint}", timeout=2)
            if response.status_code == 200:
                return response.json()
            return {}
        except requests.exceptions.RequestException:
            return {} # Retorna vacío si el nodo está apagado o ocupado

    def get_node_status(self) -> Dict[str, Any]:
        try:
            response = requests.get(f"{self._gateway_url}/health", timeout=2)
            if response.status_code == 200:
                return response.json()
            return {"status": "error", "role": "UNKNOWN"}
        except:
            return {"status": "offline", "role": "DISCONNECTED"}

    # --- NUEVOS MÉTODOS PARA LA DEMO ---
    def get_chain_data(self) -> Dict[str, Any]:
        return self._get_request('/api/chain')

    def get_mempool_data(self) -> Dict[str, Any]:
        return self._get_request('/api/mempool')

    def get_peers_data(self) -> Dict[str, Any]:
        return self._get_request('/api/peers')

    def submit_data(self, data_type: str, content: str) -> Dict[str, Any]:
        try:
            val_b64 = base64.b64encode(content.encode('utf-8')).decode('utf-8')
            payload: dict[str, Any] = {
                "source_id": "Dashboard-Web",
                "data_type": data_type,
                "value": val_b64,
                "nonce": int(time.time()),
                "metadata": {"origin": "WebUI"}
            }
            response = requests.post(f"{self._gateway_url}/submit_data", json=payload, timeout=5)
            if response.status_code == 200:
                return {"success": True, "data": response.json()}
            return {"success": False, "error": response.text}
        except Exception as e:
            return {"success": False, "error": str(e)}