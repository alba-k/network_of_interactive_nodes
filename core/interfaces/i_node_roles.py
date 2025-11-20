# network_of_interactive_nodes/core/interfaces/i_node_roles.py
'''
Define las Interfaces (Contratos) para los "roles" especializados que un nodo puede implementar.

    class IBlockValidatorRole(ABC):
        Define el rol de un validador completo (Full Node).
        
        Methods:
            validate_block_rules(self, block: Block) -> bool: Contrato para validar las reglas de un bloque.
                1. Validar la integridad del PoW (re-hasheo).
                2. Validar la conexión (índice, hash previo).
                3. Validar el timestamp del bloque.
                4. Retornar True si todas las reglas pasan.
            
            validate_tx_rules(self, tx: Transaction) -> bool: Contrato para validar las reglas de una transacción.
                1. Validar la integridad del hash de la TX.
                2. Validar la firma digital de la TX.
                3. Retornar True si todas las reglas pasan.

    class IMinerRole(ABC):
        Define el rol de un minero (construir bloques).

        Methods:
            create_new_block(self) -> Block: Contrato para orquestar la minería de un nuevo bloque.
                1. Obtener transacciones del Mempool.
                2. Obtener dificultad ('bits') de la cadena.
                3. Llamar al 'BlockBuilder' para minar (PoW).
                4. Retornar el 'Block' minado.
        
    class IWalletRole(ABC):
        Define el rol de una billetera (gestionar llaves).

        Methods:
            create_and_sign_data(self, entries: List[DataEntry]) -> Transaction: Contrato para orquestar la creación y firma de una transacción.
                1. Recibir los 'DataEntry' (datos crudos).
                2. Cargar la clave privada.
                3. Llamar al 'TransactionBuilder' para construir y firmar.
                4. Retornar la 'Transaction' firmada.

    class IAPIRole(ABC):
        Define el rol de un Gateway/Relay (exponer API).

        Methods:
            start_api_server(self): Contrato para iniciar el servidor de API (ej. Flask/Waitress).
                1. Configurar los endpoints (rutas) de Flask.
                2. Iniciar el servidor.

            stop_api_server(self): Contrato para detener el servidor de API de forma segura.
                1. Detener el servidor (ej. Waitress).
'''

from abc import ABC, abstractmethod
from typing import List

# Importaciones de la arquitectura
from core.models.block import Block
from core.models.transaction import Transaction
from core.models.data_entry import DataEntry

class IBlockValidatorRole(ABC):
    @abstractmethod
    def validate_block_rules(self, block: Block) -> bool:
        pass
        
    @abstractmethod
    def validate_tx_rules(self, tx: Transaction) -> bool:
        pass

class IMinerRole(ABC):
    @abstractmethod
    def create_new_block(self) -> Block:
        pass

class IWalletRole(ABC):
    @abstractmethod
    def create_and_sign_data(self, entries: List[DataEntry]) -> Transaction:
        pass

class IAPIRole(ABC):
    @abstractmethod
    def start_api_server(self):
        pass

    @abstractmethod
    def stop_api_server(self):
        pass