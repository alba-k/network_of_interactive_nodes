# clients/admin_dashboard/network_config.py
from typing import List, Any

NODES: List[dict[str, Any]] = [
{
        "name": "PC Master (Líder)",
        "ip": "127.0.0.1",   
        "port": 8001,        # (Asumiendo que tu PC corre el Minero/Gateway en 8101)
        "type": "PC"
    },
    {
        "name": "Móvil Termux",
        "ip": "192.168.0.XX", # (Tu móvil, si sigue conectado)
        "port": 8000,
        "type": "MOBILE"
    },
    {
        "name": "Laptop ESP32",   # <--- NUEVO NODO
        "ip": "192.168.0.12",     # <--- ¡PON LA IP DE LA NUEVA LAPTOP AQUÍ!
        "port": 8000,             # Puerto API (Porque usaste GATEWAY 8100)
        "type": "PC"
    }
]