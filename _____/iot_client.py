# iot_client.py
import requests
import logging
from _____.i_node_client import INodeClient 
from core._____.wallet import Wallet 
from core.models.transaction import Transaction # Asumido
from core.utils.transaction_serializer import TransactionSerializer # Especialista SRP

class IoTClient(INodeClient):
    
    def __init__(self, full_node_url: str):
        self.wallet = Wallet() 
        self.full_node_url = full_node_url 
        
    def get_public_address(self) -> str:
        return self.wallet.public_key_hex

    def sign_transaction(self, recipient: str, amount: float) -> Transaction:
        # Usa la Wallet del core para firmar la transacción
        return self.wallet.create_transaction(recipient, amount)

    def send_transaction(self, transaction: Transaction) -> bool:
        """Envía la transacción firmada al Full Node central a través de la API."""
        try:
            # 1. Serializa usando el especialista SRP
            tx_data = TransactionSerializer.to_dict(transaction) 
            
            # 2. Envía a la API del Full Node
            response = requests.post(
                f'{self.full_node_url}/transactions/new', 
                json=tx_data # Argumento 'json' es ahora de tipo Dict[str, Any]
            )
            
            # Comprobación de que la transacción fue aceptada (código 201)
            return response.status_code == 201
            
        except requests.exceptions.ConnectionError:
            logging.error(f"Error de conexión con el Full Node.")
            return False
        except Exception:
            logging.error(f"Error desconocido al enviar TX.")
            return False