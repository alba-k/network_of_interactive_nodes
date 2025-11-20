# mining_draft.py 
'''
class MiningDraft:
    Borrador MUTABLE. 
    Existe durante el proceso de minado.
    Gestiona el estado mutable (nonce, hash) necesario para el Proof-of-Work.

    Attributes:
        _index          (int):                  Nº de bloque (fijo).
        _timestamp      (float):                Marca de tiempo (fijo).
        _previous_hash  (Optional[str]):        Hash anterior (fijo).
        _difficulty     (int):                  Dificultad objetivo (fijo).
        _merkle_root    (str):                  Raíz de transacciones (fijo).
        _data           (List[Transaction]):    Lista de transacciones (fijo).
        _nonce          (int):                  Contador de prueba de trabajo (Mutable).
        _current_hash   (str):                  Hash calculado actual (Mutable).

    Methods:
        index (Property)->          int:                Retorna el índice del bloque.
        timestamp (Property)->      float:              Retorna la marca de tiempo.
        previous_hash (Property)->  Optional[str]:      Retorna el hash anterior.
        difficulty (Property)->     int:                Retorna la dificultad.
        merkle_root (Property)->    str:                Retorna la raíz Merkle.
        data (Property)->           List[Transaction]:  Retorna la lista de transacciones.
        nonce (Property)->          int:                Retorna el nonce actual.
        hash (Property)->           str:                Retorna el hash actual.
        increment_nonce()->         None:               Incrementa el nonce y recalcula el hash.
'''

from typing import List, Optional # Para type hints (Listas y valores opcionales)
from core.models.transaction import Transaction # Importa la clase 'Transaction' (para la lista 'data')
from core.utils.crypto_utils import CryptoUtils # Importa la 'calculadora' de hashes

class MiningDraft:

    def __init__(self, 
                 index: int, 
                 timestamp: float, 
                 previous_hash: Optional[str], 
                 difficulty: int, 
                 merkle_root: str,
                 data: List[Transaction]):
        
        # --- Datos Fijos ---
        self._index: int = index
        self._timestamp: float = timestamp
        self._previous_hash: Optional[str] = previous_hash
        self._difficulty: int = difficulty
        self._merkle_root: str = merkle_root
        self._data: List[Transaction] = data
        
        # --- Datos mutables ---
        self._nonce: int = 0
        self._current_hash: str = ""
        self._recalculate_hash()

    # ============================= #
    # --- GETTERS [propiedades] --- #
    # ============================= #

    @property
    def index(self) -> int: 
        return self._index
    
    @property
    def timestamp(self) -> float: 
        return self._timestamp
    
    @property
    def previous_hash(self) -> Optional[str]: 
        return self._previous_hash
    
    @property
    def difficulty(self) -> int: 
        return self._difficulty
    
    @property
    def merkle_root(self) -> str: 
        return self._merkle_root
    
    @property
    def data(self) -> List[Transaction]: 
        return self._data
    
    @property
    def nonce(self) -> int: 
        return self._nonce
    
    @property
    def hash(self) -> str: 
        return self._current_hash

    # ======================================== #
    # --- MODIFICADORES [metodos publicos] --- #
    # ======================================== #

    def increment_nonce(self) -> None:
        '''
        Esta es la lógica que sacamos del Block.
        '''
        self._nonce += 1
        self._recalculate_hash()

    # ======================== #
    # --- [metodo privado] --- #
    # ======================== #

    def _recalculate_hash(self) -> None:
        '''
        Llama a la calculadora para actualizar su propio hash.
        '''
        self._current_hash: str = CryptoUtils.calculate_hash(
            index = self._index,
            timestamp = self._timestamp,
            previous_hash = self._previous_hash,
            merkle_root = self._merkle_root, 
            difficulty = self._difficulty, 
            nonce = self._nonce          
        )

        