from web3 import Web3
from web3.exceptions import ContractLogicError
import os
import json

class Web3Manager:
    def __init__(self, rpc_url, private_key):
        """
        Constructor: inicializa la conexión con la blockchain.
        - Crea un proveedor HTTP apuntando a la RPC_URL (ej: nodo de Sepolia).
        - Deriva la cuenta (address pública) a partir de la private_key.
          La private key NUNCA sale de aquí, solo se usa para firmar txs localmente.
        """
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
        """
        Comprueba si el nodo RPC responde.
        Útil para mostrar el semáforo verde/rojo en la sidebar de la app.
        """
        return self.w3.is_connected()

    def get_address(self):
        """
        Devuelve la dirección pública (0x...) de la billetera cargada.
        Si no hay private key configurada, devuelve None.
        """
        return self.account.address if self.account else None

    def get_balance(self):
        """
        Consulta el balance de ETH de nuestra billetera directamente en la blockchain.
        Devuelve el valor en ETH (no en wei, que es la unidad mínima de Ethereum).
        """
        if self.account:
            balance_wei = self.w3.eth.get_balance(self.account.address)
            return self.w3.from_wei(balance_wei, 'ether')
        return 0

    def _get_contract_data(self, contract_name):
        """
        Método interno (privado, por eso empieza con _).
        Lee el archivo compiled_contracts.json que genera compile_token.py
        y devuelve el ABI y el bytecode del contrato solicitado.
        - ABI: es como el "manual de instrucciones" del contrato, le dice a web3
          qué funciones existen y qué parámetros aceptan.
        - Bytecode: el código compilado que se despliega en la blockchain.
        """
        compiled_path = os.path.join(os.path.dirname(__file__), 'compiled_contracts.json')
        if not os.path.exists(compiled_path):
            raise Exception("Ejecuta compile_token.py primero.")
        
        with open(compiled_path, 'r') as f:
            data = json.load(f)
        
        if contract_name not in data:
            raise Exception(f"Contrato {contract_name} no encontrado en la compilacion.")
        
        return data[contract_name]['abi'], data[contract_name]['bin']

    def deploy_contract(self, contract_name):
        """
        Despliega un contrato nuevo en la blockchain.
        """
        if not self.account:
            raise Exception("Configura tu Private Key.")
        
        abi, bytecode = self._get_contract_data(contract_name)
        Contract = self.w3.eth.contract(abi=abi, bytecode=bytecode)

        # Boost gas price by 20% to avoid getting stuck
        current_gas_price = self.w3.eth.gas_price
        gas_price = int(current_gas_price * 1.2)

        tx = Contract.constructor().build_transaction({
            'from': self.account.address,
            'nonce': self.w3.eth.get_transaction_count(self.account.address),
            'gas': 2000000,
            'gasPrice': gas_price,
            'chainId': self.w3.eth.chain_id
        })

        signed_tx = self.w3.eth.account.sign_transaction(tx, private_key=self.private_key)
        tx_hash = self.w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        
        tx_hex = self.w3.to_hex(tx_hash)
        print(f"Transacción enviada: {tx_hex}")
        
        # Esperamos a que la tx sea incluida en un bloque (máximo 5 min)
        try:
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=300)
            return {
                "address": receipt.contractAddress,
                "tx_hash": tx_hex
            }
        except Exception as e:
            raise Exception(f"Tiempo de espera agotado o error: {tx_hex}. Revisa en Etherscan.")

    def approve_airdrop(self, token_address, airdrop_address, amount):
        """
        Llama a la función approve() del contrato ERC20 (CosaToken).
        Esto le da permiso al contrato Airdrop para mover tokens en nuestro nombre.
        Sin este paso previo, el Airdrop no podría hacer transferFrom() y fallaría.
        Es el paso 1 obligatorio antes de ejecutar cualquier airdrop de tokens.
        """
        abi, _ = self._get_contract_data('CosaToken')
        token_contract = self.w3.eth.contract(address=Web3.to_checksum_address(token_address), abi=abi)
        
        # Boost gas price
        current_gas_price = self.w3.eth.gas_price
        gas_price = int(current_gas_price * 1.2)

        tx = token_contract.functions.approve(
            Web3.to_checksum_address(airdrop_address),
            amount
        ).build_transaction({
            'from': self.account.address,
            'nonce': self.w3.eth.get_transaction_count(self.account.address),
            'gasPrice': gas_price,
            'chainId': self.w3.eth.chain_id
        })

        signed_tx = self.w3.eth.account.sign_transaction(tx, private_key=self.private_key)
        tx_hash = self.w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        
        tx_hex = self.w3.to_hex(tx_hash)
        print(f"Approve enviado: {tx_hex}")
        
        # Esperamos confirmación (máximo 5 min)
        self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=300)
        
        return tx_hex

    def send_airdrop(self, airdrop_address, token_address, recipients, amounts):
        """
        Llama a airdropTokens() en el smart contract Airdrop.
        Le pasa la lista de destinatarios y cantidades, y el contrato hace un
        bucle en la blockchain ejecutando transferFrom() por cada destinatario.
        Requiere que antes se haya hecho approve() con suficiente allowance.
        """
        abi, _ = self._get_contract_data('Airdrop')
        airdrop_contract = self.w3.eth.contract(address=Web3.to_checksum_address(airdrop_address), abi=abi)

        # Boost gas price
        current_gas_price = self.w3.eth.gas_price
        gas_price = int(current_gas_price * 1.2)

        tx = airdrop_contract.functions.airdropTokens(
            Web3.to_checksum_address(token_address),
            [Web3.to_checksum_address(r) for r in recipients],
            amounts
        ).build_transaction({
            'from': self.account.address,
            'nonce': self.w3.eth.get_transaction_count(self.account.address),
            'gas': 3000000,
            'gasPrice': gas_price,
            'chainId': self.w3.eth.chain_id
        })

        signed_tx = self.w3.eth.account.sign_transaction(tx, private_key=self.private_key)
        tx_hash = self.w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        
        tx_hex = self.w3.to_hex(tx_hash)
        print(f"Airdrop enviado: {tx_hex}")
        
        self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=300)
        return tx_hex

    # --- FUNCIONES PARA EL DASHBOARD ---

    def get_contract_eth_balance(self, contract_address):
        """
        Consulta el balance de ETH que tiene acumulado un contrato.
        No llama a ninguna función del contrato, directamente pregunta al nodo
        cuánto ETH hay en esa dirección (los contratos también tienen balance).
        """
        balance_wei = self.w3.eth.get_balance(Web3.to_checksum_address(contract_address))
        return self.w3.from_wei(balance_wei, 'ether')

    def get_donors_list(self, contract_address):
        """
        Llama a getDonors() en el contrato Airdrop.
        """
        abi, _ = self._get_contract_data('Airdrop')
        contract = self.w3.eth.contract(address=Web3.to_checksum_address(contract_address), abi=abi)
        return contract.functions.getDonors().call()

    def get_donors_data(self, contract_address):
        """
        [NUEVA FUNCIÓN] Devuelve una lista de diccionarios con la dirección y la cantidad total 
        donada por cada usuario. Útil para el "Fund Me" del dashboard.
        """
        donors = self.get_donors_list(contract_address)
        abi, _ = self._get_contract_data('Airdrop')
        contract = self.w3.eth.contract(address=Web3.to_checksum_address(contract_address), abi=abi)
        
        data = []
        for d in donors:
            amount_wei = contract.functions.donationAmount(Web3.to_checksum_address(d)).call()
            data.append({
                "address": d,
                "amount": float(self.w3.from_wei(amount_wei, 'ether'))
            })
        return data

    def donate_eth(self, contract_address, amount_eth):
        """
        Envía ETH directamente a la dirección del contrato.
        El contrato tiene una función receive() que se activa automáticamente
        cuando recibe ETH sin datos. Eso registra al donante en su lista interna.
        """
        # Boost gas price
        current_gas_price = self.w3.eth.gas_price
        gas_price = int(current_gas_price * 1.2)

        tx = {
            'to': Web3.to_checksum_address(contract_address),
            'value': self.w3.to_wei(amount_eth, 'ether'),
            'gas': 200000,
            'gasPrice': gas_price,
            'nonce': self.w3.eth.get_transaction_count(self.account.address),
            'chainId': self.w3.eth.chain_id
        }
        signed_tx = self.w3.eth.account.sign_transaction(tx, private_key=self.private_key)
        tx_hash = self.w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        
        tx_hex = self.w3.to_hex(tx_hash)
        print(f"Donación enviada: {tx_hex}")
        
        self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=300)
        return tx_hex

    # --- NUEVAS FUNCIONES ---

    def get_token_balance(self, token_address, wallet_address=None):
        """
        Consulta cuántos tokens ERC20 tiene una billetera.
        Si no se especifica wallet_address, usa la billetera propia.
        Llama a balanceOf() del contrato CosaToken (lectura, sin gas).
        Muy útil para comprobar si tienes suficientes tokens antes de lanzar un airdrop.
        Devuelve el balance en unidades enteras (dividido entre 10^18 decimales).
        """
        abi, _ = self._get_contract_data('CosaToken')
        token_contract = self.w3.eth.contract(address=Web3.to_checksum_address(token_address), abi=abi)
        address_to_check = wallet_address if wallet_address else self.account.address
        balance_raw = token_contract.functions.balanceOf(Web3.to_checksum_address(address_to_check)).call()
        return balance_raw / 10**18

    def get_token_allowance(self, token_address, spender_address):
        """
        Comprueba cuántos tokens tiene permitido gastar el contrato Airdrop en nuestro nombre.
        Llama a allowance(owner, spender) del contrato CosaToken (lectura, sin gas).
        Útil para verificar si el approve() se hizo correctamente antes del airdrop,
        o si ya se agotó el permiso tras envíos anteriores.
        Devuelve el allowance en unidades enteras.
        """
        abi, _ = self._get_contract_data('CosaToken')
        token_contract = self.w3.eth.contract(address=Web3.to_checksum_address(token_address), abi=abi)
        allowance_raw = token_contract.functions.allowance(
            self.account.address,
            Web3.to_checksum_address(spender_address)
        ).call()
        return allowance_raw / 10**18

    def get_donor_amount(self, airdrop_address, donor_address):
        """
        Consulta cuánto ETH ha donado una dirección concreta al contrato Airdrop.
        El contrato tiene un mapping público donationAmount(address) que guarda
        el acumulado de cada donante. Es lectura pura, no consume gas.
        Devuelve el valor en ETH.
        """
        abi, _ = self._get_contract_data('Airdrop')
        contract = self.w3.eth.contract(address=Web3.to_checksum_address(airdrop_address), abi=abi)
        amount_wei = contract.functions.donationAmount(Web3.to_checksum_address(donor_address)).call()
        return self.w3.from_wei(amount_wei, 'ether')

    def withdraw_funds(self, airdrop_address):
        """
        Llama a withdrawFunds() en el contrato Airdrop.
        Solo puede ejecutarlo el owner (quien desplegó el contrato), si otro lo intenta
        el contrato lanza un require() y la tx falla.
        Transfiere todo el ETH acumulado por donaciones al wallet del owner.
        """
        if not self.account:
            raise Exception("Configura tu Private Key.")
        
        abi, _ = self._get_contract_data('Airdrop')
        contract = self.w3.eth.contract(address=Web3.to_checksum_address(airdrop_address), abi=abi)

        tx = contract.functions.withdrawFunds().build_transaction({
            'from': self.account.address,
            'nonce': self.w3.eth.get_transaction_count(self.account.address),
            'gas': 100000,
            'gasPrice': self.w3.eth.gas_price
        })

        signed_tx = self.w3.eth.account.sign_transaction(tx, private_key=self.private_key)
        tx_hash = self.w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        self.w3.eth.wait_for_transaction_receipt(tx_hash)
        return self.w3.to_hex(tx_hash)

    def send_eth_airdrop(self, airdrop_address, recipients, amounts_eth):
        """
        [NUEVA FUNCIÓN] Distribuye ETH desde el balance del contrato Airdrop a una lista de direcciones.
        Llama a airdropETH() en el smart contract (función nueva que hay que añadir al .sol).
        El flujo sería: varios donantes envían ETH al contrato → el owner lo redistribuye
        a quien quiera usando esta función. Es el airdrop pero en ETH en lugar de tokens.
        - recipients: lista de direcciones destino.
        - amounts_eth: lista de cantidades en ETH (ej: [0.1, 0.2]).
        """
        if not self.account:
            raise Exception("Configura tu Private Key.")

        abi, _ = self._get_contract_data('Airdrop')
        contract = self.w3.eth.contract(address=Web3.to_checksum_address(airdrop_address), abi=abi)

        amounts_wei = [self.w3.to_wei(a, 'ether') for a in amounts_eth]

        tx = contract.functions.airdropETH(
            [Web3.to_checksum_address(r) for r in recipients],
            amounts_wei
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
