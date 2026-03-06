# opengpl-sdk

The Python SDK for [OpenGPL](https://opengpl.org) policy enforcement.

## Install

```bash
pip install opengpl-sdk
```

## Quick start

```python
from opengpl import PolicyEngine

engine = PolicyEngine("policy.gpl")
result = engine.check_input("Hello, what is my balance?")
print(result.passed)  # True or False
```

## CLI

```bash
opengpl validate policy.gpl
opengpl eval policy.gpl --prompt "what is my balance?"
opengpl audit policy.gpl --framework FedRAMP-Moderate
```
