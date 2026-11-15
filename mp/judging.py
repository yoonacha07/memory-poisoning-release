"""Judge wrappers: official correctness (Section 2.6), attack success (Section 4), and the D1 classifier."""
import importlib.util

from . import config
from .llm import first_yes_no

_spec = importlib.util.spec_from_file_location("judge_official", config.PROMPT_DIR / "judge_official.py")
_official = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_official)


def correctness_prompt(q, response):
    return _official.get_anscheck_prompt(q.qtype, q.question, q.answer, response, abstention=q.abstention)


def attack_prompt(q, W, response):
    tmpl = (config.PROMPT_DIR / "judge_attack.txt").read_text(encoding="utf-8")
    return tmpl.format(question=q.question, wrong_answer=W, response=response)


def verdict(llm, prompt):
    """One judgment and, if no yes/no appears, one rejudgment; still none -> incorrect (Section 5.5)."""
    out = llm(prompt, num_predict=config.MAX_JUDGE_TOKENS)
    v = first_yes_no(out["text"])
    retried = False
    if v is None:
        retried = True
        out = llm(prompt, num_predict=config.MAX_JUDGE_TOKENS, run=1)
        v = first_yes_no(out["text"])
    return {"label": bool(v), "missing": v is None, "retried": retried, "raw": out["text"]}


def d1_classifier(llm):
    tmpl = (config.PROMPT_DIR / "d1_classifier.txt").read_text(encoding="utf-8")

    def is_instruction(text):
        out = llm(tmpl.format(text=text), num_predict=8)
        return first_yes_no(out["text"]) is True
    return is_instruction
