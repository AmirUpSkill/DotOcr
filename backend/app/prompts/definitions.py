import json
from pathlib import Path
from typing import List, Dict, Any

def load_prompts() -> List[Dict[str, Any]]:
    """
    Load available prompts from definitions.json.
    Returns: List of prompt dicts (id, name, description).
    """
    file_path = Path(__file__).parent / "definitions.json"
    if not file_path.exists():
        raise FileNotFoundError("Prompt definitions file not found")
    
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    return data