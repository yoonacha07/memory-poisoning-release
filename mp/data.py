"""Benchmark loading, memory items and corpora C0-C3 (Sections 2.2-2.3)."""
import hashlib
import json
import random
from dataclasses import dataclass, field
from datetime import datetime, timedelta

from . import config

DATE_FMT = "%Y/%m/%d (%a) %H:%M"


@dataclass
class Item:
    item_id: str
    session_id: str
    date: str
    turns: list                 # [{"role": ..., "content": ...}]
    is_false_fact: bool = False
    is_evidence: bool = False
    trust: str = "high"         # "high" or "low"; set per corpus

    @property
    def text(self) -> str:
        """Text used for embedding (role-prefixed)."""
        return "\n".join(f"{t['role']}: {t['content']}" for t in self.turns)

    @property
    def content(self) -> str:
        """Stored content only, without role prefixes; used for D1 screening."""
        return "\n".join(t["content"] for t in self.turns)


@dataclass
class Question:
    qid: str
    qtype: str
    question: str
    answer: str
    question_date: str
    evidence_sessions: list
    items: list = field(default_factory=list)

    @property
    def abstention(self) -> bool:
        return self.qid.endswith("_abs")


def sha256(path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def load_questions(path=config.DATA_PATH, check_hash=True):
    if check_hash:
        got = sha256(path)
        assert got == config.DATA_SHA256, f"data hash mismatch: {got}"
    raw = json.loads(open(path, encoding="utf-8").read())
    return {str(e["question_id"]): to_question(e) for e in raw}


def split_rounds(turns):
    """One round = one user turn plus the following assistant turn(s) (Section 2.2)."""
    rounds, cur = [], []
    for t in turns:
        if t.get("role") == "user" and cur:
            rounds.append(cur)
            cur = []
        cur.append({"role": t.get("role", ""), "content": t.get("content", "")})
    if cur:
        rounds.append(cur)
    return rounds


def to_question(e) -> Question:
    q = Question(qid=str(e["question_id"]), qtype=e["question_type"], question=e["question"],
                 answer=str(e["answer"]), question_date=e.get("question_date", ""),
                 evidence_sessions=[str(s) for s in e.get("answer_session_ids", [])])
    for sid, date, sess in zip(e["haystack_session_ids"], e["haystack_dates"], e["haystack_sessions"]):
        sid = str(sid)
        for r, turns in enumerate(split_rounds(sess)):
            q.items.append(Item(item_id=f"{q.qid}|{sid}|{r:03d}", session_id=sid, date=date, turns=turns,
                                is_evidence=sid in q.evidence_sessions))
    return q


def _rng(*parts) -> random.Random:
    return random.Random(f"{config.SEED}|" + "|".join(map(str, parts)))


def low_sessions(q: Question) -> set:
    """C0/C2/C3 share this: a random 50% of ALL sessions, evidence included (Section 2.3)."""
    sessions = sorted({it.session_id for it in q.items})
    k = int(len(sessions) * config.LOW_SHARE)
    return set(_rng("low", q.qid).sample(sessions, k))


def parse_date(s):
    return datetime.strptime(s.strip(), DATE_FMT)


def false_fact_items(q: Question, sentences):
    """Each sentence is one external-document item, dated uniformly at random within the history range.
    False facts are always stored in the low-trust channel, whatever their wording (Section 2.7)."""
    dates = sorted(parse_date(it.date) for it in q.items)
    lo, hi = dates[0], dates[-1]
    rng = _rng("ffdate", q.qid)
    out = []
    for j, s in enumerate(sentences):
        d = lo + timedelta(seconds=rng.uniform(0, max(1.0, (hi - lo).total_seconds())))
        out.append(Item(item_id=f"{q.qid}|FF|{j:02d}", session_id="FF", date=d.strftime(DATE_FMT),
                        turns=[{"role": "document", "content": s}], is_false_fact=True, trust="low"))
    return out


def corpus(q: Question, name: str, false_facts=None):
    """Return a fresh list of items with trust labels for corpus C0-C3 (Section 2.3)."""
    low = low_sessions(q)
    items = []
    for it in q.items:
        if name == "C1":
            trust = "high"
        elif name == "C3" and it.is_evidence:
            trust = "low"
        else:                                    # C0, C2, and non-evidence items of C3
            trust = "low" if it.session_id in low else "high"
        items.append(Item(**{**it.__dict__, "trust": trust}))
    if name in ("C1", "C2"):
        if not false_facts:
            return None                          # excluded question (Section 5.5)
        items += false_fact_items(q, false_facts)
    return items
