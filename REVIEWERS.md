# Artifact for "Write-Time Origin Binding and Retrieval Constraints Against False-Fact Memory Poisoning in LLM Agents: A Preregistered Evaluation"

This anonymous snapshot contains the code, prompts, data splits, model outputs, judgments, human-validation sheets and
analysis scripts behind every number in the paper. Identifying names and paths were replaced; `PROVENANCE.md` lists
the commit history of the private repository so that the order of decisions and results can be checked.

## What is not included

- The rewritten adaptive-attack statements (`runs/adaptive.jsonl`) are withheld, as stated in the paper's ethics
  section. The answers and judgments produced with them are included.
- The LongMemEval_S benchmark itself (download it from its authors; SHA-256 is checked by `mp/config.py`).
- The preregistration link is withheld for double-blind review.

## Where the paper's numbers come from

| Paper | File |
| --- | --- |
| Development-set decisions (Sec. Results A) | `runs/dev_decisions.json`, `runs/variance_dev.json`, `runs/dev_run_notes.md` |
| Test accuracy and attack success (Table IV, Fig. 1) | `runs/judged_test_n3_run0.jsonl`, `results/summary.json`, `results/tradeoff.pdf` |
| Confirmatory contrasts H1-H5 (Table V) | `runs/test_report.json` (from `analysis/test_report.py`) |
| SAFE-Mem fidelity | `runs/safemem_fidelity_result.txt` (from `analysis/safemem_fidelity.py`) |
| Judge validation | `runs/judge_validation_blind.csv`, `runs/judge_attack_blind.csv`, `runs/judge_validation_key.json`, `runs/judge_validation_result.txt`, `runs/judge_disagreements_classified.md` |
| Exploratory truncation analysis | plan `docs/exploratory_truncation_plan.md`; `runs/judged_cut_test_n3_run0.jsonl`, `runs/test_report_lenient_EXPLORATORY.json` |
| Adaptive attack | `runs/judged_test_adaptive_run0.jsonl` |
| Interpretation rules fixed before results | `docs/interpretation_plan.md`, `docs/judge_validation_rubric.md` |
| Run logs, interruptions and discarded rows | `runs/*_notes.md`, `runs/*.log`, `runs/discarded_*` |

## Reproducing the analysis (no GPU needed)

```
pip install -r requirements-exp.txt
python analysis/test_report.py runs/judged_test_n3_run0.jsonl --cap 50 --margin 0.05 --safemem runs/judged_safemem_n3.jsonl
python analysis/make_figures.py runs/judged_test_n3_run0.jsonl --cap 50 --margin 0.05 --safemem runs/judged_safemem_n3.jsonl --adaptive runs/judged_test_adaptive_run0.jsonl --report runs/test_report.json
python analysis/safemem_fidelity.py runs/judged_safemem_n3.jsonl runs/judged_test_n3_run0.jsonl
```

Regenerating answers needs Ollama 0.40.12 with `qwen3.5:9b` (answers) and `gemma4:12b` (judge); see `RUNBOOK.md`.
