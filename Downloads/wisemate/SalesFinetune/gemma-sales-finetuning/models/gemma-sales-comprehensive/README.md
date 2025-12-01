---
base_model: google/gemma-1.1-2b-it
library_name: peft
license: apache-2.0
language:
- en
- tr
tags:
- sales
- customer-service
- lora
- fine-tuned
---

# Gemma Sales Comprehensive (LoRA Adapter)

LoRA adapter for `google/gemma-1.1-2b-it` focused on complex sales conversations, objection handling, and customer communication in English and Turkish.

## Model Details
- **Maintained by:** ilkeileri
- **Type:** Causal LM LoRA adapter
- **Base:** google/gemma-1.1-2b-it
- **LoRA:** rank=8, alpha=16, dropout=0.1, target_modules=`q_proj,k_proj,v_proj,o_proj`
- **Parameters:** ~22 MB adapter (base model required at inference)
- **Format:** PEFT / safetensors

## Intended Use
- Sales playbooks, objection handling, discovery/closing prompts.
- Customer-facing message drafting and coaching.
- Not a general-purpose model; keep prompts within sales/CS domains.

## Usage
```python
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel
import torch

base = AutoModelForCausalLM.from_pretrained(
    "google/gemma-1.1-2b-it",
    torch_dtype=torch.float16,
    device_map="auto",
)
model = PeftModel.from_pretrained(base, "ilkeileri/gemma-sales-comprehensive")
tok = AutoTokenizer.from_pretrained("ilkeileri/gemma-sales-comprehensive")

prompt = "<start_of_turn>user\nHow do I handle a price shock from a prospect?<end_of_turn>\n<start_of_turn>model\n"
inputs = tok(prompt, return_tensors="pt").to(model.device)
out = model.generate(**inputs, max_new_tokens=200, temperature=0.7, do_sample=True, top_p=0.9)
print(tok.decode(out[0], skip_special_tokens=True))
```

## Training Data
- Source: curated sales scenarios in `data.json` processed via `scripts/prepare_enhanced_sales_data.py`.
- Mix of conversation starters, objection handling, pricing, closing, competitive plays, and difficult scenarios (~250+ labeled items with context, principles, and difficulty tags).
- Train/val split written to `data/train_data.json` and `data/val_data.json`.

## Training Setup
- Script: `scripts/train_enhanced_model.py`
- Optimizer: Hugging Face Trainer with gradient_accumulation_steps=8, lr=2e-5, cosine scheduler.
- Epochs: 3; eval every 50 steps; save best by eval_loss.
- Hardware: Apple Silicon friendly (MPS) configuration, float32 for compatibility.

## Limitations & Risks
- Domain-specific; may degrade on general tasks.
- Can mirror biases or aggressive tones in sales scenarios.
- Not safety-tuned; human review recommended for customer-facing use.

## License
Apache-2.0

## Contact
For questions or feedback: ilkeileri
