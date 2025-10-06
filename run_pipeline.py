import json
import os
from contract_pipeline import ContractPipeline

# Load DB config
with open("config/config.json", "r", encoding="utf-8") as f:
    db_config = json.load(f)

pipeline = ContractPipeline(db_config)

# Process all .txt files in the contracts folder
folder = "data/raw"
for filename in sorted(os.listdir(folder)):
    if not filename.lower().endswith(".txt"):
        continue
    path = os.path.join(folder, filename)
    with open(path, "r", encoding="utf-8") as f:
        text = f.read()
    print(f"\n--- Processing file: {filename}")
    pipeline.process_contract(text, filename)
