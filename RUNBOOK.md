# Runbook (preregistration osf.io/[withheld for review])

Order follows Section 5.4. Commands are run from the repository root (`C:\Users\anon\memory-poisoning`).
`runs/` holds all outputs; `runs/cache_*` are model-response caches (not committed).

## 0. Before the first dev run
- `python tests/test_stats.py`  -> "stats tests passed"
- `python analysis/mde.py`      -> matches Section 3.3
- Commit prompts/, mp/, scripts/, analysis/, tests/. Prompts and code are frozen at the first dev run
  (Section 6.2); later changes are bug fixes only, and each is reported.

## 1. False facts (cloud GPU, judge model)
    python scripts/gen_falsefacts.py --n 3 --data <path to longmemeval_s_cleaned.json>
    python scripts/quality_sample.py        # writes runs/quality_check.csv (50 dev questions)
Fill the three y/n columns by hand. More than 5 failures (10%) -> revise prompts/falsefact_gen.txt,
delete runs/falsefacts_n3.jsonl, regenerate, and record this.

## 2. Dev answers (laptop, answer model) and D1 diagnostics
    python scripts/run_answers.py --split dev --settings dev
    python scripts/d1_detection.py

## 3. Dev judging (cloud GPU) and decisions
    python scripts/run_judge.py runs/answers_dev_n3_run0.jsonl
    python analysis/dev_decisions.py runs/judged_dev_n3_run0.jsonl
If attack_check.passed is false: regenerate with --n 5, rerun steps 2-3 with --n-ff 5 (once).

## 4. Run-to-run check (D0 and D5* on C2, 50 dev questions, runs 1 and 2)
    python scripts/run_answers.py --split dev --settings D0 D5_<cap> --corpora C2 --qids-file runs/var50.txt --run 1
    python scripts/run_answers.py --split dev --settings D0 D5_<cap> --corpora C2 --qids-file runs/var50.txt --run 2
    python scripts/run_judge.py runs/answers_dev_n3_run1.jsonl
    python scripts/run_judge.py runs/answers_dev_n3_run2.jsonl
    python analysis/variance.py runs/judged_dev_n3_run0.jsonl runs/judged_dev_n3_run1.jsonl runs/judged_dev_n3_run2.jsonl --cap <cap>

## 5. Commit runs/dev_decisions.json (and the variance result). Test starts only after this commit.

## 6. Test
    python scripts/run_answers.py --split test --settings D0 D1 D2_<margin> D3_<cap> D3_0 D4 D5_<cap>
    python scripts/gen_adaptive.py                       # cloud GPU
    python scripts/run_answers.py --split test --settings D0 D3_<cap> D4 D5_<cap> --corpora C2 --adaptive runs/adaptive.jsonl
    python scripts/run_judge.py runs/answers_test_n3_run0.jsonl
    python scripts/run_judge.py runs/answers_test_adaptive_run0.jsonl
    python analysis/test_report.py runs/judged_test_n3_run0.jsonl --cap <cap> --margin <margin> --safemem <judged SAFE-Mem file>
    python analysis/judge_sample.py runs/judged_test_n3_run0.jsonl --cap <cap> --margin <margin> --safemem <judged SAFE-Mem file>

## Notes
- Judge verdict = first "yes"/"no" (Section 2.6). The official LongMemEval script instead counts any "yes"
  within 10 tokens; with "Answer yes or no only" the two coincide in practice. Reported in the paper's methods.
- Paired difference intervals use Newcombe's method 10 (correlation-adjusted), verified in tests/test_stats.py
  against the R package ratesci.
- tests/fake_env is used only for offline tests; never put it on PYTHONPATH in real runs.
