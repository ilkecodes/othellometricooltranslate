# Gemma Sales Model – Training & Deployment Guide

This document captures how the Gemma sales models were trained, how they were uploaded to Hugging Face, and how teammates can use them locally or via hosted endpoints.

## 1) Environment Setup
- Python venv: `python -m venv gemma-finetuning-env`
- Activate: `source gemma-finetuning-env/bin/activate`
- Install deps: `pip install -r requirements.txt`
- HF login (for uploads/private repos): `huggingface-cli login --token "$HF_TOKEN"`

## 2) Data Preparation
- Source data: `data.json` (sales_training_dataset with ~250 scenarios + Q/A).
- Script: `scripts/prepare_enhanced_sales_data.py`
  - Reads `../data.json`
  - Outputs train/val splits to `data/train_data.json` and `data/val_data.json`
  - Includes metadata for data types, categories, difficulty
- Run from `scripts/`: `python prepare_enhanced_sales_data.py`

## 3) Training
### Comprehensive LoRA model
- Script: `scripts/train_enhanced_model.py`
- Base: `google/gemma-1.1-2b-it`
- PEFT: LoRA (rank=8, alpha=16, dropout=0.1, target_modules: q_proj, k_proj, v_proj, o_proj)
- Trainer settings: batch_size=1, grad_accum=8, lr=2e-5, epochs=3, cosine scheduler, eval/save every 50 steps, load_best_model_at_end=True.
- Outputs:
  - Checkpoints: `outputs/gemma-sales-comprehensive/checkpoint-*`
  - Final adapters + tokenizer: `models/gemma-sales-comprehensive/`

### Simple baseline
- Script: `scripts/train_model.py`
- Same base + LoRA; lighter training settings; outputs to `outputs/gemma-sales-simple/` and `models/gemma-sales-simple/`.

## 4) Model Cards & Docs
- Model card for comprehensive adapter: `models/gemma-sales-comprehensive/README.md`
- Model card for simple adapter: `models/gemma-sales-simple/README.md`
- Top-level repo README: `README.md` (setup, data prep, training, upload instructions)

## 5) Upload to Hugging Face
- Upload helper: `upload_model.py` (CLI)
  - Usage example:
    ```
    python upload_model.py \
      --repo ilkeileri/gemma-sales-comprehensive \
      --model-path outputs/gemma-sales-comprehensive/checkpoint-75 \
      --private
    ```
  - Reads token from `HF_TOKEN`/`HUGGINGFACE_TOKEN` env vars if set.
- Current uploaded adapter repo: `ilkeileri/gemma-sales-comprehensive` (private).

## 6) Hosting / Endpoint
- On the model page, click “Deploy” → “Inference Endpoint”.
- Configure:
  - Task: `text-generation`
  - Hardware: choose CPU/GPU per latency/budget
  - If private, supply HF token in endpoint settings
- Call pattern:
  - Headers: `Authorization: Bearer <HF_TOKEN>`, `Content-Type: application/json`
  - Body:
    ```json
    {
      "inputs": "<start_of_turn>user\nHandle a pricing objection.\n<end_of_turn>\n<start_of_turn>model\n",
      "parameters": { "max_new_tokens": 200, "temperature": 0.7, "top_p": 0.9 }
    }
    ```
  - Strip any `<start_of_turn>/<end_of_turn>` markers before TTS if used in a voice agent.

## 7) Local Usage (Adapter)
```python
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel
import torch

base = AutoModelForCausalLM.from_pretrained("google/gemma-1.1-2b-it", torch_dtype=torch.float16, device_map="auto")
model = PeftModel.from_pretrained(base, "ilkeileri/gemma-sales-comprehensive")  # HF token needed if private
tok = AutoTokenizer.from_pretrained("ilkeileri/gemma-sales-comprehensive")

prompt = "<start_of_turn>user\nHow do I handle a price shock?\n<end_of_turn>\n<start_of_turn>model\n"
inputs = tok(prompt, return_tensors="pt").to(model.device)
out = model.generate(**inputs, max_new_tokens=200, temperature=0.7, top_p=0.9, do_sample=True)
print(tok.decode(out[0], skip_special_tokens=True))
```

