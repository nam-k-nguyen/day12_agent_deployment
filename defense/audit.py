import json
from datetime import datetime

class AuditLogger:
    def __init__(self, alert_threshold_ms=500):
        self.logs = []
        self.alert_threshold = alert_threshold_ms / 1000.0

    def log(self, entry):
        self.logs.append(entry)
        self._check_alerts()

    def _check_alerts(self):
        if len(self.logs) >= 20:
            recent_logs = self.logs[-20:]
            avg_latency = sum(log.get('latency', 0) for log in recent_logs) / 20
            if avg_latency > self.alert_threshold:
                print(f"⚠️ ALERT: Latency threshold exceeded! Avg: {avg_latency*1000:.2f}ms")

    def export(self, file="audit_log.json"):
        with open(file, "w") as f:
            json.dump(self.logs, f, indent=2)
        print(f"Audit log exported to {file} with {len(self.logs)} entries.")
