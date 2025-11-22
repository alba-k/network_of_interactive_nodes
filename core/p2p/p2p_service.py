# network_of_interactive_nodes/core/p2p/p2p_service.py
'''
class P2PService:
    Orquesta toda la comunicación de red P2P (asyncio).
    Maneja las conexiones entrantes y salientes (peers), y utiliza los Serializers/Deserializers para enviar y recibir mensajes.

    Attributes:
        _node       (INode):            La instancia del nodo (capa superior) a la que se reportan los mensajes.
        _peers      (Dict):             Un diccionario de los 'Peers' actualmente conectados.
        _server     (asyncio.Server):   La instancia del servidor que escucha.
        _host       (str):              El host donde escucha el servidor.
        _port       (int):              El puerto donde escucha el servidor.
        _seed_peers (List):             Una lista de tuplas (host, port) para la conexión inicial.

    Methods:
        start_service(): Inicia el servicio (escucha y conexión a seeds).
            1. Iniciar el servidor (escuchar)
            2. Conectar a los 'seeds' (hablar)

        _start_listening(): (Privado) Inicia el servidor asyncio.
            1. Iniciar el servidor asyncio

        _connect_to_seeds(): (Privado) Se conecta a los peers iniciales.
            1. Esperar un momento a que el servidor inicie
            2. Iterar sobre los seeds y crear tareas de conexión

        stop_service(self): Detiene el servicio P2P (cierra el servidor y desconecta a los pares).
            1. Detener el servidor (no más conexiones entrantes)
            2. Desconectar todos los pares (cerrar conexiones)
            3. Crear tareas para cerrar cada 'writer'
            4. Esperar a que todos los writers se cierren
            
        connect_to_peer(host, port): Inicia una conexión saliente a un par.
            1. Generar ID y evitar reconexión
            2. Intentar abrir la conexión (outbound)
            3. Registrar la nueva conexión

        _handle_inbound_connection(reader, writer): (Callback) Maneja conexiones entrantes.
            1. Obtener ID del par entrante
            2. Registrar la nueva conexión

        handle_new_connection(reader, writer, peer_id, is_outbound): (Lógica) Registra un nuevo par (entrante o saliente).
            1. Crear y almacenar el objeto Peer
            2. Iniciar la tarea de escucha para este par
            3. Si somos el iniciador (outbound), enviar handshake

        _listen_to_peer(peer, peer_id): (Bucle) Tarea principal que escucha mensajes de un par conectado.
            1. Bucle principal de escucha
            2. Leer el header (tamaño fijo)
            3. Pre-parsear el header (solo para obtener el tamaño)
            4. **Validar tamaño contra NetworkConfig.MAX_PAYLOAD_SIZE**
            5. Leer el payload (tamaño variable)
            6. Combinar header + payload
            7. Deserializar el paquete completo
            8. Pasar el mensaje al Nodo (capa superior)
            9. Manejar desconexión y limpiar

        get_peer(peer_id): Retorna un objeto Peer si está conectado.

        send_message(peer, command, payload_dto): Serializa y envía un mensaje a un par.
            1. Serializar el mensaje (a 'tu manera')
            2. Enviar los bytes por el 'writer'

        broadcast(command, payload_dto): Envía un mensaje a todos los pares conectados.
            1. Iterar sobre todos los pares conectados
            2. Enviar el mensaje a cada uno
'''

import asyncio
import logging
import struct 
from typing import Dict, Any, List, Tuple, Coroutine

# Importaciones de la arquitectura
from core.interfaces.i_node import INode 
from core.p2p.peer import Peer
from core.p2p.p2p_message_serializer import P2PMessageSerializer
from core.p2p.p2p_message_deserializer import P2PMessageDeserializer  
from core.p2p.message import Message 

# Importacion de la configuracion
from config import Config

