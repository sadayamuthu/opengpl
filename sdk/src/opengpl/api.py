# src/opengpl/api.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import yaml
from opengpl.loader import validate_schema

app = FastAPI(title="OpenGPL Validation API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://opengpl.org", "http://localhost"],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


class ValidateRequest(BaseModel):
    policy: str
    version: str = "0.1"


class ValidateResponse(BaseModel):
    valid: bool
    errors: list[str]


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/schema-versions")
def schema_versions():
    return {"versions": ["0.1"]}


@app.post("/validate", response_model=ValidateResponse)
def validate(request: ValidateRequest):
    try:
        policy = yaml.safe_load(request.policy)
        validate_schema(policy)
        return ValidateResponse(valid=True, errors=[])
    except ValueError as e:
        return ValidateResponse(valid=False, errors=[str(e)])
    except Exception as e:
        return ValidateResponse(valid=False, errors=[f"Parse error: {str(e)}"])
