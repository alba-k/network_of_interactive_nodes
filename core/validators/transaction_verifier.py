# network_of_interactive_nodes/core/validators/transaction_verifier.py
'''
class TransactionVerifier:
    Actúa como el "Script Interpreter" (Motor de Scripting) del Núcleo Estático.
    
    Responsabilidad: Ejecutar la lógica criptográfica para validar que el "ScriptSig" (Firma)
    desbloquea el "ScriptPubKey" (Clave Pública).

    *** ACTUALIZACIÓN: Sincronizado con TransactionSigner (Manejo de bytes crudos). ***

    Methods:
        verify(public_key, tx_hash, signature_hex) -> bool:
            Punto de entrada. Orquesta la ejecución del script de validación estándar (P2PKH).
            
        _op_check_sig(public_key, message_hash, signature_bytes) -> bool:
            Implementación del OpCode OP_CHECKSIG (Verificación ECDSA pura).
'''

import logging
from typing import Any 
from Crypto.PublicKey.ECC import EccKey
from Crypto.Signature import DSS
from Crypto.Hash import SHA256
from binascii import unhexlify

class TransactionVerifier:

    @staticmethod
    def verify(public_key: EccKey, tx_hash: str, signature_hex: str) -> bool:
        '''
        Ejecuta la validación estándar (Simulación de P2PKH).
        Equivalente a: OP_DUP OP_HASH160 <pubKey> OP_EQUALVERIFY OP_CHECKSIG
        '''
        try:
            # 1. Preparar los datos (La "Pila")
            # IMPORTANTE: Debe coincidir exactamente con la lógica del TransactionSigner.
            # Convertimos el hash hex a bytes crudos antes de hashear para verificar.
            try:
                raw_hash_bytes = unhexlify(tx_hash)
            except Exception:
                # Fallback defensivo si el hash no es hex válido (para compatibilidad)
                raw_hash_bytes = tx_hash.encode('utf-8')

            message_hash_obj = SHA256.new(raw_hash_bytes)
            signature_bytes = unhexlify(signature_hex)

            # 2. Ejecutar Operación Criptográfica (OP_CHECKSIG)
            return TransactionVerifier._op_check_sig(
                public_key=public_key, 
                message_hash_obj=message_hash_obj, 
                signature_bytes=signature_bytes
            )

        except (ValueError, TypeError) as e:
            logging.debug(f"Verifier: Fallo de formato en validación: {e}")
            return False
        except Exception as e:
            logging.error(f"Verifier: Error crítico en motor de scripts: {e}")
            return False

    # --- Implementación de OpCodes (Instrucciones del Intérprete) ---

    @staticmethod
    def _op_check_sig(public_key: EccKey, message_hash_obj: Any, signature_bytes: bytes) -> bool:
        '''
        OP_CHECKSIG: Verifica una firma ECDSA contra un mensaje y una clave pública.
        '''
        try:
            # Usamos el estándar FIPS-186-3 para ECDSA (Curva NIST P-256 / secp256r1)
            # Nota: RFC 6979 se usa para firmar (generar k), pero la verificación
            # sigue el estándar matemático normal ECDSA.
            verifier = DSS.new(public_key, 'fips-186-3') # type: ignore
            
            verifier.verify(message_hash_obj, signature_bytes)
            return True
        except ValueError:
            # La firma no es válida para esta clave y mensaje
            return False