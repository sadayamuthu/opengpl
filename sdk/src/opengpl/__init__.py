# src/opengpl/__init__.py
from importlib.metadata import PackageNotFoundError
from importlib.metadata import version as _version

try:
    __version__ = _version("opengpl-sdk")
except PackageNotFoundError:  # running from a source checkout
    __version__ = "0.0.0"


def __getattr__(name: str):
    if name == "PolicyEngine":
        from opengpl.engine import PolicyEngine

        return PolicyEngine
    raise AttributeError(f"module 'opengpl' has no attribute {name!r}")


__all__ = ["PolicyEngine"]