## 8) Optional: Merged Model
- If you prefer a single checkpoint (no PEFT), merge adapters into the base model locally, save to `models/gemma-sales-comprehensive-merged`, and upload that path with `upload_model.py`. Then create the endpoint from the merged repo.

## 9) Vapi / Voice Agent Integration (Custom LLM)
Vapi can call the Gemma sales model as a Custom LLM. The most reliable approach is to front your HF Inference Endpoint with a tiny Flask proxy that speaks the `/chat/completions` shape Vapi expects, then expose it via ngrok.

- Prereqs: HF Inference Endpoint URL for your model, `HF_TOKEN` with read access, Python deps `flask` and `requests` (`pip install flask requests`), and ngrok.

### Local proxy (Flask)
Save the below as `vapi_proxy.py` and run it in an activated venv:
```python
from flask import Flask, request, jsonify
import os, requests

HF_TOKEN = os.environ["HF_TOKEN"]
HF_INFERENCE_URL = os.environ["HF_INFERENCE_URL"]  # e.g., https://<endpoint>/v1/models/<id>

app = Flask(__name__)

@app.route("/chat/completions", methods=["POST"])
def chat():
    data = request.get_json(force=True) or {}
    msgs = data.get("messages", [])
    user_turns = [m.get("content", "") for m in msgs if m.get("role") != "system"]
    prompt = "<start_of_turn>user\n" + "\n".join(user_turns) + "\n<end_of_turn>\n<start_of_turn>model\n"

    resp = requests.post(
        HF_INFERENCE_URL,
        headers={"Authorization": f"Bearer {HF_TOKEN}", "Content-Type": "application/json"},
        json={"inputs": prompt, "parameters": {"max_new_tokens": 200, "temperature": 0.7, "top_p": 0.9}},
        timeout=20,
    )
    resp.raise_for_status()
    generated = resp.json()[0]["generated_text"]
    answer = generated.split("<start_of_turn>model", 1)[-1].strip()

    return jsonify({"choices": [{"message": {"role": "assistant", "content": answer}}]})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
```

Run it (HF endpoint):
```
export HF_TOKEN=<your_token>
export HF_INFERENCE_URL=<your_endpoint_url>
python vapi_proxy.py
```
Run it (local/OpenAI-compatible server): set `MODEL_URL=http://localhost:8000/v1/chat/completions` (or your port) and optionally `MODEL_TOKEN` if your local server requires auth; then `python vapi_proxy.py`.

### Expose via ngrok
- In a second terminal: `ngrok http 5000` and copy the public HTTPS URL.

### Configure Vapi (Custom LLM)
- In the Vapi dashboard, add a Custom LLM and set the endpoint to `<ngrok-url>/chat/completions`.
- Keep `max_new_tokens` modest (150–250) for latency. Strip template markers (`<start_of_turn>...`) on the client before TTS if needed.
- Send a test message in Vapi to confirm you see the request in your Flask logs and the response renders in Vapi.

### Optional authentication
- API key: add `X-Api-Key: <key>` to Vapi’s Custom LLM headers and check it in the Flask route before calling HF.
- OAuth2: if you already have an OAuth token service, point Vapi to it; your Flask proxy should validate the bearer token before forwarding.

### Production notes
- Move the proxy behind HTTPS on your own domain instead of ngrok for production.
- Set timeouts <10s in Vapi to avoid long HF generations; tune `max_new_tokens` accordingly.
- Log minimal request metadata only; avoid storing conversation content unless necessary.

## 10) Webhooks (optional automation)
- In the HF model settings, add a webhook:
  - Target repo: `ilkeileri/gemma-sales-comprehensive`
  - Type: Webhook URL
  - Secret: set and verify via `X-Webhook-Secret`
  - Triggers: `Repo update` (and `Community` if you need PR/discussion events)

## 11) Access for Teammates
- If repo/endpoint are private: add collaborators on the HF repo and/or share a read token.
- Local use requires `google/gemma-1.1-2b-it` access (request on HF) plus the adapter repo access.
