import json
from pathlib import Path

def extract_artifacts():
    build_dir = Path(__file__).resolve().parent / "build"
    compiled_path = build_dir / "compiled_output.json"
    artifacts_dir = build_dir / "artifacts"
    artifacts_dir.mkdir(exist_ok=True)

    with open(compiled_path) as f:
        compiled = json.load(f)

    contracts = compiled.get("contracts", {})

    for file_name, file_contracts in contracts.items():
        for contract_name, data in file_contracts.items():
            abi = data.get("abi")
            bytecode = data.get("evm", {}).get("bytecode", {}).get("object")
            metadata = data.get("metadata")

            if abi:
                abi_path = artifacts_dir / f"{contract_name}.abi.json"
                with open(abi_path, "w") as f:
                    json.dump(abi, f, indent=2)
                print(f"✅ ABI saved: {abi_path.name}")

            if bytecode:
                bin_path = artifacts_dir / f"{contract_name}.bin"
                with open(bin_path, "w") as f:
                    f.write(bytecode)
                print(f"✅ Bytecode saved: {bin_path.name}")

            if metadata:
                metadata_path = artifacts_dir / f"{contract_name}.metadata.json"
                with open(metadata_path, "w") as f:
                    json.dump(json.loads(metadata), f, indent=2)
                print(f"✅ Metadata saved: {metadata_path.name}")

if __name__ == "__main__":
    extract_artifacts()

