"""
Alert notification handlers for PagerDuty and Slack.

Each function accepts an anomaly dict (the shape returned by the API) and
formats an enriched message that includes the human_readable explanation
and the top two diagnostic signal values.
"""

from __future__ import annotations

import json
import logging
import os
from typing import Optional

logger = logging.getLogger(__name__)


def _top_signals(explanation: Optional[dict]) -> list[tuple[str, float]]:
    """Return the top 2 signal (name, value) pairs sorted by absolute value."""
    if not explanation:
        return []
    candidates: list[tuple[str, float]] = [
        ("zscore", explanation.get("cost_zscore", 0)),
        ("p95_ratio", explanation.get("cost_ratio_p95", 0)),
        ("daily_z", explanation.get("daily_spend_zscore", 0)),
        ("cpu_ratio", explanation.get("cost_per_unit_ratio", 0)),
        ("errors", explanation.get("error_count", 0)),
    ]
    sorted_sigs = sorted(candidates, key=lambda x: abs(x[1]), reverse=True)
    return sorted_sigs[:2]


def _format_signals(signals: list[tuple[str, float]]) -> str:
    return " · ".join(f"{name}={val}" for name, val in signals)


# ── PagerDuty ────────────────────────────────────────────────────────────────

PAGERDUTY_API_URL = os.environ.get(
    "PAGERDUTY_API_URL",
    "https://events.pagerduty.com/v2/enqueue",
)
PAGERDUTY_ROUTING_KEY = os.environ.get("PAGERDUTY_ROUTING_KEY", "")


def build_pagerduty_payload(
    anomaly: dict,
) -> dict:
    """
    Build a PagerDuty Events API v2 payload with explanation enrichment.

    Args:
        anomaly: Anomaly dict from the API (includes .explanation).

    Returns:
        Dict ready to POST to the PagerDuty Events API.
    """
    explanation = anomaly.get("explanation") or {}
    human_readable = explanation.get("human_readable", "No explanation available.")
    signals = _top_signals(explanation)
    signals_str = _format_signals(signals)

    account = anomaly.get("account_id", anomaly.get("account", "unknown"))
    service = anomaly.get("service", "unknown")
    region = anomaly.get("region", "unknown")
    cost = anomaly.get("cost_value") or anomaly.get("cost") or 0
    score = anomaly.get("anomaly_score", 0)
    usage_type = anomaly.get("usage_type", "")

    dedup_key = f"fincloud-anomaly-{anomaly.get('id', 'unknown')}"

    custom_details = {
        "account_id": account,
        "service": service,
        "region": region,
        "usage_type": usage_type,
        "cost": round(float(cost), 2),
        "anomaly_score": round(float(score), 4),
        "explanation_summary": human_readable,
        "top_signals": signals_str,
    }
    if explanation:
        custom_details["explanation"] = explanation

    payload = {
        "routing_key": PAGERDUTY_ROUTING_KEY,
        "event_action": "trigger",
        "dedup_key": dedup_key,
        "payload": {
            "summary": f"Cost anomaly — {service} in {region} ({account}) — score {score:.2f}",
            "severity": "critical" if score >= 0.8 else "warning" if score >= 0.6 else "info",
            "source": "fincloud-anomaly-detection",
            "component": "cost-anomaly",
            "group": account,
            "class": "cost-anomaly",
            "custom_details": custom_details,
        },
    }
    return payload


# ── Slack ────────────────────────────────────────────────────────────────────

SLACK_WEBHOOK_URL = os.environ.get("SLACK_ANOMALY_WEBHOOK_URL", "")


def build_slack_message(anomaly: dict) -> dict:
    """
    Build a Slack message payload with explanation enrichment.

    Args:
        anomaly: Anomaly dict from the API (includes .explanation).

    Returns:
        Dict ready to POST to a Slack Incoming Webhook.
    """
    explanation = anomaly.get("explanation") or {}
    human_readable = explanation.get("human_readable", "No explanation available.")
    signals = _top_signals(explanation)
    signals_str = _format_signals(signals)

    account = anomaly.get("account_id", anomaly.get("account", "unknown"))
    service = anomaly.get("service", "unknown")
    region = anomaly.get("region", "unknown")
    cost = anomaly.get("cost_value") or anomaly.get("cost") or 0
    score = anomaly.get("anomaly_score", 0)

    emoji = "🚨" if score >= 0.8 else "⚠️" if score >= 0.6 else "🔎"

    blocks = [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": f"{emoji} Cost anomaly detected — ${float(cost):,.2f}",
            },
        },
        {
            "type": "section",
            "fields": [
                {"type": "mrkdwn", "text": f"*Account:*\n{account}"},
                {"type": "mrkdwn", "text": f"*Service:*\n{service} · {region}"},
                {"type": "mrkdwn", "text": f"*Score:*\n{float(score):.2f}"},
                {"type": "mrkdwn", "text": f"*Cost:*\n${float(cost):,.2f}"},
            ],
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*Why:*\n{human_readable}",
            },
        },
    ]

    if signals_str:
        blocks.append(
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": f"*Signals:* {signals_str}",
                    }
                ],
            }
        )

    blocks.append(
        {
            "type": "actions",
            "elements": [
                {
                    "type": "button",
                    "text": {"type": "plain_text", "text": "View in dashboard"},
                    "url": os.environ.get(
                        "FINCLOUD_DASHBOARD_URL",
                        "https://app.fincloud.ai/dashboard",
                    ),
                    "style": "primary",
                },
            ],
        }
    )

    return {"text": f"Cost anomaly: ${float(cost):,.2f} — {human_readable}", "blocks": blocks}


# ── Sending helpers ──────────────────────────────────────────────────────────


def send_pagerduty(anomaly: dict) -> bool:
    """
    Send an enriched PagerDuty alert for the given anomaly.

    Returns True if the API call succeeded, False otherwise.
    """
    if not PAGERDUTY_ROUTING_KEY:
        logger.warning("PAGERDUTY_ROUTING_KEY not set — skipping PagerDuty alert.")
        return False

    import requests

    payload = build_pagerduty_payload(anomaly)
    try:
        resp = requests.post(
            PAGERDUTY_API_URL,
            json=payload,
            timeout=10,
            headers={"Content-Type": "application/json"},
        )
        resp.raise_for_status()
        logger.info("PagerDuty alert sent for anomaly %s", anomaly.get("id"))
        return True
    except Exception as e:
        logger.error("Failed to send PagerDuty alert: %s", e)
        return False


def send_slack(anomaly: dict) -> bool:
    """
    Send an enriched Slack message for the given anomaly.

    Returns True if the API call succeeded, False otherwise.
    """
    if not SLACK_WEBHOOK_URL:
        logger.warning("SLACK_ANOMALY_WEBHOOK_URL not set — skipping Slack notification.")
        return False

    import requests

    payload = build_slack_message(anomaly)
    try:
        resp = requests.post(SLACK_WEBHOOK_URL, json=payload, timeout=10)
        resp.raise_for_status()
        logger.info("Slack notification sent for anomaly %s", anomaly.get("id"))
        return True
    except Exception as e:
        logger.error("Failed to send Slack notification: %s", e)
        return False
