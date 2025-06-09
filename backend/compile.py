
import solcx
from solcx import compile_standard
import json
from pathlib import Path

solcx.install_solc("0.8.20")

def compile_contracts():
    contract_dir = Path(__file__).resolve().parent.parent / "contracts"
    sources = {}

    # Directories to fully ignore
    IGNORED_DIRS = ["@openzeppelin", "node_modules"]

    def is_ignored(file: Path):
        # Ignore if any part matches ignored directories
        if any(part in IGNORED_DIRS for part in file.parts):
            return True
        # In utils folder, keep only ReentrancyGuard.sol
        if "utils" in file.parts and file.name != "ReentrancyGuard.sol":
            return True
        return False

    for file in contract_dir.rglob("*.sol"):
        if is_ignored(file):
            continue
        sources[file.name] = {
            "urls": [str(file)],
            "content": file.read_text()
        }

    compiled = compile_standard(
        {
            "language": "Solidity",
            "sources": {k: {"content": v["content"]} for k, v in sources.items()},
            "settings": {
                "outputSelection": {
                    "*": {
                        "*": ["abi", "metadata", "evm.bytecode", "evm.sourceMap"]
                    }
                }
            },
        },
        solc_version="0.8.20",
        base_path=str(contract_dir)
    )

    build_dir = Path(__file__).resolve().parent / "build"
    build_dir.mkdir(exist_ok=True)

    with open(build_dir / "compiled_output.json", "w") as f:
        json.dump(compiled, f, indent=2)

    print("✅ Contracts compiled and saved to build/compiled_output.json")

if __name__ == "__main__":
    compile_contracts()
