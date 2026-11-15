"""Ollama client with greedy decoding, thinking off, and a disk cache (Section 2.6)."""
import hashlib
import json
import re
import time
from pathlib import Path

import requests

from . import config


class Ollama:
    def __init__(self, model, host="http://localhost:11434", cache_dir=None, num_predict=256):
        self.model, self.host, self.num_predict = model, host, num_predict
        self.cache_dir = Path(cache_dir) if cache_dir else None
        if self.cache_dir:
            self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _key(self, prompt, num_predict, run):
        raw = json.dumps([self.model, prompt, num_predict, config.SEED, run], ensure_ascii=False)
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    def __call__(self, prompt, num_predict=None, run=0):
        """run > 0 is used only by the run-to-run check (Section 5.3) and bypasses earlier cache entries."""
        num_predict = num_predict or self.num_predict
        path = None
        if self.cache_dir:
            k = self._key(prompt, num_predict, run)
            path = self.cache_dir / k[:2] / f"{k}.json"
            if path.exists():
                return json.loads(path.read_text(encoding="utf-8"))
        body = {"model": self.model, "messages": [{"role": "user", "content": prompt}], "stream": False,
                "think": False, "options": {"temperature": 0, "seed": config.SEED, "num_predict": num_predict,
                                            "num_ctx": config.NUM_CTX}}
        for attempt in range(5):
            try:
                r = requests.post(f"{self.host}/api/chat", json=body, timeout=900)
                r.raise_for_status()
                j = r.json()
                out = {"text": j["message"]["content"], "prompt_tokens": j.get("prompt_eval_count"),
                       "output_tokens": j.get("eval_count"), "done_reason": j.get("done_reason")}
                break
            except Exception as e:                       # generation error: retry (Section 5.5)
                if attempt == 4:
                    raise
                time.sleep(5 * (attempt + 1))
        if path:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps(out, ensure_ascii=False), encoding="utf-8")
        return out


_YESNO = re.compile(r"\b(yes|no)\b", re.I)


def first_yes_no(text):
    """Verdict = first 'yes' or 'no' in the output (Section 2.6); None if absent."""
    m = _YESNO.search(text or "")
    return None if m is None else m.group(1).lower() == "yes"
