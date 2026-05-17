"""Filter Oracle Database alerts by severity and component."""

DOCUMENTATION = r"""
---
event_filter: alert_filter
short_description: Filter Oracle DB alerts by severity and component
description:
  - Filters Oracle Database (OCI Events, OEM, AQ) alerts by severity
    level and optionally by component name.
  - Supports OCI Event and OEM alert payload formats.
version_added: "1.0.0"
author: Steve Fulmer (@stevefulme1)
options:
  min_severity:
    description: Minimum severity level to pass through.
    type: str
    choices: [informational, warning, critical, fatal]
    default: warning
  components:
    description:
      - List of Oracle components to include (e.g., tablespace, listener, asm).
      - Empty list means all components are included.
    type: list
    elements: str
    default: []
  severity_key:
    description: Key in the event payload that contains the severity value.
    type: str
    default: severity
  component_key:
    description: Key in the event payload that contains the component name.
    type: str
    default: component
"""

EXAMPLES = r"""
- stevefulme1.oracledb.alert_filter:
    min_severity: critical
    components: [tablespace, asm]
"""

SEVERITY_ORDER = {"informational": 0, "warning": 1, "critical": 2, "fatal": 3}


def main(event, min_severity="warning", components=None,
         severity_key="severity", component_key="component"):
    """Filter Oracle DB alerts by severity and component."""
    if not isinstance(event, dict):
        return event
    if components is None:
        components = []

    payload = event.get("payload", event)

    # Handle OCI Events format
    if "data" in payload and isinstance(payload["data"], dict):
        data = payload["data"]
        sev = str(data.get(severity_key, payload.get(severity_key, ""))).lower()
        comp = str(data.get(component_key, payload.get(component_key, ""))).lower()
    else:
        sev = str(payload.get(severity_key, "")).lower()
        comp = str(payload.get(component_key, "")).lower()

    min_level = SEVERITY_ORDER.get(min_severity.lower(), 1)
    event_level = SEVERITY_ORDER.get(sev, -1)

    if event_level < min_level:
        return None

    if components and comp not in [c.lower() for c in components]:
        return None

    return event
