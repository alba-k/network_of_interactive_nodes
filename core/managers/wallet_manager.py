# network_of_interactive_nodes/core/managers/wallet_manager.py
'''
class WalletManager(IWalletRole):
    Gestor (Capa 2) responsable de la identidad, direcciones y firma criptográfica.
    
    Patrón: Dependency Inversion/Polimorfismo. 
    NO almacena la clave privada. En su lugar, consume el contrato ISigner.
    
    Consume: TransactionFactory, AddressFactory, TransactionUtils, ISigner.

    Attributes:
        _public_key (EccKey): La clave pública.
        _signer (ISigner): El servicio de firma inyectado (SoftwareSigner, HardwareSigner, etc.).
        _address (str): La dirección P2PKH derivada.

    Methods:
        get_address() -> str: Retorna la dirección pública legible.
        create_and_sign_data(entries: List[DataEntry]) -> Transaction:
            1. Crea la TX sin firmar (para obtener el hash).
            2. DELEGA la firma al self._signer.
            3. Crea la TX final con la firma.
            4. Verifica la estabilidad del hash (Seguridad Paranoica).
'''

import logging
import time
from typing import List
from Crypto.PublicKey.ECC import EccKey

# Interfaces
from core.interfaces.i_node_roles import IWalletRole
from core.interfaces.i_signer import ISigner 

# Modelos y Estáticos
from core.models.transaction import Transaction
from core.models.data_entry import DataEntry
# TransactionSigner ya NO es necesario aquí directamente, se usa a través del ISigner inyectado.
from core.factories.transaction_factory import TransactionFactory
from identity.address_factory import AddressFactory
from core.dto.transaction_creation_params import TransactionCreationParams
from core.utils.transaction_utils import TransactionUtils

class WalletManager(IWalletRole):

    def __init__(self, public_key: EccKey, signer: ISigner):
        
        # 1. Almacenar la clave pública y el servicio de firma (Inyección).
        self._public_key = public_key
        self._signer = signer 

        # 2. Generamos la dirección real con el AddressFactory (Núcleo Estático).
        self._address = AddressFactory.generate_p2pkh(self._public_key)
        
        logging.info(f'Wallet Manager refactorizado y listo. Dirección: {self._address}')

    def get_address(self) -> str:
        return self._address

    def create_and_sign_data(self, entries: List[DataEntry]) -> Transaction:
        
        current_timestamp: float = time.time()
        
        # 1. Calcular tamaño (Usa Herramienta Estática: TransactionUtils).
        size_bytes: int = TransactionUtils.calculate_data_size(entries)
        
        # 2. Crear TX "Pre-Imagen" (sin firma) para obtener el hash a firmar.
        params_no_sig = TransactionCreationParams(
            entries = entries, 
            timestamp = current_timestamp, 
            signature = None,
            fee = 0, 
            size_bytes = size_bytes, 
            fee_rate = 0.0
        )
        unsigned_tx: Transaction = TransactionFactory.create(params_no_sig)
        
        # 3. FIRMA (Delegación Polimórfica).
        #    El WalletManager NO sabe dónde está la clave, solo llama al contrato.
        signature_hex: str = self._signer.sign(tx_hash=unsigned_tx.tx_hash)
        
        # 4. Crear TX Final (con firma).
        params_with_sig = TransactionCreationParams(
            entries=entries, 
            timestamp=current_timestamp, 
            signature=signature_hex,
            fee=0, 
            size_bytes=size_bytes, 
            fee_rate=0.0
        )
        signed_tx: Transaction = TransactionFactory.create(params_with_sig)
        
        # 5. Verificación Paranoica (Seguridad): El hash no debe cambiar.
        if signed_tx.tx_hash != unsigned_tx.tx_hash:
             raise RuntimeError('Error Crítico: El Hash de la transacción cambió al firmar.')
             
        return signed_tx