class P2PService:

    def __init__(self, node: INode, host: str, port: int, seed_peers: List[Tuple[str, int]] | None = None):
        self._node: INode = node
        self._peers: Dict[str, Peer] = {}
        self._server: asyncio.Server | None = None
        self._host: str = host
        self._port: int = port
        self._seed_peers: List[Tuple[str, int]] = seed_peers or []

    async def start_service(self):
        asyncio.create_task(self._start_listening())
        asyncio.create_task(self._connect_to_seeds())

    async def _start_listening(self):
        try:
            self._server = await asyncio.start_server(self._handle_inbound_connection, self._host, self._port)
            logging.info(f'Servidor P2P escuchando en {self._host}:{self._port}')
        except OSError as e:
            logging.error(f'Error P2P: No se pudo iniciar el servidor en {self._port}. {e}')
            raise

    async def _connect_to_seeds(self):
        await asyncio.sleep(2) 
        for host, port in self._seed_peers:
            asyncio.create_task(self.connect_to_peer(host, port))

    async def connect_to_peer(self, host: str, port: int):
        peer_id = f'{host}:{port}'
        if peer_id in self._peers: return
        
        try:
            logging.info(f'P2P: Conectando a (seed) {peer_id}...')
            reader, writer = await asyncio.open_connection(host, port)
            self.handle_new_connection(reader, writer, peer_id, is_outbound = True)
            
        except OSError as e:
            logging.warning(f'Error P2P: No se pudo conectar a {peer_id}. {e}')

    async def _handle_inbound_connection(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        addr = writer.get_extra_info('peername')
        peer_id = f'{addr[0]}:{addr[1]}'
        logging.info(f'Nueva conexión P2P entrante de: {peer_id}')
        self.handle_new_connection(reader, writer, peer_id, is_outbound = False)

    async def stop_service(self):
        
        if self._server:
            self._server.close()
            await self._server.wait_closed()
            logging.info('Servidor P2P detenido.')
            self._server = None
            
        peers_to_disconnect = list(self._peers.values())
        
        if peers_to_disconnect:
            logging.info(f'Desconectando {len(peers_to_disconnect)} pares...')
            tasks: List[Coroutine[Any, Any, None]] = [] 

            for peer in peers_to_disconnect:
                if not peer.writer.is_closing():
                    peer.writer.close()
                    tasks.append(peer.writer.wait_closed())
            
            await asyncio.gather(*tasks, return_exceptions = True)
        self._peers.clear()
        logging.info('Servicio P2P completamente detenido.')

    def handle_new_connection(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter, peer_id: str, is_outbound: bool):
        peer = Peer(host = peer_id.split(':')[0], port = int(peer_id.split(':')[1]), reader = reader, writer = writer)
        self._peers[peer_id] = peer
        asyncio.create_task(self._listen_to_peer(peer, peer_id))
        
        if is_outbound:
            self._node.initiate_handshake(peer)

    async def _listen_to_peer(self, peer: Peer, peer_id: str):

        try:
            while True:
                header_data = await peer.reader.readexactly(P2PMessageSerializer.HEADER_SIZE)
                
                try:
                    _command, payload_size, _checksum = struct.unpack(P2PMessageSerializer.HEADER_FORMAT, header_data)
                except struct.error:
                    logging.warning(f'Error P2P: Header corrupto de {peer_id}. Desconectando.')
                    break
                
                # Usamos Config.NETWORK_MAX_PAYLOAD_SIZE en lugar de NetworkConfig directo
                if payload_size > Config.NETWORK_MAX_PAYLOAD_SIZE:
                    logging.warning(f'SEGURIDAD P2P: Par {peer_id} excedió límite de configuración ({payload_size} bytes). Desconectando.')
                    break

                payload_data = await peer.reader.readexactly(payload_size)
                full_packet = header_data + payload_data
                
                try:
                    message: Message = P2PMessageDeserializer.deserialize(full_packet)
                    self._node.handle_message(message, peer_id)
                    
                except ValueError as e:
                    logging.warning(f'Error P2P: Mensaje corrupto de {peer_id}. {e}')
                    
        except (asyncio.IncompleteReadError, ConnectionResetError):
            logging.info(f'Par {peer_id} desconectado (Fin de stream).')
        except Exception as e:
            logging.error(f'Error inesperado en conexión con {peer_id}: {e}')
        finally:
            self._peers.pop(peer_id, None)
            if not peer.writer.is_closing():
                peer.writer.close()
                await peer.writer.wait_closed()

    def get_peer(self, peer_id: str) -> Peer | None:
        return self._peers.get(peer_id)

    async def send_message(self, peer: Peer, command: str, payload_dto: Any):
        try:
            message_bytes = P2PMessageSerializer.serialize(command, payload_dto)
            peer.writer.write(message_bytes)
            await peer.writer.drain()
            
        except (OSError, BrokenPipeError) as e:
            logging.warning(f'Error P2P: No se pudo enviar mensaje a {peer.host}. {e}')

    async def broadcast(self, command: str, payload_dto: Any):
        for peer in self._peers.values():
            await self.send_message(peer, command, payload_dto)