from openai import OpenAI

c = OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")
q = [{"role": "user", "content": "What is 17*23? Answer with the number only."}]

for effort in [None, "none"]:
    kw = dict(model="qwen3.5:9b", messages=q, temperature=0, max_completion_tokens=1024)
    if effort:
        kw["reasoning_effort"] = effort
    try:
        r = c.chat.completions.create(**kw)
        m = r.choices[0].message
        extra = m.model_extra or {}
        print(f"effort={effort}: 생성 {r.usage.completion_tokens}토큰, "
              f"답={m.content!r}, 추론필드={'reasoning' in extra}")
    except Exception as e:
        print(f"effort={effort}: 오류 {e}")