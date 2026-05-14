from __future__ import annotations
from pathlib import Path
from typing import Any
import yaml

TEMPLATES_DIR = Path(__file__).parent.parent / "templates"

def load_template(name: str) -> dict[str, Any]:
    path = TEMPLATES_DIR / f"{name}.yaml"
    if not path.exists():
        raise FileNotFoundError(f"Template not found: {name}")
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def list_templates() -> list[dict[str, str]]:
    result = []
    for f in sorted(TEMPLATES_DIR.glob("*.yaml")):
        data = yaml.safe_load(f.read_text(encoding="utf-8"))
        result.append({"id": f.stem, "name": data.get("name", f.stem)})
    return result
