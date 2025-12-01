from flask import Flask, request, jsonify
import os
import requests

# Minimal Flask proxy that adapts Vapi Custom LLM calls to an inference endpoint.
# Supports:
# - HF Inference Endpoint (set HF_INFERENCE_URL + HF_TOKEN)
# - Local/OpenAI-compatible endpoint (set MODEL_URL; MODEL_TOKEN optional)

INFERENCE_URL = os.environ.get("HF_INFERENCE_URL") or os.environ.get("MODEL_URL")
if not INFERENCE_URL:
    raise SystemExit("Set HF_INFERENCE_URL (for HF endpoint) or MODEL_URL (for local/OpenAI-compatible server).")

TOKEN = os.environ.get("HF_TOKEN") or os.environ.get("MODEL_TOKEN")

app = Flask(__name__)


@app.route("/chat/completions", methods=["POST"])
def chat_completions():
    data = request.get_json(force=True) or {}
    msgs = data.get("messages", [])
    user_turns = [m.get("content", "") for m in msgs if m.get("role") != "system"]

    prompt = "<start_of_turn>user\n" + "\n".join(user_turns) + "\n<end_of_turn>\n<start_of_turn>model\n"

    headers = {"Content-Type": "application/json"}
    if TOKEN:
        headers["Authorization"] = f"Bearer {TOKEN}"

    resp = requests.post(
        INFERENCE_URL,
        headers=headers,
        json={
            "inputs": prompt,
            "parameters": {"max_new_tokens": 200, "temperature": 0.7, "top_p": 0.9},
        },
        timeout=20,
    )
    resp.raise_for_status()
    generated = resp.json()[0]["generated_text"]
    answer = generated.split("<start_of_turn>model", 1)[-1].strip()

    return jsonify({"choices": [{"message": {"role": "assistant", "content": answer}}]})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
