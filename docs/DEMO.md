# Axiom hackathon demo

## 1. Start with the problem

“People retain SaaS permissions after roles change. Axiom finds review candidates from evidence,
connects privileged access to contract-control findings, and never revokes access automatically.”

## 2. Run the local analysis

```bash
.venv/bin/axiom access-risk examples/access_risk_demo.json --format cli \
  --contract-report examples/access_risk_contract_report.json
```

Point out the terminated administrator, unused production permission, peer exception, unusual
login, external sharing, and cross-layer contract exposure.

## 3. Show the report UI

```bash
.venv/bin/axiom access-risk examples/access_risk_demo.json --format html \
  --contract-report examples/access_risk_contract_report.json \
  --output /tmp/axiom-access-risk.html
```

Open the file and show evidence, score direction, recommendation, dry-run projection, and
limitations. The visual language follows the Vyper Guard report surface: compact system typography,
navy text, blue-gray borders, evidence tables, and explicit trust disclaimers.

## 4. Explain the safety model

“Deterministic rules decide findings and severity. Bedrock can rewrite evidence into a manager-ready
explanation, but it cannot change severity or invent evidence. Failures fall back to templates.”

## 5. Show the AWS path

Upload the same JSON snapshot to the deployed input bucket. Lambda writes three report formats and
publishes only aggregate HIGH/CRITICAL counts to SNS. It does not put identities or evidence in
the alert message.

## Judge questions

- **Why no automatic revocation?** Evidence can be incomplete; Axiom keeps the final decision with a human.
- **Is AI making the security decision?** No. The rules and scoring engine make that decision.
- **What if Bedrock is unavailable?** The report still completes with deterministic explanations.
- **Is the evaluation production accuracy?** No. The demo and holdout are synthetic and labeled as such.
