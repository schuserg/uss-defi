import json
from pathlib import Path
from web3 import Web3
from dotenv import load_dotenv
import os
from datetime import datetime

load_dotenv()

# Web3 setup
w3 = Web3(Web3.HTTPProvider(os.getenv("WEB3_PROVIDER")))
account = w3.eth.account.from_key(os.getenv("PRIVATE_KEY"))
w3.eth.default_account = account.address

# Paths
build_dir = Path(__file__).resolve().parent / "build"
artifacts_dir = build_dir / "artifacts"

output_addresses = build_dir / "deployed_addresses.json"
output_log = build_dir / "deployment_report.json"

# Load contracts metadata
def load_metadata(contract_name):
    abi_path = artifacts_dir / f"{contract_name}.abi.json"
    bin_path = artifacts_dir / f"{contract_name}.bin"
    meta_path = artifacts_dir / f"{contract_name}.metadata.json"
    abi = json.loads(abi_path.read_text())
    bytecode = bin_path.read_text()
    metadata = json.loads(meta_path.read_text())
    return abi, bytecode, metadata, abi_path

# Deploy one contract
def deploy_contract(name, abi, bytecode, constructor_args=[]):
    contract = w3.eth.contract(abi=abi, bytecode=bytecode)
    tx = contract.constructor(*constructor_args).build_transaction({
        'from': w3.eth.default_account,
        'nonce': w3.eth.get_transaction_count(w3.eth.default_account, 'pending'),
        'gas': 3000000,
        'gasPrice': w3.to_wei('5', 'gwei')
    })
    signed = w3.eth.account.sign_transaction(tx, private_key=os.getenv("PRIVATE_KEY"))
    tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    return receipt, tx_hash.hex()

# Deployment flow
contracts = {}
report = {}

# Deploy USSToken
abi, bytecode, metadata, abi_path = load_metadata("USSToken")
receipt, tx_hash = deploy_contract("USSToken", abi, bytecode)
usstoken_address = receipt.contractAddress
contracts["USSToken"] = usstoken_address
report["USSToken"] = {
    "address": usstoken_address,
    "tx_hash": tx_hash,
    "gas_used": receipt.gasUsed,
    "constructor_args": [],
    "abi_path": str(abi_path),
    "deployed_at": datetime.utcnow().isoformat() + "Z"
}

# Deploy FarmToken
abi, bytecode, metadata, abi_path = load_metadata("FarmToken")
receipt, tx_hash = deploy_contract("FarmToken", abi, bytecode)
farmtoken_address = receipt.contractAddress
contracts["FarmToken"] = farmtoken_address
report["FarmToken"] = {
    "address": farmtoken_address,
    "tx_hash": tx_hash,
    "gas_used": receipt.gasUsed,
    "constructor_args": [],
    "abi_path": str(abi_path),
    "deployed_at": datetime.utcnow().isoformat() + "Z"
}

# Deploy USSStaking
abi, bytecode, metadata, abi_path = load_metadata("USSStaking")
receipt, tx_hash = deploy_contract("USSStaking", abi, bytecode, [usstoken_address, farmtoken_address, w3.eth.default_account])
staking_address = receipt.contractAddress
contracts["USSStaking"] = staking_address
report["USSStaking"] = {
    "address": staking_address,
    "tx_hash": tx_hash,
    "gas_used": receipt.gasUsed,
    "constructor_args": [usstoken_address, farmtoken_address],
    "abi_path": str(abi_path),
    "deployed_at": datetime.utcnow().isoformat() + "Z"
}

# Save outputs
output_addresses.write_text(json.dumps(contracts, indent=2))
output_log.write_text(json.dumps(report, indent=2))

print("\u2705 All contracts deployed. Addresses saved to:", output_addresses)
print("\u2705 Deployment report saved to:", output_log)

