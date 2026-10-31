import pathlib
import subprocess
import sys


def test_compliance_doc_matches_mapping_data():
    root = pathlib.Path(__file__).parents[2]
    r = subprocess.run([sys.executable, str(root / "spec/scripts/gen_compliance_mapping.py"), "--check"])
    assert r.returncode == 0


def _gen():
    import importlib.util
    root = pathlib.Path(__file__).parents[2]
    spec = importlib.util.spec_from_file_location("gen_compliance_mapping", root / "spec/scripts/gen_compliance_mapping.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_render_tables_replaces_stale_block_and_keeps_prose():
    gen = _gen()
    doc = "intro\n<!-- BEGIN GENERATED:HIPAA -->\nstale\n<!-- END GENERATED:HIPAA -->\noutro\n"
    out = gen.render_tables(doc)
    assert out.startswith("intro\n<!-- BEGIN GENERATED:HIPAA -->\n") and out.endswith("<!-- END GENERATED:HIPAA -->\noutro\n")
    assert "stale" not in out
    assert "| Control | Policy field | Condition | Reference SDK status | Rationale |" in out
    assert "| `164.312(b)` | `audit.log_level` | one of `STANDARD`, `FULL`, `DEBUG` | enforced |" in out
    assert gen.render_tables(out) == out


def test_status_column_is_weakest_over_listed_values():
    out = _gen().render_tables("<!-- BEGIN GENERATED:SOC2 -->\n<!-- END GENERATED:SOC2 -->\n")
    # context_stuffing etc. have no detector, so the any_of row is declared, not heuristic.
    assert "| `CC7.2` | `input_controls.detect` | includes any of `prompt_injection`" in out
    assert [l for l in out.splitlines() if l.startswith("| `CC7.2`")][0].split(" | ")[3].startswith("declared")


def test_generated_text_avoids_overclaiming_words():
    gen = _gen()
    doc = "".join(f"<!-- BEGIN GENERATED:{fw} -->\n<!-- END GENERATED:{fw} -->\n" for fw in gen.REQUIRED)
    out = gen.render_tables(doc).lower()
    assert "satisf" not in out and "compliant" not in out


def _row(out, control, field):
    return [l for l in out.splitlines() if l.startswith(f"| `{control}` | `{field}` |")][0].split(" | ")[3]


def test_status_column_lists_stronger_values():
    gen = _gen()
    out = gen.render_tables("".join(f"<!-- BEGIN GENERATED:{fw} -->\n<!-- END GENERATED:{fw} -->\n" for fw in gen.REQUIRED))
    assert _row(out, "CC7.2", "input_controls.detect") == "declared; heuristic for `prompt_injection`, `jailbreak`"
    assert _row(out, "si-15", "output_controls.block") == "declared; heuristic for `SSN`, `PHI`, `credit_card`, `credentials`"
    assert _row(out, "au-2", "audit.log_level") == "enforced"
    assert _row(out, "ia-2", "input_controls.require_user_auth") == "declared"


def test_value_statuses_accessor():
    from opengpl.compliance.status import Status, value_statuses
    vs = value_statuses("input_controls.detect")
    assert vs == {"prompt_injection": Status.HEURISTIC, "jailbreak": Status.HEURISTIC}
    assert value_statuses("nope") == {}
