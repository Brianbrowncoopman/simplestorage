from solcx import compile_standard, install_solc
import json
from web3 import Web3
import os
from dotenv import load_dotenv

load_dotenv()

with open("./SimpleStorage.sol", "r") as file:
    simple_storage_file = file.read()


# compilar
install_solc("0.6.0")
compiled_sol = compile_standard(
    {
        "language": "Solidity",
        "sources": {"SimpleStorage.sol": {"content": simple_storage_file}},
        "settings": {
            "outputSelection": {
                "*": {
                    "*": ["abi", "metadata", "evm.bytecode", "evm.bytecode.sourceMap"]
                }
            }
        },
    },
    solc_version="0.6.0",
)


with open("compliled_code.json", "w") as file:
    json.dump(compiled_sol, file)

# Bytecode
bytecode = compiled_sol["contracts"]["SimpleStorage.sol"]["SimpleStorage"]["evm"][
    "bytecode"
]["object"]

# abi
abi = json.loads(
    compiled_sol["contracts"]["SimpleStorage.sol"]["SimpleStorage"]["metadata"]
)["output"]["abi"]


# coneccion a ganache
w3 = Web3(Web3.HTTPProvider("http://172.23.0.1:7545"))  # url ganache
chain_id = 1337
my_address = "0x0d4B912b1440C877e784fd7e251c9afFf7116e7B"  # direccion
private_key = os.getenv("PRIVATE_KEY")


SimpleStorage = w3.eth.contract(abi=abi, bytecode=bytecode)


nonce = w3.eth.getTransactionCount(my_address)

# construir
# firmar
# enviar

transaction = SimpleStorage.constructor().buildTransaction(
    {
        "chainId": chain_id,
        "gasPrice": w3.eth.gas_price,
        "from": my_address,
        "nonce": nonce,
    }
)

signed_txn = w3.eth.account.sign_transaction(transaction, private_key=private_key)


tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
print("esperando que termine la transaccion...")
tx_recipt = w3.eth.wait_for_transaction_receipt(tx_hash)


# working with deployed contract
simple_storage = w3.eth.contract(address=tx_recipt.contractAddress, abi=abi)

# call => simula un llamado para obterne valor / no cuesta gass
# Transact =>  genera cambos y cuesta gas
print(simple_storage.functions.retrieve().call())


store_transaction = simple_storage.functions.store(15).buildTransaction(
    {
        "chainId": chain_id,
        "gasPrice": w3.eth.gas_price,
        "from": my_address,
        "nonce": nonce + 1,
    }
)

signed_store_txn = w3.eth.account.sign_transaction(
    store_transaction, private_key=private_key
)
print("Updating storedar value")

t_hash = w3.eth.send_raw_transaction(signed_store_txn.rawTransaction)
tx_recipt = w3.eth.wait_for_transaction_receipt(t_hash)

print(simple_storage.functions.retrieve().call())
