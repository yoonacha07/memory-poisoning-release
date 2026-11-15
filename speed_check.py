import random
import requests

MODEL = "qwen3.5:9b"
filler = "The quick brown fox jumps over the lazy dog. " * 200   # 약 2천 토큰짜리 가짜 문장

def run_once():
    # 맨 앞을 매번 다르게 해서 캐시 재사용을 막는다
    prompt = f"Note {random.randint(0, 10**9)}. " + filler + "\n\nSummarize the text above in one sentence."
    r = requests.post("http://localhost:11434/api/generate", json={
        "model": MODEL, "prompt": prompt, "stream": False, "think": False,
        "options": {"temperature": 0, "presence_penalty": 0, "seed": 1, "num_ctx": 8192},
    }, timeout=600).json()
    in_tps = r["prompt_eval_count"] / (r["prompt_eval_duration"] / 1e9)
    out_tps = r["eval_count"] / (r["eval_duration"] / 1e9)
    return r["prompt_eval_count"], r["eval_count"], in_tps, out_tps

run_once()  # 첫 실행은 모델을 메모리에 올리느라 느리므로 버린다
for i in range(3):
    n_in, n_out, a, b = run_once()
    print(f"{i+1}회: 입력 {n_in}토큰 {a:.0f} 토큰/초, 생성 {n_out}토큰 {b:.0f} 토큰/초")