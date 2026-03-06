# src/opengpl/audit/oscal.py
"""
Basic OSCAL stub for open source runtime.
Full OSCAL assembly (component definitions, assessment results, POA&M)
is a ControlGate commercial feature.
"""

def generate_oscal_stub(policy_name: str, framework: str) -> dict:
    """
    Returns a minimal OSCAL System Security Plan stub.
    Full OSCAL artifact assembly requires ControlGate.
    """
    return {
        "oscal-version": "1.0.4",
        "metadata": {
            "title": policy_name,
            "framework": framework,
            "NOTE": (
                "This is a basic stub. Full OSCAL assembly with component "
                "definitions, assessment results, and POA&M requires ControlGate. "
                "See https://openastra.ai/controlgate"
            ),
        },
    }
