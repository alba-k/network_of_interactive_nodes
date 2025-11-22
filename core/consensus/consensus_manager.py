# network_of_interactive_nodes/core/consensus/consensus_manager.py
'''
class ConsensusManager:
    Servicio que aplica las reglas de consenso y gestiona la Blockchain.

    *** CORRECCIÓN: Usa Config.DIFFICULTY_ADJUSTMENT_INTERVAL en lugar de la constante eliminada. ***
'''

import logging
from typing import Dict, Any, List, Optional, TYPE_CHECKING
from Crypto.PublicKey.ECC import EccKey

# Importaciones de la arquitectura
from core.models.blockchain import Blockchain
from core.models.block import Block
from core.validators.block_validator import BlockValidator
from core.validators.transaction_verifier import TransactionVerifier
from core.consensus.difficulty_adjuster import DifficultyAdjuster

# --- IMPORTACIÓN CLAVE ---
from config import Config

if TYPE_CHECKING:
    EccKeyType = Any
else:
    EccKeyType = EccKey

class ConsensusManager:

    def __init__(self, blockchain: Blockchain):
        self._blockchain = blockchain
        self._orphan_blocks: Dict[str, List[Block]] = {}
        self._side_blocks: Dict[str, Block] = {} 

    def add_block(self, new_block: Block, public_key_map: Dict[str, EccKeyType]) -> bool:
        
        last_block: Block | None = self._blockchain.last_block
        
        # 1. Validación Estructural
        if not BlockValidator.verify(new_block):
            logging.warning(f'Error Consenso: Bloque {new_block.index} inválido (PoW o Integridad).')
            return False

        # 2. Lógica de Posicionamiento
        # CASO A: Extensión Normal
        if last_block and new_block.previous_hash == last_block.hash:
            if self._validate_context(new_block, last_block, public_key_map):
                self._blockchain.add_block_forced(new_block)
                self._process_orphans(new_block.hash, public_key_map)
                return True
            return False

        # CASO B: Génesis
        if not last_block and new_block.index == 0:
            self._blockchain.add_block_forced(new_block)
            return True

        # CASO C: Fork
        parent_block = self._find_block_by_hash(new_block.previous_hash)
        if parent_block:
            logging.info(f"Consenso: Detectada rama lateral (Fork) en bloque {new_block.index}.")
            return self._handle_fork(new_block, parent_block, public_key_map)
        
        # CASO D: Huérfano
        self._add_orphan(new_block)
        return False

    def _validate_context(self, block: Block, previous_block: Block, public_key_map: Dict[str, EccKeyType]) -> bool:
        '''Valida reglas que dependen del bloque anterior.'''
        
        # 1. Índice
        if block.index != (previous_block.index + 1):
            return False

        # 2. Dificultad (Ajuste)
        if DifficultyAdjuster.should_adjust(block.index):
            # ---------------------------------------------------------
            # [CORRECCIÓN] Usamos Config en lugar de DifficultyAdjuster
            # ---------------------------------------------------------
            interval = Config.DIFFICULTY_ADJUSTMENT_INTERVAL
            prev_adj_index = block.index - interval
            
            if prev_adj_index >= 0 and prev_adj_index < len(self._blockchain.chain):
                prev_adj_block = self._blockchain.chain[prev_adj_index]
                expected_bits = DifficultyAdjuster.calculate_new_bits(prev_adj_block, previous_block)
                if block.bits != expected_bits:
                    logging.warning(f"Dificultad incorrecta. Esperada: {expected_bits}")
                    return False

        # 3. Firmas
        for tx in block.data:
            if tx.signature is None or not tx.entries: continue
            data_owner_id = tx.entries[0].source_id
            public_key = public_key_map.get(data_owner_id)
            if public_key:
                if not TransactionVerifier.verify(public_key, tx.tx_hash, tx.signature):
                    logging.warning(f"Firma inválida en TX {tx.tx_hash}")
                    return False
        
        return True

    def _handle_fork(self, new_block: Block, parent_block: Block, public_key_map: Dict[str, EccKeyType]) -> bool:
        if not self._validate_context(new_block, parent_block, public_key_map):
            return False

        self._side_blocks[new_block.hash] = new_block
        
        current_tip = self._blockchain.last_block
        if not current_tip: return False

        if new_block.index > current_tip.index:
            logging.info(f"⚖️ REORG: Nueva cadena (Altura {new_block.index}) supera a actual. Cambiando...")
            return self._reorganize_chain(new_block)
        return True

    def _reorganize_chain(self, new_tip: Block) -> bool:
        new_chain_segment: List[Block] = []
        current_block = new_tip
        main_chain_hashes = {b.hash for b in self._blockchain.chain}
        
        while current_block.hash not in main_chain_hashes:
            new_chain_segment.append(current_block)
            parent_hash = current_block.previous_hash
            if parent_hash in self._side_blocks:
                current_block = self._side_blocks[parent_hash]
            elif self._find_block_in_main_chain(parent_hash):
                break
            else:
                return False

        common_ancestor_hash = current_block.previous_hash
        new_full_chain: List[Block] = []
        
        for blk in self._blockchain.chain:
            new_full_chain.append(blk)
            if blk.hash == common_ancestor_hash:
                break
        
        for blk in reversed(new_chain_segment):
            new_full_chain.append(blk)

        self._blockchain.replace_chain(new_full_chain)
        logging.info(f"✅ REORG COMPLETADO. Nueva altura: {new_tip.index}")
        return True

    def _find_block_by_hash(self, block_hash: str | None) -> Optional[Block]:
        if not block_hash: return None
        for b in self._blockchain.chain:
            if b.hash == block_hash: return b
        return self._side_blocks.get(block_hash)

    def _find_block_in_main_chain(self, block_hash: str | None) -> bool:
        if not block_hash: return False
        for b in self._blockchain.chain:
            if b.hash == block_hash: return True
        return False

    def _add_orphan(self, block: Block):
        parent_hash = block.previous_hash or "None"
        if parent_hash not in self._orphan_blocks:
            self._orphan_blocks[parent_hash] = []
        self._orphan_blocks[parent_hash].append(block)

    def _process_orphans(self, parent_hash: str, public_key_map: Dict[str, EccKeyType]):
        if parent_hash in self._orphan_blocks:
            orphans = self._orphan_blocks[parent_hash]
            del self._orphan_blocks[parent_hash]
            for orphan in orphans:
                self.add_block(orphan, public_key_map)