# network_of_interactive_nodes/core/services/merkle_root_calculator.py
'''
class MerkleRootCalculator:
    Contiene la lógica para calcular un Merkle Root.

    Methods:
        calculate(tx_hashes: List[str], log_layers: bool) -> str: Calcula el Merkle Root.
            1. Validar entradas.
            2. Ordenar la lista de hashes.
            3. Copiar la lista ordenada.
            4. Bucle de construcción del árbol (hash_pair).
            5. Retornar la raíz.
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

        current_layer: List[str] = sorted(tx_hashes)
        
        layer_num: int = 0

        if log_layers:
            logging.debug(f'Merkle: Iniciando cálculo con {len(current_layer)} hojas ordenadas.')

        while len(current_layer) > 1:

            if len(current_layer) % 2 != 0:
                current_layer.append(current_layer[-1])

            next_layer: List[str] = []

            for i in range(0, len(current_layer), 2):
                left: str = current_layer[i]
                right: str = current_layer[i + 1]
                parent_hash: str = MerkleHasher.hash_pair(left, right)

                next_layer.append(parent_hash)

            current_layer = next_layer
            layer_num += 1

            if log_layers:
                logging.info(f'Capa {layer_num}: {current_layer}')

        return current_layer[0]