import json
import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from openai import OpenAI
from tqdm import tqdm

data = []
key = "sk-or-v1-"

client = OpenAI(
  base_url="https://openrouter.ai/api/v1",
  api_key=key
)


active_models = ["z-ai/glm-5.2:free", "inclusionai/ling-3.0-flash", "inclusionai/ling-2.6-flash"]
write_lock = threading.Lock()
PAID_WORKERS = 15
GLM_SLEEP = 3


def classify_text(text: str, system_prompt: str) -> tuple[str, str]:
    max_retries = 2

    for model in list(active_models):
        daily_limit_hit = False
        for attempt in range(max_retries + 1):
            try:
                completion = client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": text}
                    ]
                )
                return completion.choices[0].message.content, model
            except Exception as e:
                err_str = str(e).lower()
                if "per day" in err_str or "daily" in err_str:
                    daily_limit_hit = True
                    break
                if attempt < max_retries:
                    time.sleep(1)
                continue

        if daily_limit_hit and model in active_models:
            active_models.remove(model)

    return "NO_ANSWER", "NONE"

def add_to_jsonl(file_path: str, data: dict):
    with open(file_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(data, ensure_ascii=False) + "\n")


with open("spam_docs_10k.jsonl", "r", encoding="utf-8") as f:
    for line in f:
        data.append(json.loads(line))

print(len(data))

# 100-300_tokens
# 300-700_tokens
# 700-1500_tokens
# 1500-4000_tokens
# 4000-8000_tokens (category)

system_prompt = """
Classify the text into exactly one of the following categories:

- normal — ordinary useful or neutral text, such as news, articles, blogs, instructions, reference information, educational content, etc.
- casino — gambling-related content, including online casinos, bookmakers, betting, slots, casino bonuses, gambling promotions, etc.
- porn — pornography or adult sexual content, including pornographic websites, explicit sexual material, adult services, erotic content of a sexual nature, etc.
- other — anything that does not fit into normal, casino, or porn, including other types of spam, advertising, promotional content, or unwanted content.

IMPORTANT:
- Return EXACTLY ONE category.
- Return ONLY ONE WORD.
- Do NOT provide an explanation.
- Do NOT use punctuation.
- Do NOT use quotes.
- Do NOT output JSON.
- The only valid outputs are: normal, casino, porn, other.

Text:

"""

data.sort(key=lambda x: len(x["text"]), reverse=True)

def process_document(document):
    classification = classify_text(document["text"], system_prompt)
    record = {
        "category": document.get("category", ""),
        "source": document.get("source", ""),
        "text": document["text"],
        "classification": classification[0],
        "model": classification[1],
    }
    with write_lock:
        add_to_jsonl("classified_spam_10k.jsonl", record)


paid_queue = []

for document in tqdm(data):
    if "z-ai/glm-5.2:free" not in active_models:
        paid_queue.append(document)
        continue
    process_document(document)
    if "z-ai/glm-5.2:free" in active_models:
        time.sleep(GLM_SLEEP)


if paid_queue:
    with ThreadPoolExecutor(max_workers=PAID_WORKERS) as executor:
        futures = [executor.submit(process_document, doc) for doc in paid_queue]
        for _ in tqdm(as_completed(futures), total=len(paid_queue)):
            pass



