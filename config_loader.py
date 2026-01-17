import json

# Load system configuration
def load_config(path="config.json"):
    try:
        with open(path, "r", encoding="utf-8") as f:
            config = json.load(f)
        print(" Configuration loaded successfully.")
        return config
    except FileNotFoundError:
        print(" config.json not found. Please create it first.")
        return {}
    except json.JSONDecodeError as e:
        print(f" Error decoding JSON: {e}")
        return {}

# Example usage
if __name__ == "__main__":
    config = load_config()
    if config:
        print("System Instruction:")
        print(config.get("system_instruction", " No system_instruction found in config.json"))
import json

# Load system configuration
def load_config(path="config.json"):
    try:
        with open(path, "r", encoding="utf-8") as f:
            config = json.load(f)
        print(" Configuration loaded successfully.")
        return config
    except FileNotFoundError:
        print(" config.json not found. Please create it first.")
        return {}
    except json.JSONDecodeError as e:
        print(f" Error decoding JSON: {e}")
        return {}

# Example usage
if __name__ == "__main__":
    config = load_config()
    if config:
        print("System Instruction:")
        print(config.get("system_instruction", " No system_instruction found in config.json"))