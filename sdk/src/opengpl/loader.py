# src/opengpl/loader.py
import json
import pathlib
import yaml
import jsonschema

_SCHEMA_DIR = pathlib.Path(__file__).parent / "schemas"


def _get_schema(version: str) -> dict:
    schema_path = _SCHEMA_DIR / f"opengpl-v{version}.json"
    if schema_path.exists():
        return json.loads(schema_path.read_text())
    import urllib.request
    url = f"https://opengpl.org/schemas/v{version}/opengpl.schema.json"
    return json.loads(urllib.request.urlopen(url).read())


def load(path: str) -> dict:
    """Load and validate a .gpl policy file. Returns parsed dict."""
    p = pathlib.Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Policy file not found: {path}")
    policy = yaml.safe_load(p.read_text())
    validate_schema(policy)
    return policy


def validate_schema(policy: dict) -> None:
    """Validate a policy dict against the OpenGPL JSON Schema."""
    version = policy.get("opengpl", "0.1")
    schema = _get_schema(version)
    validator = jsonschema.Draft202012Validator(schema)
    errors = list(validator.iter_errors(policy))
    if errors:
        # Report the first (most relevant) error
        raise ValueError(f"Policy failed schema validation: {errors[0].message}") from errors[0]
