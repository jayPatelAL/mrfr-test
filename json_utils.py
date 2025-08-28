import json
import logging

def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def save_json(data, path):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def is_valid_text_content(value):
    if not isinstance(value, str):
        return False
    if value.strip() == "" or value.strip().lower() in ["n/a", "none"]:
        return False
    if any(char.isalpha() for char in value):
        return True
    return False

def extract_sections(obj):
    results = []
    if isinstance(obj, dict):
        title = obj.get("title")
        content_text = obj.get("description") or obj.get("body")
        if title and is_valid_text_content(content_text):
            results.append({"key": title, "text": content_text})
        for v in obj.values():
            results.extend(extract_sections(v))
    elif isinstance(obj, list):
        for item in obj:
            results.extend(extract_sections(item))
    return results