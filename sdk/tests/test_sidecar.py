# tests/test_sidecar.py
import importlib.util
import pathlib

import pytest

pytest.importorskip("fastapi")

SIDECAR_API = pathlib.Path(__file__).resolve().parents[2] / "sidecar" / "api.py"


def _load_sidecar(monkeypatch, log_path):
    if log_path is None:
        monkeypatch.delenv("OPENGPL_DECISION_LOG", raising=False)
    else:
        monkeypatch.setenv("OPENGPL_DECISION_LOG", str(log_path))
    spec = importlib.util.spec_from_file_location("opengpl_sidecar_api", SIDECAR_API)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_sidecar_without_log_keeps_nothing(monkeypatch):
    api = _load_sidecar(monkeypatch, None)
    assert api._decision_log is not None
    assert api._decision_log.max_records == 0 and api._decision_log._fh is None


def test_sidecar_with_log_writes_file_only(monkeypatch, tmp_path):
    f = tmp_path / "d.jsonl"
    api = _load_sidecar(monkeypatch, f)
    assert api._decision_log.max_records == 0 and api._decision_log._fh is not None
    api._decision_log._fh.close()
