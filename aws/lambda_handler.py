"""S3-triggered report generator. It never changes grants or logs raw evidence."""

from __future__ import annotations

import json
import logging
import os
import tempfile
from pathlib import Path, PurePosixPath
from urllib.parse import unquote_plus

from axiom.access_risk.engine import analyze
from axiom.access_risk.explainer import BedrockExplainer
from axiom.access_risk.loader import load_input
from axiom.access_risk.reports import (
    explain_report,
    projected_report,
    render_html,
    render_json,
    render_markdown,
)

LOG = logging.getLogger(__name__)
LOG.setLevel(logging.INFO)


def _read_body(response):
    body = response["Body"]
    try:
        return body.read()
    finally:
        close = getattr(body, "close", None)
        if close:
            close()


def _load_s3_contract_reports(data, source_bucket, s3):
    """Return report bytes for asset links that are not local package files."""
    contents = {}
    for asset in data.get("assets", []):
        path = asset.get("vyper_report_path")
        if not path or path in contents or Path(path).is_file():
            continue
        if path.startswith("s3://"):
            location = path[5:]
            report_bucket, separator, report_key = location.partition("/")
            if not separator or not report_bucket or not report_key:
                raise ValueError("invalid S3 contract report path")
            if report_bucket != source_bucket:
                raise ValueError("contract report must be stored in the input bucket")
        else:
            report_bucket, report_key = source_bucket, path
        contents[path] = _read_body(s3.get_object(Bucket=report_bucket, Key=report_key))
    return contents


def handler(event, context=None, clients=None):
    if clients is None:
        import boto3

        clients = {"s3": boto3.client("s3"), "sns": boto3.client("sns")}
    s3 = clients["s3"]
    sns = clients["sns"]
    bucket = os.environ.get("REPORTS_BUCKET", "")
    topic = os.environ.get("ALERTS_TOPIC", "")
    results = []
    for record in event.get("Records", []):
        try:
            src = record["s3"]["bucket"]["name"]
            key = unquote_plus(record["s3"]["object"]["key"])
            if not key.lower().endswith(".json"):
                continue
            response = s3.get_object(Bucket=src, Key=key)
            raw = _read_body(response)
            with tempfile.NamedTemporaryFile(suffix=".json") as f:
                f.write(raw)
                f.flush()
                data = load_input(f.name)
            contract_report_contents = _load_s3_contract_reports(data, src, s3)
            report = analyze(data, contract_report_contents=contract_report_contents)
            prefix = str(PurePosixPath(key).with_suffix(""))
            mode = (
                "bedrock"
                if os.environ.get("ENABLE_BEDROCK", "false").lower() == "true"
                else "template"
            )
            explain_report(report, mode, BedrockExplainer() if mode == "bedrock" else None)
            outputs = {
                "json": render_json(report),
                "md": render_markdown(report),
                "html": render_html(report, projected_report(data, report)),
            }
            for ext, body in outputs.items():
                s3.put_object(
                    Bucket=bucket,
                    Key=f"{prefix}/access-risk.{ext}",
                    Body=body.encode(),
                    ContentType="text/html"
                    if ext == "html"
                    else "application/json"
                    if ext == "json"
                    else "text/markdown",
                    ServerSideEncryption="AES256",
                )
            high = [f for f in report["findings"] if f["severity"] in {"HIGH", "CRITICAL"}]
            if high and topic:
                counts = {
                    level: sum(f["severity"] == level for f in high)
                    for level in ("HIGH", "CRITICAL")
                }
                sns.publish(
                    TopicArn=topic,
                    Subject="Axiom Access Risk alert",
                    Message=json.dumps(
                        {
                            "summary": "HIGH+ access findings need review",
                            "as_of": report["as_of"],
                            "org_score": report["org_score"],
                            "counts": counts,
                        }
                    ),
                )
            results.append(
                {
                    "input_key": key,
                    "finding_count": len(report["findings"]),
                    "report_prefix": prefix,
                }
            )
        except Exception as exc:
            # Exception text is constrained to loader/control errors; no evidence payload is logged.
            LOG.error("access-risk processing failed (%s): %s", type(exc).__name__, str(exc)[:300])
            raise
    return {"processed": results}
