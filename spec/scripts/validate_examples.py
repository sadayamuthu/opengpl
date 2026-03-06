#!/usr/bin/env python3
"""Validate all .gpl example policies against the OpenGPL JSON Schema."""
import json
import pathlib
import sys
import yaml
import jsonschema

REPO_ROOT = pathlib.Path(__file__).parent.parent
SCHEMA_PATH = REPO_ROOT / "schema" / "opengpl-v0.1.json"
EXAMPLES_DIR = REPO_ROOT / "examples"


def main():
    schema = json.loads(SCHEMA_PATH.read_text())
    examples = sorted(EXAMPLES_DIR.glob("*.gpl"))

    if not examples:
        print("No .gpl files found in examples/")
        sys.exit(1)

    errors = []
    for path in examples:
        try:
            docs = list(yaml.safe_load_all(path.read_text()))
            for doc in docs:
                if doc is not None:
                    jsonschema.validate(doc, schema)
            print(f"  ✓ {path.name}")
        except (yaml.YAMLError, jsonschema.ValidationError) as e:
            errors.append(f"  ✗ {path.name}: {e}")
            print(f"  ✗ {path.name}: {e}")

    print(f"\n{len(examples) - len(errors)}/{len(examples)} policies valid")

    if errors:
        sys.exit(1)


if __name__ == "__main__":
    main()
