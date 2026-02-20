# library imports
import os
import json

# load JSON data from a file, output: list
def load_json(file_name):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    input_dir = os.path.join(base_dir, "..", "output")
    file_path = os.path.join(input_dir, f"{file_name}.json")

    if not os.path.exists(file_path):
        print(f"[json_funs] Error: {file_name}.json not found in output folder.")
        return []
    else:
        print(f"[json_funs] Loading data from {file_name}.json ...")
        with open(file_path, mode='r', encoding='utf-8') as json_file:
            data = json.load(json_file)
        print(f"[json_funs] Loaded {len(data)} records.")
        return data
    
# save data to a JSON file, procedure
def save_json(data, file_name):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    output_dir = os.path.join(base_dir, "..", "output")
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    file_path = os.path.join(output_dir, f"{file_name}.json")

    with open(file_path, mode='w', encoding='utf-8') as json_file:
        json.dump(data, json_file, indent=4)
    print(f"[json_funs] Saved {len(data)} records to {file_name}.json in output folder.")    