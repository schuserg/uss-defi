import json
import time
import os
from dotenv import load_dotenv
from web3 import Web3
from datetime import datetime

# Load .env variables
load_dotenv()
WEB3_PROVIDER = os.getenv("WEB3_PROVIDER")
STAKING_ADDRESS = os.getenv("USSSTAKING_ADDRESS")

# Connect to network
w3 = Web3(Web3.HTTPProvider(WEB3_PROVIDER))
assert w3.is_connected(), "❌ RPC unavailable"

# Load ABI from file
with open("build/artifacts/USSStaking.abi.json", "r") as f:
    abi = json.load(f)

# Contract
contract = w3.eth.contract(address=STAKING_ADDRESS, abi=abi)

# Events
event_names = ["Staked", "Claimed", "Withdrawn", "WithdrawnAll"]
log_file = "logs/mint_log.json"
os.makedirs("logs", exist_ok=True)

# Starting block
start_block = w3.eth.block_number

def save_log(entry):
    try:
        with open(log_file, "r") as f:
            logs = json.load(f)
    except FileNotFoundError:
        logs = []

    logs.append(entry)
    with open(log_file, "w") as f:
        json.dump(logs, f, indent=2)

def format_amount(value):
    return float(value) / 1e18

print("📡 Listener started. Waiting for events...")

while True:
    latest = w3.eth.block_number
    for event_name in event_names:
        event = getattr(contract.events, event_name)
        try:
            logs = event().get_logs(fromBlock=start_block, toBlock=latest)
            for log in logs:
                entry = {
                    "event": event_name,
                    "block": log.blockNumber,
                    "txHash": log.transactionHash.hex(),
                    "args": {k: (format_amount(v) if isinstance(v, int) else v) for k, v in dict(log.args).items()},
                    "timestamp": datetime.utcnow().isoformat() + "Z"
                }
                save_log(entry)
                print(f"📥 {event_name}: {entry}")
        except Exception as e:
            print(f"⚠️ Error while fetching {event_name}: {e}")
    start_block = latest + 1
    time.sleep(5)
