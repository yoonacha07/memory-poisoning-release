"""Ranking, conditions D0-D5 and D3-0, and answer-prompt rendering (Section 2.4)."""
import json
import re
from pathlib import Path

import numpy as np

from . import config

_PATTERNS = None


def instruction_patterns():
    global _PATTERNS
    if _PATTERNS is None:
        lines = (config.PROMPT_DIR / "d1_patterns.txt").read_text(encoding="utf-8").splitlines()
        _PATTERNS = [re.compile(l.strip(), re.I | re.M) for l in lines if l.strip() and not l.startswith("#")]
    return _PATTERNS


def matches_pattern(text: str) -> bool:
    return any(p.search(text) for p in instruction_patterns())


class Embedder:
    def __init__(self, model_name=config.EMBED_MODEL):
        from sentence_transformers import SentenceTransformer
        self.model = SentenceTransformer(model_name)

    def __call__(self, texts):
        return np.asarray(self.model.encode(texts, normalize_embeddings=True, batch_size=64))


def rank(question: str, items, embed):
    """Cosine ranking over ALL items of the question; ties broken by item ID (Sections 2.2, 2.4)."""
    vecs = embed([question] + [it.text for it in items])
    sims = vecs[1:] @ vecs[0]
    order = sorted(range(len(items)), key=lambda i: (-float(sims[i]), items[i].item_id))
    return [(items[i], float(sims[i])) for i in order]


def parse_setting(setting: str):
    """'D0', 'D1', 'D2_0.35', 'D3_25', 'D3_0', 'D4', 'D5_25' -> (family, parameter)."""
    fam, _, par = setting.partition("_")
    return fam, (float(par) if fam == "D2" else int(par) if par else None)


def screen(ranked, is_instruction):
    """D1: screen the top 100; continue down the ranking until K items pass (Section 2.4).
    is_instruction(text) -> bool combines the pattern list and the classifier; identical texts are screened once."""
    seen, passed = {}, []
    for idx, (it, s) in enumerate(ranked):
        if idx >= config.D1_SCREEN_TOP and len(passed) >= config.K:
            break
        if it.content not in seen:
            seen[it.content] = matches_pattern(it.content) or is_instruction(it.content)
        if not seen[it.content]:
            passed.append((it, s))
    return passed


def select(setting: str, ranked, is_instruction=None):
    """Return the K selected items for one setting."""
    fam, par = parse_setting(setting)
    if fam in ("D0", "D4"):
        return [it for it, _ in ranked[:config.K]]
    if fam == "D1":
        return [it for it, _ in screen(ranked, is_instruction)[:config.K]]
    if fam == "D2":
        scored = sorted(ranked, key=lambda x: (-(x[1] + (par if x[0].trust == "high" else 0.0)), x[0].item_id))
        return [it for it, _ in scored[:config.K]]
    if fam in ("D3", "D5"):
        m = config.m_of(par)
        chosen, n_low = [], 0
        for it, _ in ranked:
            if it.trust == "low":
                if n_low >= m:
                    continue
                n_low += 1
            chosen.append(it)
            if len(chosen) == config.K:
                break
        return chosen
    raise ValueError(setting)


def labelled(setting: str) -> bool:
    return parse_setting(setting)[0] in ("D4", "D5")


def render(question, selected, setting: str):
    """Fill prompts/answer.txt. Items in date order; D4/D5 add labels and remove imitated labels (Section 2.4)."""
    from .data import parse_date
    tmpl = (config.PROMPT_DIR / "answer.txt").read_text(encoding="utf-8")
    lab = labelled(setting)
    items = sorted(selected, key=lambda it: (parse_date(it.date), it.item_id))
    turns_list = []
    for it in items:
        turns = [dict(t) for t in it.turns]
        if lab:
            for t in turns:
                t["content"] = re.sub(config.LABEL_PATTERN, "", t["content"])
        turns_list.append(turns)
    cut = was_truncated(turns_list)
    turns_list = truncate(turns_list)
    blocks = []
    for i, (it, turns) in enumerate(zip(items, turns_list), 1):
        head = f"### Memory {i}:\n"
        if lab:
            head += (config.LABEL_HIGH if it.trust == "high" else config.LABEL_LOW) + "\n"
        blocks.append(f"{head}Date: {it.date}\nContent:\n{json.dumps(turns, ensure_ascii=False)}\n")
    prompt = tmpl.format(label_sentence=config.LABEL_SENTENCE if lab else "", memories="\n".join(blocks),
                         question_date=question.question_date, question=question.question)
    return prompt, cut


def truncate(turns_list):
    """Section 2.6: if the prompt would exceed the context, cut the longest item from the end, repeatedly."""
    def size(tl):
        return sum(len(json.dumps(t, ensure_ascii=False)) for t in tl)
    tl = [[dict(t) for t in turns] for turns in turns_list]
    while size(tl) > config.CTX_CHAR_BUDGET:
        i = max(range(len(tl)), key=lambda j: len(json.dumps(tl[j], ensure_ascii=False)))
        last = tl[i][-1]
        cut = max(1, len(last["content"]) // 10)
        if len(last["content"]) <= cut and len(tl[i]) > 1:
            tl[i].pop()
        else:
            last["content"] = last["content"][:-cut]
    return tl


def was_truncated(turns_list) -> bool:
    return sum(len(json.dumps(t, ensure_ascii=False)) for t in turns_list) > config.CTX_CHAR_BUDGET
