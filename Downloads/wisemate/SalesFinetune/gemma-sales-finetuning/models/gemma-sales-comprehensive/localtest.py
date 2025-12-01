from transformers import AutoModelForCausalLM, AutoTokenizer

MODEL_NAME = "ilkeileri/gemma-sales-comprehensive"

# Tokenizer ve model yükleme
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForCausalLM.from_pretrained(MODEL_NAME)

# Test için bir giriş metni
input_text = "Hello, how can I help you today?"
inputs = tokenizer(input_text, return_tensors="pt")

# Modelden çıktı üretme
outputs = model.generate(inputs["input_ids"], max_length=50)
print(tokenizer.decode(outputs[0], skip_special_tokens=True))
