import json
import os
from typing import Dict, Any

def get_all_standards() -> Dict[str, Any]:
    """
    Load all JSON standard files and merge them into a unified dictionary.
    
    Returns:
        Dict containing all standards merged together
    """
    standards = {}
    standards_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "standards")
    
    # List of standard files to load
    standard_files = [
        "sdlc.json",
        "agile.json", 
        "devops.json",
        "itil.json",
        "iso.json",
        "pmbok.json"
    ]
    
    for filename in standard_files:
        file_path = os.path.join(standards_dir, filename)
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # Use filename without extension as key
                standard_name = filename.replace('.json', '')
                standards[standard_name] = data
        except FileNotFoundError:
            print(f"Warning: {filename} not found")
            standards[filename.replace('.json', '')] = {}
        except json.JSONDecodeError as e:
            print(f"Error parsing {filename}: {e}")
            standards[filename.replace('.json', '')] = {}
    
    return standards
