from web3 import Web3
from web3.exceptions import ContractLogicError
import os
import json

class Web3Manager:
    def __init__(self, rpc_url, private_key):
        rpc_url = rpc_url.strip() if rpc_url else ""
        private_key = private_key.strip() if private_key else ""
        
        self.w3 = Web3(Web3.HTTPProvider(rpc_url))
        self.private_key = private_key
        if private_key:
            try:
                self.account = self.w3.eth.account.from_key(private_key)
            except Exception as e:
                print(f"Error cargando key: {e}")
                self.account = None
        else:
            self.account = None

    def is_connected(self):
        return self.w3.is_connected()

    def get_address(self):
        return self.account.address if self.account else None

    def get_balance(self):
        if self.account:
            balance_wei = self.w3.eth.get_balance(self.account.address)
            return self.w3.from_wei(balance_wei, 'ether')
        return 0

    def _get_contract_data(self, contract_name):
        compiled_path = os.path.join(os.path.dirname(__file__), 'compiled_contracts.json')
        if not os.path.exists(compiled_path):
            raise Exception("Ejecuta compile_token.py primero.")
        
        with open(compiled_path, 'r') as f:
            data = json.load(f)
        
        if contract_name not in data:
            raise Exception(f"Contrato {contract_name} no encontrado en la compilacion.")
        
        return data[contract_name]['abi'], data[contract_name]['bin']

    def deploy_contract(self, contract_name):
        if not self.account:
            raise Exception("Configura tu Private Key.")
        
        abi, bytecode = self._get_contract_data(contract_name)
        Contract = self.w3.eth.contract(abi=abi, bytecode=bytecode)

        tx = Contract.constructor().build_transaction({
            'from': self.account.address,
            'nonce': self.w3.eth.get_transaction_count(self.account.address),
            'gas': 2000000,
            'gasPrice': self.w3.eth.gas_price
        })

        signed_tx = self.w3.eth.account.sign_transaction(tx, private_key=self.private_key)
        tx_hash = self.w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        
        # ESPERAR CONFIRMACIÓN
        receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)

        return {
            "address": receipt.contractAddress,
            "tx_hash": self.w3.to_hex(tx_hash)
        }

    def approve_airdrop(self, token_address, airdrop_address, amount):
        """
        Da permiso al contrato de Airdrop para mover tus tokens.
        """
        abi, _ = self._get_contract_data('CosaToken')
        token_contract = self.w3.eth.contract(address=Web3.to_checksum_address(token_address), abi=abi)
        
        tx = token_contract.functions.approve(
            Web3.to_checksum_address(airdrop_address),
            amount
        ).build_transaction({
            'from': self.account.address,
            'nonce': self.w3.eth.get_transaction_count(self.account.address),
            'gasPrice': self.w3.eth.gas_price   

            
        })

        signed_tx = self.w3.eth.account.sign_transaction(tx, private_key=self.private_key)
        tx_hash = self.w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        
        # ESPERAR CONFIRMACIÓN
        self.w3.eth.wait_for_transaction_receipt(tx_hash)
        
        return self.w3.to_hex(tx_hash)

    def send_airdrop(self, airdrop_address, token_address, recipients, amounts):
        """
        Ejecuta el airdrop real.
        """
        abi, _ = self._get_contract_data('Airdrop')
        airdrop_contract = self.w3.eth.contract(address=Web3.to_checksum_address(airdrop_address), abi=abi)

        tx = airdrop_contract.functions.airdropTokens(
            Web3.to_checksum_address(token_address),
            [Web3.to_checksum_address(r) for r in recipients],
            amounts
        ).build_transaction({
            'from': self.account.address,
            'nonce': self.w3.eth.get_transaction_count(self.account.address),
            'gas': 3000000,
            'gasPrice': self.w3.eth.gas_price
        })

        signed_tx = self.w3.eth.account.sign_transaction(tx, private_key=self.private_key)
        tx_hash = self.w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        self.w3.eth.wait_for_transaction_receipt(tx_hash)
        return self.w3.to_hex(tx_hash)

    # --- NUEVAS FUNCIONES PARA EL DASHBOARD ---

    def get_contract_eth_balance(self, contract_address):
        """Devuelve el balance en ETH de un contrato."""
        balance_wei = self.w3.eth.get_balance(Web3.to_checksum_address(contract_address))
        return self.w3.from_wei(balance_wei, 'ether')

    def get_donors_list(self, contract_address):
        """Llama a la función del contrato para ver los donantes."""
        abi, _ = self._get_contract_data('Airdrop')
        contract = self.w3.eth.contract(address=Web3.to_checksum_address(contract_address), abi=abi)
        return contract.functions.getDonors().call()

    def donate_eth(self, contract_address, amount_eth):
        """Envía ETH directamente al contrato para donar."""
        tx = {
            'to': Web3.to_checksum_address(contract_address),
            'value': self.w3.to_wei(amount_eth, 'ether'),
            'gas': 200000,
            'gasPrice': self.w3.eth.gas_price,
            'nonce': self.w3.eth.get_transaction_count(self.account.address),
            'chainId': self.w3.eth.chain_id
        }
        signed_tx = self.w3.eth.account.sign_transaction(tx, private_key=self.private_key)
        tx_hash = self.w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        self.w3.eth.wait_for_transaction_receipt(tx_hash)
        return self.w3.to_hex(tx_hash)
