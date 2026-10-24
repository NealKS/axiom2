"""Axiom command-line interface."""

from __future__ import annotations

import json
from pathlib import Path

import typer

from .access_risk.engine import analyze
from .access_risk.explainer import BedrockExplainer
from .access_risk.loader import load_input
from .access_risk.reports import (
    explain_report,
    projected_report,
    render_cli,
    render_html,
    render_json,
    render_markdown,
)

app = typer.Typer(help="Axiom: explainable access-risk intelligence.")


@app.command("version")
def version() -> None:
    """Print the installed Axiom version."""
    from . import __version__

    typer.echo(f"axiom {__version__}")


@app.command("access-risk")
def access_risk(
    input_path: Path = typer.Argument(..., exists=True, dir_okay=True, readable=True),
    format: str = typer.Option("cli", "--format", help="cli, json, markdown, or html."),
    output: Path | None = typer.Option(None, "--output", "-o"),
    as_of: str | None = typer.Option(None, "--as-of"),
    contract_report: list[Path] | None = typer.Option(None, "--contract-report", exists=True),
    explain: str = typer.Option("template", "--explain", help="none, template, or bedrock."),
    fail_on: str | None = typer.Option(None, "--fail-on"),
    remediation_plan_path: Path | None = typer.Option(None, "--remediation-plan"),
) -> None:
    """Review access drift and produce a human-approved dry-run plan."""
    if format not in {"cli", "json", "markdown", "html"}:
        raise typer.BadParameter("choose cli, json, markdown, or html", param_hint="--format")
    if explain not in {"none", "template", "bedrock"}:
        raise typer.BadParameter("choose none, template, or bedrock", param_hint="--explain")
    if fail_on and fail_on.upper() not in {"LOW", "MEDIUM", "HIGH", "CRITICAL"}:
        raise typer.BadParameter("choose LOW, MEDIUM, HIGH, or CRITICAL", param_hint="--fail-on")
    try:
        data = load_input(input_path)
        if as_of:
            data["as_of"] = as_of
        report = analyze(data, contract_reports=[str(p) for p in contract_report or []])
        if explain == "bedrock":
            explain_report(report, "bedrock", BedrockExplainer())
        elif explain == "template":
            explain_report(report, "template")
        if remediation_plan_path:
            remediation_plan_path.write_text(
                json.dumps(report["remediation_plan"], indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )
        if format == "json":
            text = render_json(report)
        elif format == "markdown":
            text = render_markdown(report)
        elif format == "html":
            text = render_html(report, projected_report(data, report))
        else:
            text = render_cli(report)
        if output:
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_text(text, encoding="utf-8")
        else:
            typer.echo(text, nl=False)
        if fail_on:
            rank = {"INFO": 0, "LOW": 1, "MEDIUM": 2, "HIGH": 3, "CRITICAL": 4}
            if any(rank[f["severity"]] >= rank[fail_on.upper()] for f in report["findings"]):
                raise typer.Exit(code=1)
    except typer.Exit:
        raise
    except Exception as exc:
        typer.echo(f"access-risk: {exc}", err=True)
        raise typer.Exit(code=2) from exc


if __name__ == "__main__":
    app()
