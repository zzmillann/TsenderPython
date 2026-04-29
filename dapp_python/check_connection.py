from web3 import Web3
import os
from dotenv import load_dotenv

load_dotenv()

rpc_url = os.getenv("RPC_URL", "https://rpc.sepolia.org")
private_key = os.getenv("PRIVATE_KEY")

w3 = Web3(Web3.HTTPProvider(rpc_url))

if not w3.is_connected():
    print(f"Error: No se pudo conectar a {rpc_url}")
else:
    print(f"Conectado a {rpc_url}")
    if private_key:
        account = w3.eth.account.from_key(private_key)
        balance = w3.eth.get_balance(account.address)
        print(f"Dirección: {account.address}")
        print(f"Balance: {w3.from_wei(balance, 'ether')} ETH")
        print(f"Nonce: {w3.eth.get_transaction_count(account.address)}")
        print(f"Gas Price: {w3.eth.gas_price / 10**9} Gwei")
    else:
        print("No hay Private Key en el .env")
