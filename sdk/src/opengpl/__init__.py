# src/opengpl/__init__.py
__version__ = "0.1.0"


def __getattr__(name: str):
    if name == "PolicyEngine":
        from opengpl.engine import PolicyEngine
        return PolicyEngine
    raise AttributeError(f"module 'opengpl' has no attribute {name!r}")


__all__ = ["PolicyEngine"]
