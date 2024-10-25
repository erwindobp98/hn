from web3 import Web3
import time
import os

# Fungsi untuk menampilkan teks di tengah layar
def center_text(text):
    terminal_width = os.get_terminal_size().columns
    lines = text.splitlines()
    centered_lines = [line.center(terminal_width) for line in lines]
    return "\n".join(centered_lines)

# Deskripsi teks
description = """
HANA NETWORK
BY : PUCUK KANGKUNG KONTOL BABI
- KONTOL NGENTOD ANJING
"""

# Output
print(center_text(description))
print("\n\n")

# Network information (Base)
network = {
    'name': 'Base',
    'rpc_url': 'https://base.llamarpc.com',
    'chain_id': 8453,
    'contract_address': '0xC5bf05cD32a14BFfb705Fb37a9d218895187376c'
}

# Wallet details
wallet = {
    'private_key': '',  # Tambahkan private key
    'address': ''       # Tambahkan alamat wallet
}

# ABI for the contract
contract_abi = [
    {
        "constant": False,
        "inputs": [],
        "name": "depositETH",
        "outputs": [],
        "payable": True,
        "stateMutability": "payable",
        "type": "function"
    }
]

# Function to deposit ETH using the depositETH function in the contract
def deposit_to_contract(network, private_key, from_address, amount_in_eth):
    web3 = Web3(Web3.HTTPProvider(network['rpc_url']))
    if not web3.is_connected():
        print(f"Cannot connect to network {network['name']}")
        return None

    contract = web3.eth.contract(address=network['contract_address'], abi=contract_abi)
    nonce = web3.eth.get_transaction_count(from_address)

    # Convert amount to Wei
    transaction_value = web3.to_wei(amount_in_eth, 'ether')

    # Estimate gas
    try:
        gas_estimate = contract.functions.depositETH().estimate_gas({'from': from_address, 'value': transaction_value})
        gas_limit = gas_estimate + 10000  # Tambahkan buffer gas
    except Exception as e:
        print(f"Error estimating gas: {e}")
        return None

    # Gas price and fees
    current_gas_price = web3.eth.gas_price
    max_priority_fee_per_gas = int(min(current_gas_price * 0.1, web3.to_wei(0.052, 'gwei')))
    max_fee_per_gas = int(current_gas_price + max_priority_fee_per_gas)

    # Check wallet balance
    balance = web3.eth.get_balance(from_address)
    total_cost = transaction_value + (gas_limit * max_fee_per_gas)
    if balance < total_cost:
        print(f"Insufficient funds. Balance: {web3.from_wei(balance, 'ether')} ETH, Required: {web3.from_wei(total_cost, 'ether')} ETH")
        return None

    # Transaction details for calling depositETH
    transaction = contract.functions.depositETH().build_transaction({
        'nonce': nonce,
        'value': transaction_value,
        'gas': gas_limit,
        'maxFeePerGas': max_fee_per_gas,
        'maxPriorityFeePerGas': max_priority_fee_per_gas,
        'chainId': network['chain_id'],
    })

    # Sign and send transaction
    try:
        signed_txn = web3.eth.account.sign_transaction(transaction, private_key)
        tx_hash = web3.eth.send_raw_transaction(signed_txn.rawTransaction)
        return web3.to_hex(tx_hash)
    except Exception as e:
        print(f"Transaction error: {e}")
        return None

def main():
    amount_in_eth = 0.00000000001  # Masukan eth base yang ingin dimasukan

    while True:
        # Start timer
        start_time = time.time()

        # Execute deposit
        tx_hash = deposit_to_contract(network, wallet['private_key'], wallet['address'], amount_in_eth)

        # End timer and calculate duration
        end_time = time.time()
        duration = end_time - start_time

        if tx_hash:
            print(f"Network: {network['name']} | Tx Hash: {tx_hash}")
        else:
            print("Transaction failed")

        print(f"Transaction execution time: {duration:.2f} seconds")
        
        # jeda untuk transaksi
        time.sleep(600)  # 10 menit

if __name__ == "__main__":
    main()
