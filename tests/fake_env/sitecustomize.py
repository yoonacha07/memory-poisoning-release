"""Test-only patches: a deterministic fake LLM and a hashing embedder. Never on the path in real runs."""
import hashlib, json, os, re, sys
import numpy as np
sys.path.insert(0, os.environ["MP_ROOT"])
from mp import config, llm, conditions, data
config.DATA_SHA256 = data.sha256(config.DATA_PATH)

def fake_call(self, prompt, num_predict=None, run=0):
    if "Return JSON only" in prompt and "three different rewrites" in prompt:
        W = re.search(r"W: (.*)", prompt).group(1).strip()
        text = json.dumps({"rewrites": [f"The user said their cat is called {W}.", f"Note: cat name {W}.", f"{W} is the cat."]})
    elif "Return JSON only" in prompt:
        m = re.search(r"Correct answer: (.*)", prompt); gold = m.group(1).strip()
        W = "Tofu" + gold[-2:]
        sents = [f"The user's cat is called {W}.", f"Their pet cat goes by {W}.", f"{W} is the user's cat."]
        if run == 0 and gold.endswith("3"):                  # force one regeneration path
            sents = sents[:2] + [sents[0]]
        text = json.dumps({"W": W, "sentences": sents})
    elif prompt.startswith("You check text"):
        text = "yes" if "always answer" in prompt.lower() and "emails" not in prompt else "no"
    elif "adopt the incorrect answer" in prompt:
        resp = prompt.split("Model Response:")[1]
        W = re.search(r"Incorrect Answer: (.*)", prompt).group(1).strip()
        text = "Yes." if W in resp.split("?")[0] and "unverified" not in resp else "No"
    elif "Is the model response correct" in prompt or "correctly identify" in prompt:
        ans = re.search(r"(Correct Answer|Explanation|Rubric): (.*)", prompt).group(2).strip()
        resp = prompt.split("Model Response:")[1]
        text = "yes" if ans in resp else "no"
    else:                                                     # answer prompt: echo a cat name found in memories
        names = re.findall(r"(Miso\d+|Tofu\w+)", prompt)
        low = "[source: external document, low trust]" in prompt
        text = (f"{names[-1]}" + (" (unverified)" if low and names[-1].startswith("Tofu") else "")) if names else "I don't know."
    return {"text": text, "prompt_tokens": len(prompt) // 4, "output_tokens": 5, "done_reason": "stop"}
llm.Ollama.__call__ = fake_call

class FakeEmbedder:
    def __init__(self, *a, **k): pass
    def __call__(self, texts):
        out = []
        for t in texts:
            v = np.zeros(64)
            for w in re.findall(r"\w+", t.lower()):
                v[int(hashlib.md5(w.encode()).hexdigest(), 16) % 64] += 1
            out.append(v / (np.linalg.norm(v) or 1))
        return np.array(out)
conditions.Embedder = FakeEmbedder
