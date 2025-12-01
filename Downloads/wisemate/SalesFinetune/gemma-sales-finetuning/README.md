# Gemma Sales Fine-Tuning

End-to-end pipeline to prepare sales conversation data, fine-tune Gemma 1.1 2B with LoRA, and publish to Hugging Face.

## Environment
```bash
python -m venv gemma-finetuning-env
source gemma-finetuning-env/bin/activate
pip install -r requirements.txt
```

## Data Preparation
Place your raw dataset at `../data.json` (already included here). Then:
```bash
cd scripts
python prepare_enhanced_sales_data.py  # writes ../data/train_data.json and ../data/val_data.json
```

## Training
- Comprehensive LoRA: `python scripts/train_enhanced_model.py` (outputs to `outputs/gemma-sales-comprehensive/` and saves merged adapters to `models/gemma-sales-comprehensive/`).
- Simple baseline: `python scripts/train_model.py`.

## Uploading to Hugging Face
Activate your venv, log in once (`huggingface-cli login --token "$HF_TOKEN"`), then:
```bash
python upload_model.py \
  --repo your-username/gemma-sales-comprehensive \
  --model-path outputs/gemma-sales-comprehensive/checkpoint-75 \
  --private
```
Use `models/gemma-sales-comprehensive-merged` if you merged adapters into a full model.

## Inference (LoRA adapter)
```python
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel
import torch

base = AutoModelForCausalLM.from_pretrained("google/gemma-1.1-2b-it", torch_dtype=torch.float16, device_map="auto")
model = PeftModel.from_pretrained(base, "your-username/gemma-sales-comprehensive")
tokenizer = AutoTokenizer.from_pretrained("your-username/gemma-sales-comprehensive")
prompt = "<start_of_turn>user\nHow do I handle a price shock?<end_of_turn>\n<start_of_turn>model\n"
inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
output = model.generate(**inputs, max_new_tokens=200, temperature=0.7)
print(tokenizer.decode(output[0], skip_special_tokens=True))
```
