import solcx
import json
import os

def compile_contracts():
    print("Preparando compilador Solidity v0.8.20...")
    solcx.install_solc('0.8.20')
    solcx.set_solc_version('0.8.20')

    contracts = ['CosaToken.sol', 'Airdrop.sol']
    compiled_data = {}

    for contract_file in contracts:
        file_path = os.path.join(os.path.dirname(__file__), contract_file)
        if not os.path.exists(file_path):
            print(f"Error: No se encuentra {contract_file}")
            continue

        print(f"Compilando {contract_file}...")
        compiled_sol = solcx.compile_files(
            [file_path],
            output_values=['abi', 'bin']
        )

        for contract_id, interface in compiled_sol.items():
            name = contract_id.split(':')[-1]
            compiled_data[name] = interface

    # Guardar todos los contratos en un solo JSON
    out_path = os.path.join(os.path.dirname(__file__), 'compiled_contracts.json')
    with open(out_path, 'w') as f:
        json.dump(compiled_data, f)
    
    print(f"Compilacion exitosa. Datos guardados en {out_path}")

if __name__ == "__main__":
    compile_contracts()
