# src/opengpl/loader.py
import json
import pathlib

import jsonschema
import yaml

_SCHEMA_DIR = pathlib.Path(__file__).parent / "schemas"


def _get_schema(version: str) -> dict:
    parts = version.split(".") if isinstance(version, str) else []
    if len(parts) != 2 or any(
        not part.isascii()
        or not part.isdigit()
        or (len(part) > 1 and part.startswith("0"))
        for part in parts
    ):
        raise ValueError("Invalid OpenGPL schema version")
    schema_path = _SCHEMA_DIR / f"opengpl-v{version}.json"
    if schema_path.exists():
        return json.loads(schema_path.read_text())
    import urllib.request

    url = f"https://opengpl.org/schema/v{version}/schema.json"
    return json.loads(urllib.request.urlopen(url).read())


def load_all(path: str) -> list[dict]:
    """Load and validate every policy in a .gpl file.

    A file may hold several policies separated by ``---`` (see
    ``examples/multi-agent.gpl``).
    """
    p = pathlib.Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Policy file not found: {path}")
    try:
        docs = [d for d in yaml.safe_load_all(p.read_text()) if d is not None]
    except yaml.YAMLError as e:
        raise ValueError(f"Invalid YAML in {path}: {e}") from e
    if not docs:
        raise ValueError(f"No policy found in {path}")
    for doc in docs:
        if not isinstance(doc, dict):
            raise ValueError(f"Policy in {path} must be a YAML mapping")
        validate_schema(doc)
    return docs


def load(path: str) -> dict:
    """Load and validate a single-policy .gpl file. Returns parsed dict."""
    docs = load_all(path)
    if len(docs) > 1:
        names = ", ".join(str(d.get("policy", "?")) for d in docs)
        raise ValueError(
            f"{path} contains {len(docs)} policies ({names}); "
            "PolicyEngine takes one policy per file. Split the file, "
            "or use opengpl.loader.load_all()."
        )
    return docs[0]


def validate_schema(policy: dict) -> None:
    """Validate a policy dict against the OpenGPL JSON Schema."""
    version = policy.get("opengpl", "0.1")
    schema = _get_schema(version)
    validator = jsonschema.Draft202012Validator(schema)
    errors = list(validator.iter_errors(policy))
    if errors:
        # Report the first (most relevant) error
        raise ValueError(f"Policy failed schema validation: {errors[0].message}") from errors[0]
