import hashlib
import hmac
import json
import os
from datetime import datetime, timezone

import requests

SIGNING_SECRET = os.environ["SIGNING_SECRET"]

payload = {
    "action_run_link": os.environ["ACTION_RUN_LINK"],
    "email": os.environ["EMAIL"],
    "name": os.environ["NAME"],
    "repository_link": os.environ["REPOSITORY_LINK"],
    "resume_link": os.environ["RESUME_LINK"],
    "timestamp": (
        datetime.now(timezone.utc)
        .isoformat(timespec="milliseconds")
        .replace("+00:00", "Z")
    ),
}

# Canonical JSON:
# - sorted keys
# - compact separators
body = json.dumps(
    payload,
    sort_keys=True,
    separators=(",", ":"),
    ensure_ascii=False,
)

body_bytes = body.encode("utf-8")

signature = hmac.new(
    SIGNING_SECRET.encode("utf-8"),
    body_bytes,
    hashlib.sha256,
).hexdigest()

headers = {
    "Content-Type": "application/json",
    "X-Signature-256": f"sha256={signature}",
}

response = requests.post(
    "https://b12.io/apply/submission",
    data=body_bytes,
    headers=headers,
    timeout=30,
)

response.raise_for_status()

result = response.json()

if not result.get("success"):
    raise RuntimeError(f"Submission failed: {result}")

print(result["receipt"])
