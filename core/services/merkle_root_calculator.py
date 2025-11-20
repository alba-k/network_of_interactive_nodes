# network_of_interactive_nodes/core/services/merkle_root_calculator.py
'''
class MerkleRootCalculator:
    Servicio puro (estático) que contiene la lógica para calcular un Merkle Root.

    Methods:
        calculate(tx_hashes: List[str], log_layers: bool) -> str: Calcula el Merkle Root.
                1. Validar que la lista de hashes no esté vacía.
                2. Validar el formato de cada hash (64-char hex).
                3. Copiar la lista de hashes para no mutar la original.
                4. Iniciar el bucle 'while' (mientras haya más de 1 nodo).
                5.  Si el número de nodos es impar, duplicar el último nodo.
                6.  Crear la siguiente capa (next_layer) vacía.
                7.  Iterar sobre la capa actual de 2 en 2.
                8.  Calcular el hash padre.
                9.  Añadir el hash padre a 'next_layer'.
                10. Reemplazar la capa actual por la 'next_layer' completa.
                11. Registrar la capa (logging) si log_layers es True.
                12. Retornar el único hash restante (el Merkle Root).
'''

import logging
from typing import List

# Importaciones de la arquitectura
from core.hashing.merkle_hasher import MerkleHasher

class MerkleRootCalculator:
    @staticmethod
    def calculate(tx_hashes: List[str], log_layers: bool = False) -> str:
        
        if not tx_hashes:
            raise ValueError('La lista de transacciones no puede estar vacía.')

        for h in tx_hashes:
            if len(h) != 64 or not all(c in '0123456789abcdefABCDEF' for c in h):
                raise ValueError(f'Hash inválido o malformado: {h}')

        current_layer: List[str] = tx_hashes.copy()
        layer_num: int = 0

        while len(current_layer) > 1:
            
            if len(current_layer) % 2 != 0:
                current_layer.append(current_layer[-1])

            next_layer: List[str] = []

            for i in range(0, len(current_layer), 2):
                left: str = current_layer[i]
                right: str = current_layer[i + 1]
                
                parent_hash: str = MerkleHasher.hash_pair(left, right)
                
                next_layer.append(parent_hash)

            current_layer: List[str] = next_layer
            layer_num += 1
            
            if log_layers:
                logging.info(f"Capa {layer_num}: {current_layer}")

        return current_layer[0]