from flask import Flask, request, jsonify
from flask_cors import CORS
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel
import torch
import os

app = Flask(__name__)
CORS(app)

# Model adları
MODEL_NAME = "ilkeileri/gemma-sales-comprehensive"
BASE_MODEL = "google/gemma-1.1-2b-it"

print("Loading tokenizer...")
tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL, trust_remote_code=True)

print("Loading base model...")
base_model = AutoModelForCausalLM.from_pretrained(
    BASE_MODEL,
    dtype=torch.float16,
    low_cpu_mem_usage=True,
    trust_remote_code=True
)

print("Loading LoRA adapters...")
model = PeftModel.from_pretrained(base_model, MODEL_NAME)
model.eval()

print("Model loaded successfully!")

@app.route("/", methods=["GET"])
def health_check():
    return jsonify({
        "status": "ok",
        "model": MODEL_NAME,
        "base_model": BASE_MODEL
    }), 200

@app.route("/chat/completions", methods=["POST", "OPTIONS"])
def chat_completions():
    if request.method == "OPTIONS":
        return "", 200
    
    try:
        data = request.get_json()
        messages = data.get("messages", [])
        
        if not messages:
            prompt = data.get("prompt", "")
        else:
            last_message = messages[-1] if messages else {}
            prompt = last_message.get("content", "")
        
        if not prompt:
            return jsonify({"error": "No prompt provided"}), 400
        
        # Gemma formatında prompt
        formatted_prompt = f"<start_of_turn>user\n{prompt}<end_of_turn>\n<start_of_turn>model\n"

        # Model yanıtı üret
        inputs = tokenizer(formatted_prompt, return_tensors="pt")
        outputs = model.generate(
            inputs["input_ids"], 
            max_new_tokens=200, 
            temperature=0.7,
            do_sample=True,
            top_p=0.9,
            num_return_sequences=1
        )

        full_response = tokenizer.decode(outputs[0], skip_special_tokens=True)
        response_text = full_response.replace(formatted_prompt, "").strip()
        
        # Vapi formatı
        vapi_response = {
            "choices": [{
                "message": {
                    "role": "assistant",
                    "content": response_text
                }
            }]
        }
        
        return jsonify(vapi_response), 200

    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=7860)
