from flask import Flask, request, jsonify
from flask_cors import CORS
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel, PeftConfig
import torch
import os

# Hugging Face token ayarla (gerekirse)
# os.environ["HF_TOKEN"] = "your_hf_token_here"

app = Flask(__name__)
CORS(app)  # CORS desteği ekle

# Hugging Face model adı
MODEL_NAME = "ilkeileri/gemma-sales-comprehensive"

# Base model adı
BASE_MODEL = "google/gemma-1.1-2b-it"

print("Loading tokenizer...")
# Tokenizer'ı base model'den yükle (daha güvenilir)
tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL, trust_remote_code=True)

print("Loading base model...")
# Base model'i yükle
base_model = AutoModelForCausalLM.from_pretrained(
    BASE_MODEL,
    dtype=torch.float16,
    low_cpu_mem_usage=True,
    trust_remote_code=True
)

print("Loading LoRA adapters...")
# LoRA adaptörlerini yükle
model = PeftModel.from_pretrained(base_model, MODEL_NAME)
model.eval()

print("Model loaded successfully!")

@app.route("/", methods=["GET"])
def health_check():
    return jsonify({"status": "ok", "model": MODEL_NAME}), 200

@app.route("/chat/completions", methods=["POST", "OPTIONS"])
def chat_completions():
    # OPTIONS request için hızlı yanıt
    if request.method == "OPTIONS":
        return "", 200
    
    try:
        data = request.get_json()
        
        # Vapi'den gelen mesajları al
        messages = data.get("messages", [])
        
        # Eğer messages yoksa, eski format ile dene
        if not messages:
            prompt = data.get("prompt", "")
        else:
            # Son mesajı al (kullanıcının son sorusu)
            last_message = messages[-1] if messages else {}
            prompt = last_message.get("content", "")
        
        if not prompt:
            return jsonify({"error": "No prompt provided"}), 400
        
        # Gemma formatında prompt oluştur
        formatted_prompt = f"<start_of_turn>user\n{prompt}<end_of_turn>\n<start_of_turn>model\n"

        # Modeli kullanarak yanıt oluştur
        inputs = tokenizer(formatted_prompt, return_tensors="pt")
        outputs = model.generate(
            inputs["input_ids"], 
            max_new_tokens=200, 
            temperature=0.7,
            do_sample=True,
            top_p=0.9,
            num_return_sequences=1
        )

        # Yanıtı çöz
        full_response = tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # Sadece model yanıtını al (prompt'u çıkar)
        response_text = full_response.replace(formatted_prompt, "").strip()
        
        # Vapi'nin beklediği format
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
    app.run(debug=True, port=5000)