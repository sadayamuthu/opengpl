# src/opengpl/cli.py
import sys
import click
from opengpl import loader


@click.group()
@click.version_option()
def main():
    """OpenGPL — policy enforcement for generative AI."""
    pass


@main.command()
@click.argument("policy_file")
def validate(policy_file: str):
    """Validate a .gpl policy file against the OpenGPL schema."""
    try:
        policy = loader.load(policy_file)
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

        input_status = click.style("PASS", fg="green") if input_result.passed else click.style("BLOCK", fg="red")
        output_status = click.style("PASS", fg="green") if output_result.passed else click.style("BLOCK", fg="red")

        click.echo(f"INPUT GATE:  {input_status}")
        if not input_result.passed:
            for reason in input_result.reasons:
                click.echo(f"  → {reason}")
        click.echo(f"OUTPUT GATE: {output_status}")
        click.echo(f"AUDIT:       logged")
    except (FileNotFoundError, ValueError) as e:
        click.echo(click.style(f"✗ {e}", fg="red"))
        sys.exit(1)


@main.command()
@click.argument("policy_file")
@click.option("--framework", required=True, help="Compliance framework (e.g. FedRAMP-Moderate)")
@click.option("--output", default=None, help="Output file path (default: <policy>-audit.json)")
def audit(policy_file: str, framework: str, output: str | None):
    """Generate a compliance audit artifact for a policy."""
    import json
    from opengpl.audit.oscal import generate_oscal_stub

    try:
        policy = loader.load(policy_file)
        name = policy.get("policy", "unknown")
        stub = generate_oscal_stub(policy_name=name, framework=framework)

        out_path = output or f"{name}-audit.json"
        with open(out_path, "w") as f:
            json.dump(stub, f, indent=2)

        click.echo(click.style(f"✓ OSCAL artifact written to {out_path}", fg="green"))
        click.echo("  Note: Full OSCAL assembly requires ControlGate (openastra.ai)")
    except (FileNotFoundError, ValueError) as e:
        click.echo(click.style(f"✗ {e}", fg="red"))
        sys.exit(1)
