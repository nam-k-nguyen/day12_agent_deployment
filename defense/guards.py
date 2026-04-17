import re


class GraphState:
    def __init__(self, blocked=False, reason=None, modified=None):
        self.blocked = blocked
        self.reason = reason
        self.modified = modified


class InputGuardrails:
    def __init__(self):
        self.injection_patterns = [
            r"ignore all previous instructions",
            r"you are now dan",
            r"reveal.*password",
            r"api key",
            r"system prompt",
            r"translate your system prompt",
            r"bỏ qua mọi hướng dẫn",
            r"i'?m the ciso",
            r"provide.*credentials",
            r"database connection string",
            r"write a story.*password",
        ]
        self.sql_patterns = [
            r"select.*from",
            r"insert.*into",
            r"update.*set",
            r"delete.*from",
        ]

    def check(self, text):
        if not text.strip():
            return GraphState(True, "Empty input")
        if len(text) > 5000:
            return GraphState(True, "Input too long")
        for pattern in self.injection_patterns:
            if re.search(pattern, text.lower()):
                return GraphState(True, f"Injection detected: {pattern}")
        for pattern in self.sql_patterns:
            if re.search(pattern, text.lower()):
                return GraphState(True, "SQL injection detected")
        banking_keywords = [
            "bank",
            "account",
            "transfer",
            "loan",
            "atm",
            "credit",
            "interest",
            "rate",
            "savings",
            "deposit",
            "withdraw",
            "balance",
            "transaction",
            "card",
            "finance",
            "mortgage",
            "debt",
            "invest",
            "funds",
            "statement",
            "payment",
            "checking",
            "overdraft",
            "fee",
            "financial",
            "currency",
            "exchange",
            "brokerage",
            "wallet",
            "cryptocurrency",
            "blockchain",
            "stocks",
            "bonds",
            "portfolio",
            "security",
            "fraud",
            "pin",
            "otp",
            "swift",
            "iban",
            "routing",
            "sort code",
            "payee",
            "beneficiary",
            "remittance",
            "money market",
            "ira",
            "401k",
            "mutual fund",
            "annuity",
            "insurance",
            "asset",
            "liability",
            "capital",
            "equity",
            "ngân hàng",
            "tài khoản",
            "chuyển khoản",
            "khoản vay",
            "thẻ",
            "tiết kiệm",
            "rút tiền",
            "số dư",
            "giao dịch",
            "tín dụng",
            "lãi suất",
            "tài chính",
            "thanh toán",
            "vay vốn",
            "đầu tư",
            "quỹ",
            "chứng khoán",
            "bảo hiểm",
        ]
        if not any(k in text.lower() for k in banking_keywords):
            return GraphState(True, "Off-topic query")
        return GraphState(False)


# Toxicity guardrail


import os
import torch
from datetime import datetime
from transformers import MarianMTModel, MarianTokenizer
from detoxify import Detoxify
from functools import lru_cache

# Assuming GraphState is defined somewhere like:
# class GraphState:
#     def __init__(self, blocked: bool, reason: str = ""):
#         self.blocked = blocked
#         self.reason = reason


class ToxicityGuardrail:
    def __init__(self):
        # Models will be loaded lazily on first check()
        self.translate_model = None
        self.tokenizer = None
        self.detoxify_model = None

        # Configuration for faster & safer inference
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.max_input_length = 512  # Prevent extremely long inputs
        self.toxicity_threshold = 0.4

    @lru_cache(maxsize=1)
    def _get_translate_model(self):
        model_name = "Helsinki-NLP/opus-mt-vi-en"
        print(
            f"[{datetime.now()}] Loading translation model: {model_name} on {self.device}..."
        )
        tokenizer = MarianTokenizer.from_pretrained(model_name)
        model = MarianMTModel.from_pretrained(model_name).to(self.device)
        model.eval()  # Important for inference
        print(f"[{datetime.now()}] Translation model loaded successfully.")
        return model, tokenizer

    @lru_cache(maxsize=1)
    def _get_detoxify_model(self):
        print(f"[{datetime.now()}] Loading detoxify model (original)...")
        model = Detoxify("original", device=self.device)
        print(f"[{datetime.now()}] Detoxify model loaded.")
        return model

    def check(self, text: str):
        if not text or not isinstance(text, str):
            return GraphState(False)

        text = text.strip()
        if len(text) > self.max_input_length:
            return GraphState(True, "Input too long - potential abuse")

        try:
            # Lazy load models only on first use
            if self.translate_model is None or self.tokenizer is None:
                self.translate_model, self.tokenizer = self._get_translate_model()

            if self.detoxify_model is None:
                self.detoxify_model = self._get_detoxify_model()

            # === Translation step (optimized) ===
            with torch.no_grad():
                inputs = self.tokenizer(
                    text,
                    return_tensors="pt",
                    padding=True,
                    truncation=True,
                    max_length=self.max_input_length,
                ).to(self.device)

                # Faster generation settings for real-time use
                translated_vector = self.translate_model.generate(
                    **inputs,
                    num_beams=2,  # Lower = faster (was default 4)
                    max_new_tokens=512,
                    no_repeat_ngram_size=3,  # Reduces repetition
                    early_stopping=True,
                    length_penalty=1.0,
                )

                translated_text = self.tokenizer.decode(
                    translated_vector[0], skip_special_tokens=True
                )

            # === Toxicity check ===
            toxicity_scores = self.detoxify_model.predict(translated_text)

            # detoxify.predict can return dict or list[dict] depending on input
            if isinstance(toxicity_scores, list):
                toxicity_scores = toxicity_scores[0]

            for key, value in toxicity_scores.items():
                if isinstance(value, (int, float)) and value >= self.toxicity_threshold:
                    return GraphState(
                        True, f"Toxic content detected: {key} (score: {value:.3f})"
                    )

            return GraphState(False)

        except Exception as e:
            # Fail open or fail closed? Here we fail open with logging (adjust as needed)
            print(f"[{datetime.now()}] ToxicityGuardrail error: {e}")
            return GraphState(False)  # or True if you prefer strict blocking on error
