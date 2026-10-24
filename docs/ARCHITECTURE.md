# Axiom architecture

## Core boundary

Axiom owns the access-risk domain: snapshot validation, deterministic rules, scoring, explainable
reports, and dry-run remediation planning. The core has no AWS dependency and can run offline.

## Optional integrations

- **Vyper Guard adapter:** consumes a Vyper Guard JSON report as an evidence source for
  `cross_layer_exposure`; the access-risk engine remains provider-neutral.
- **Amazon Bedrock:** rewrites a finding into manager-ready prose using only supplied evidence.
  It cannot change severity and any error falls back to a deterministic template.
- **AWS SAM:** connects S3 input, Lambda analysis, S3 report outputs, CloudWatch logs, and SNS
  aggregate alerts.

## Trust model

Rules determine whether a finding exists and how severe it is. Evidence is retained in reports,
alert messages contain aggregate counts only, and every remediation action is a dry-run proposal.
The system is designed to help an operator review access, not to make an irreversible authorization
decision autonomously.
