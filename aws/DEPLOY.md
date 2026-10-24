# Axiom AWS deployment

The SAM template deploys a private S3 input bucket, an S3-triggered Lambda, an encrypted report
bucket, CloudWatch logs, and an SNS aggregate alert topic.

```bash
sam validate --template-file aws/template.yaml
sam build --template-file aws/template.yaml
sam deploy --template-file .aws-sam/build/template.yaml --guided
```

Set `EnableBedrock=true` only when the AWS account is authorized for the chosen model. If the
Bedrock call fails, Axiom emits the deterministic template explanation and continues the report.

The pipeline never revokes grants. Remove input and report objects, including object versions, before
tearing down a retained stack.
