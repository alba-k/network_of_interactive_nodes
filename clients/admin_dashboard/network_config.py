# clients/admin_dashboard/network_config.py
from typing import List, Any

NODES: List[dict[str, Any]] = [
    {
        "name": "PC 1 (Líder)", "ip": "192.168.0.5", "port": 8000, "type": "PC"
    },
    {
        "name": "PC 2 (Pablo)", "ip": "192.168.0.3", "port": 8100, "type": "PC" # Puerto API 8100
    }
]