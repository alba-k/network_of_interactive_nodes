# network_of_interactive_nodes/core/interfaces/i_node.py
'''
class INode(ABC):
    Define la Interfaz (Contrato) base para cualquier nodo P2P.

    Methods:
        async def start(self) -> None: Inicia el bucle principal del nodo y todos los servicios de red.
            1. Configurar y enlazar el socket de escucha P2P.
            2. Iniciar el bucle de eventos (asyncio loop).
            3. Lanzar tareas asíncronas para el manejo de la red. 
        
        stop(self) -> None: Cierra todas las conexiones activas y detiene los servicios de forma segura.
            1. Detener el bucle de eventos.
            2. Cerrar el socket de escucha P2P.
            3. Enviar señales de desconexión a los pares activos.
            4. Liberar todos los recursos. 

        handle_message(self, message: Message, peer_id: str) -> None: Procesa un 'Message' (DTO) que ya fue recibido, deserializado y validado.
            1. Determinar el tipo de mensaje (ej. NEW_TX, NEW_BLOCK, REQUEST_CHAIN).
            2. Despachar el mensaje al servicio o manejador interno correspondiente.
            3. Aplicar cualquier actualización de estado o lógica de negocio.  

        initiate_handshake(self, peer: Peer) -> None:   Inicia el protocolo de "apretón de manos" (handshake) con un par recién conectado.
            1. Enviar el mensaje 'VERSION' o 'HELLO' al nuevo par.
            2. Registrar el estado del par como 'HANDSHAKE_PENDING'.   
'''

from abc import ABC, abstractmethod
from core.p2p.message import Message 
from core.p2p.peer import Peer 

class INode(ABC):

    @abstractmethod
    async def start(self) -> None: 
        pass

    @abstractmethod
    async def stop(self) -> None:
        pass
    
    @abstractmethod
    def handle_message(self, message: Message, peer_id: str) -> None: 
        pass

    @abstractmethod
    def initiate_handshake(self, peer: Peer) -> None:
        pass