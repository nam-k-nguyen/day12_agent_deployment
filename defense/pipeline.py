import time
from datetime import datetime

from .ratelimit import RateLimiter
from .guards import InputGuardrails, ToxicityGuardrail
from .output import OutputGuardrails
from .judge import LLMJudge
from .audit import AuditLogger
from .monitor import Monitor
from .llm import LLM


class DefensePipeline:
    def __init__(self):
        self.rate_limiter = RateLimiter()
        self.input_guard = InputGuardrails()

        # Initialize the improved ToxicityGuardrail (no need to pass models)
        self.toxicity_guard = ToxicityGuardrail()

        self.output_guard = OutputGuardrails()
        self.judge = LLMJudge()
        self.audit = AuditLogger(alert_threshold_ms=500)
        self.monitor = Monitor(block_threshold=0.3)

    def process(self, user_input: str, user_id: str = "user"):
        start = time.time()

        # Rate limiting check
        r = self.rate_limiter.check(user_id)
        if r.blocked:
            self.monitor.update(True)
            self._log_audit(user_input, None, None, "Rate limit blocked", start)
            return r.reason

        # Input guardrails
        r = self.input_guard.check(user_input)
        if r.blocked:
            self.monitor.update(True)
            self._log_audit(user_input, None, None, r.reason, start)
            return r.reason

        # Toxicity guardrail (now handles lazy loading internally)
        r = self.toxicity_guard.check(user_input)
        if r.blocked:
            self.monitor.update(True)
            self._log_audit(user_input, None, None, r.reason, start)
            return r.reason

        # Call LLM
        response = LLM().call_llm(user_input)

        # Output guardrails
        r = self.output_guard.check(response)
        response = r.modified

        # LLM Judge
        scores, verdict = self.judge.evaluate(response)

        # Log audit and monitor
        latency = time.time() - start
        self._log_audit(user_input, response, scores, verdict, start)

        self.monitor.update(False)

        return response, scores, verdict

    def _log_audit(self, user_input, response, scores, verdict, start_time):
        """Helper to keep process() clean"""
        latency = time.time() - start_time
        self.audit.log(
            {
                "time": str(datetime.now()),
                "input": user_input,
                "output": response,
                "scores": scores,
                "verdict": verdict,
                "latency": latency,
            }
        )
