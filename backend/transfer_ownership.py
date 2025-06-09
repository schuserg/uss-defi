from web3 import Web3
import json
import os
from dotenv import load_dotenv

load_dotenv()

# Configuration from .env
WEB3_PROVIDER = os.getenv("WEB3_PROVIDER")
PRIVATE_KEY = os.getenv("PRIVATE_KEY")
PUBLIC_KEY = os.getenv("PUBLIC_KEY")
CHAIN_ID = int(os.getenv("CHAIN_ID"))
FARMTOKEN_ADDRESS = os.getenv("FARMTOKEN_ADDRESS")
USSSTAKING_ADDRESS = os.getenv("USSSTAKING_ADDRESS")

# Minimal ABI with transferOwnership(address) function
FARMTOKEN_ABI = [
    {
        "inputs": [{"internalType": "address", "name": "newOwner", "type": "address"}],
        "name": "transferOwnership",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    }
]

# Connect to the network
w3 = Web3(Web3.HTTPProvider(WEB3_PROVIDER))
assert w3.is_connected(), "❌ Failed to connect to RPC"

# Connect to the contract
farm_token = w3.eth.contract(address=FARMTOKEN_ADDRESS, abi=FARMTOKEN_ABI)

# Prepare the transaction
nonce = w3.eth.get_transaction_count(PUBLIC_KEY)
tx = farm_token.functions.transferOwnership(USSSTAKING_ADDRESS).build_transaction({
    "from": PUBLIC_KEY,
    "nonce": nonce,
    "chainId": CHAIN_ID,
    "gas": 100000,
    "gasPrice": w3.to_wei("5", "gwei")
})

# Sign and send the transaction
signed_tx = w3.eth.account.sign_transaction(tx, private_key=PRIVATE_KEY)
tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)

print(f"📤 Transaction sent: {tx_hash.hex()}")
receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
print(f"✅ Ownership transferred → USStaking\nTransaction confirmed: {receipt.transactionHash.hex()}")

