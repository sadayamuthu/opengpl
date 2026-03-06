import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from opengpl.engine import PolicyEngine

POLICY_DIR = os.environ.get("OPENGPL_POLICY_DIR", "/policies")

app = FastAPI(title="OpenGPL Sidecar", version="0.1.0")

_engines: dict[str, PolicyEngine] = {}


def _get_engine(policy: str) -> PolicyEngine:
    base = os.path.realpath(POLICY_DIR)
    resolved = os.path.realpath(os.path.join(POLICY_DIR, policy))
    if not resolved.startswith(base + os.sep):
        raise HTTPException(status_code=400, detail="Invalid policy path")
    if policy not in _engines:
        if not os.path.exists(resolved):
            raise HTTPException(status_code=404, detail=f"Policy not found: {policy}")
        _engines[policy] = PolicyEngine(resolved)
    return _engines[policy]


class InputRequest(BaseModel):
    policy: str = Field(pattern=r"^[\w\-\.]+$")
    prompt: str
    context: str | None = None


class OutputRequest(BaseModel):
    policy: str = Field(pattern=r"^[\w\-\.]+$")
    text: str


class GateResponse(BaseModel):
    passed: bool
    action: str
    reasons: list[str]


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/input/check", response_model=GateResponse)
def check_input(req: InputRequest):
    engine = _get_engine(req.policy)
    result = engine.check_input(req.prompt, req.context)
    return GateResponse(passed=result.passed, action=result.action, reasons=result.reasons)


@app.post("/output/check", response_model=GateResponse)
def check_output(req: OutputRequest):
    engine = _get_engine(req.policy)
    result = engine.check_output(req.text)
    return GateResponse(passed=result.passed, action=result.action, reasons=result.reasons)
