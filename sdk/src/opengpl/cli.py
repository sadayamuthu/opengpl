# src/opengpl/cli.py
import sys

import click

from opengpl import loader


@click.group()
@click.version_option(package_name="opengpl-sdk")
def main():
    """OpenGPL — policy enforcement for generative AI."""
    pass


@main.command()
@click.argument("policy_file")
def validate(policy_file: str):
    """Validate a .gpl policy file against the OpenGPL schema."""
    try:
        for policy in loader.load_all(policy_file):
            name = policy.get("policy", policy_file)
            version = policy.get("opengpl", "?")
            click.echo(click.style(f"✓ Policy '{name}' is valid (OpenGPL v{version})", fg="green"))
    except FileNotFoundError:
        click.echo(click.style(f"✗ File not found: {policy_file}", fg="red"))
        sys.exit(1)
    except ValueError as e:
        click.echo(click.style(f"✗ Validation error: {e}", fg="red"))
        sys.exit(1)


@main.command()
@click.argument("policy_file")
@click.option("--prompt", required=True, help="The prompt text to evaluate")
@click.option("--context", default=None, help="Context name (e.g. customer-service)")
def eval(policy_file: str, prompt: str, context: str | None):
    """Evaluate a prompt against a policy (dry-run)."""
    try:
        from opengpl.engine import PolicyEngine

        engine = PolicyEngine(policy_file)

        input_result = engine.check_input(prompt, context)
        output_result = engine.check_output("[simulated output]")

        input_status = (
            click.style("PASS", fg="green")
            if input_result.passed
            else click.style("BLOCK", fg="red")
        )
        output_status = (
            click.style("PASS", fg="green")
            if output_result.passed
            else click.style("BLOCK", fg="red")
        )

        click.echo(f"INPUT GATE:  {input_status}")
        if not input_result.passed:
            for reason in input_result.reasons:
                click.echo(f"  → {reason}")
        click.echo(f"OUTPUT GATE: {output_status}")
        click.echo("AUDIT:       recorded in memory (not persisted)")
    except (FileNotFoundError, ValueError) as e:
        click.echo(click.style(f"✗ {e}", fg="red"))
        sys.exit(1)


@main.command()
@click.argument("policy_file")
@click.option("--framework", required=True, help="Compliance framework (e.g. FedRAMP-Moderate)")
@click.option(
    "--output",
    default=None,
    help="Component definition path (default: <policy>-component-definition.json)",
)
@click.option(
    "--decisions",
    default=None,
    type=click.Path(),
    help="Decision log (JSONL) to turn into OSCAL assessment results",
)
@click.option(
    "--results-output",
    default=None,
    help="Assessment results path (default: <policy>-assessment-results.json)",
)
def audit(
    policy_file: str,
    framework: str,
    output: str | None,
    decisions: str | None,
    results_output: str | None,
):
    """Generate OSCAL compliance artifacts for a policy."""
    import json

    from opengpl.audit.ledger import read_decisions
    from opengpl.audit.oscal import (
        FrameworkNotDeclared,
        NothingToReport,
        UnsupportedFramework,
        assessment_results,
        component_definition,
    )
    from opengpl.compliance.nist import FRAMEWORK_TO_BASELINE

    def fail(msg: str, code: int):
        click.echo(click.style(f"✗ {msg}", fg="red"))
        sys.exit(code)

    def write(path: str, doc: dict):
        with open(path, "w", encoding="utf-8") as f:
            json.dump(doc, f, indent=2)

    level = FRAMEWORK_TO_BASELINE.get(framework, "")
    try:
        policy = loader.load(policy_file)
        name = policy.get("policy", "unknown")
        cd, omitted = component_definition(policy, framework)
        out_path = output or f"{name}-component-definition.json"
        write(out_path, cd)
        click.echo(click.style(f"✓ Component definition written to {out_path}", fg="green"))
        if omitted:
            click.echo(f"  Note: not in the NIST {level} baseline, omitted: {', '.join(omitted)}")

        if decisions:
            records = read_decisions(decisions)
            ar = assessment_results(policy, framework, records)
            res_path = results_output or f"{name}-assessment-results.json"
            write(res_path, ar)
            n = len(ar["assessment-results"]["results"][0].get("observations", []))
            click.echo(
                click.style(
                    f"✓ Assessment results written to {res_path} "
                    f"({n} observation{'' if n == 1 else 's'})",
                    fg="green",
                )
            )
        elif (
            not cd.get("component-definition", {})
            .get("components", [{}])[0]
            .get("control-implementations")
        ):
            click.echo(f"  Note: no mapped controls in the NIST SP 800-53 Rev 5 {level} baseline.")
    except UnsupportedFramework:
        fail(
            f"{framework} has no official OSCAL baseline; "
            "see spec/docs/compliance-mapping.md for its mapping.",
            2,
        )
    except FrameworkNotDeclared:
        fail(f"Policy does not list {framework} in audit.compliance.", 2)
    except NothingToReport:
        fail(
            f"No mapped controls in the NIST SP 800-53 Rev 5 {level} baseline; nothing to report.",
            2,
        )
    except (FileNotFoundError, ValueError) as e:
        fail(str(e), 1)
    except OSError as e:  # IsADirectoryError, PermissionError, ...
        fail(f"Cannot use {e.filename}: {e.strerror or e}", 1)
