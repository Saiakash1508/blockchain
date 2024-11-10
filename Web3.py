from solcx import compile_standard, install_solc
import json
from web3 import Web3
import os
from dotenv import load_dotenv

def deploy():
    load_dotenv()

    with open("./contracts/newContract.sol", 'r') as file:
        new_contract_file = file.read()
    install_solc("0.8.19")
    compiled_sol = compile_standard(
        {
            "language": "Solidity",
            "sources": {"newContract.sol": {"content": new_contract_file}},
            "settings": {
                "outputSelection": {
                    "*": {
                        "*": ["abi", "metadata", "evm.bytecode", "evm.sourceMap"]
                    }
                }
            },
        },
        solc_version="0.8.19"
    )

    with open("compiled_code.json", "w") as file:
        json.dump(compiled_sol, file)

    bytecode = compiled_sol["contracts"]["newContract.sol"]["newContract"]["evm"]["bytecode"]["object"]
    abi = compiled_sol["contracts"]["newContract.sol"]["newContract"]["abi"]

    w3 = Web3(Web3.HTTPProvider(os.getenv("PROVIDER")))
    chain_id = int(os.getenv("CHAINID"))  # Parse the chain ID as an integer
    my_address = os.getenv("ACCOUNT")
    private_key = os.getenv("PRIVATE_KEY")

    newContract = w3.eth.contract(abi=abi, bytecode=bytecode)

    nonce = w3.eth.get_transaction_count(my_address)

    transaction = newContract.constructor().build_transaction({
        "chainId": chain_id,
        "gas": 2000000,  # You can adjust the gas value as neededpythonpip3 install py-solc-x
        
        "gasPrice": w3.to_wei("20", "gwei"),  # You can adjust the gas price as needed
        "nonce": nonce,
    })

    signed_txn = w3.eth.account.sign_transaction(transaction, private_key=private_key)

    print("Deploying Contract!")
    tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
    print("Waiting for transaction to finish...")
    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

    return tx_receipt.contractAddress

if __name__ == '__main__':
    contractAddress = deploy()
    print({contractAddress})
