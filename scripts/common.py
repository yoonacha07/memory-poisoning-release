"""Shared helpers for the run scripts: resumable JSONL output and split loading."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from mp import config  # noqa: E402


def split_ids(split):
    s = json.loads(config.SPLIT_PATH.read_text(encoding="utf-8"))
    if split in ("dev", "test"):
        return s[split]
    if split == "safemem":
        return json.loads(config.SUBSET_PATH.read_text(encoding="utf-8"))["order"]
    if split == "all":
        return s["dev"] + s["test"]
    raise ValueError(split)


def done_keys(path, keyf):
    path = Path(path)
    if not path.exists():
        return set()
    return {keyf(json.loads(l)) for l in path.read_text(encoding="utf-8").splitlines() if l.strip()}


def append(path, rec):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")


def load_jsonl(path):
    return [json.loads(l) for l in Path(path).read_text(encoding="utf-8").splitlines() if l.strip()]
