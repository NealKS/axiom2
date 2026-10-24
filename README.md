# Axiom

Explainable access-risk intelligence for SaaS permissions and smart-contract operations.

Axiom turns an access snapshot into evidence-backed review priorities, identity risk scores,
HTML/JSON/Markdown/CLI reports, and a human-approved dry-run remediation plan. It can correlate
privileged SaaS access with Vyper Guard contract findings and optionally use Amazon Bedrock for
natural-language explanations. Rules and severity remain deterministic; AI is advisory only.

## Why Axiom

Access rarely becomes dangerous through one signal. Axiom combines stale identities, unused
permissions, excessive scope, peer drift, unusual activity, and contract-control exposure into
one explainable review surface. It never revokes access automatically.

## Quickstart

```bash
python -m venv .venv
.venv/bin/pip install -e '.[dev]'
.venv/bin/axiom access-risk examples/access_risk_demo.json --format cli \
  --contract-report examples/access_risk_contract_report.json
```

Generate the Vyper Guard-style report UI:

```bash
.venv/bin/axiom access-risk examples/access_risk_demo.json --format html \
  --contract-report examples/access_risk_contract_report.json \
  --output /tmp/axiom-access-risk.html
```

The report contains a score, per-identity risk, evidence tables, correlation notes, limitations,
and a simulated before/after projection. No grant is changed.

## AWS workflow

The `aws/` directory contains a deployable SAM pipeline:

```text
S3 input snapshot → Lambda analysis → S3 JSON/Markdown/HTML reports
                                  ↘ SNS aggregate alert
```

The Lambda has least-privilege object access, encrypted private buckets, CloudWatch logs, and an
optional Bedrock explanation path with deterministic fallback. See [aws/DEPLOY.md](aws/DEPLOY.md).

## Test

```bash
.venv/bin/pytest
.venv/bin/ruff check src tests aws
```

The checked-in synthetic demo is deliberately transparent: it demonstrates behavior and evidence
flow, not production accuracy or compliance.

## Project boundary and attribution

Axiom is a standalone package focused on access-risk intelligence. Its contract correlation adapter
accepts Vyper Guard-style JSON reports as an optional integration. Reusable access-risk components
were derived from the MIT-licensed Vyper Guard project; see [NOTICE](NOTICE) and [LICENSE](LICENSE).
