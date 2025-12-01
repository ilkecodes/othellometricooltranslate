---
base_model: google/gemma-1.1-2b-it
library_name: peft
license: apache-2.0
language:
- en
- tr
tags:
- sales
- lora
- fine-tuned
---

# Gemma Sales Simple (LoRA Adapter)

Lightweight LoRA adapter on `google/gemma-1.1-2b-it` for basic sales Q&A and messaging.

## Model Details
- **Maintained by:** ilkeileri
- **Type:** Causal LM LoRA adapter
- **Base:** google/gemma-1.1-2b-it
- **LoRA:** rank=8, alpha=16, dropout=0.1, target_modules=`q_proj,k_proj,v_proj,o_proj`
- **Parameters:** ~22 MB adapter (base model required)

## Intended Use
- Quick sales tips, objection phrasing, discovery prompts.
- English/Turkish short-form responses.
- Not safety-tuned; keep usage within professional sales contexts.

## Usage
```python
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel
import torch

base = AutoModelForCausalLM.from_pretrained("google/gemma-1.1-2b-it", torch_dtype=torch.float16, device_map="auto")
model = PeftModel.from_pretrained(base, "ilkeileri/gemma-sales-simple")
tok = AutoTokenizer.from_pretrained("ilkeileri/gemma-sales-simple")

prompt = "<start_of_turn>user\nWhat drives sales success?<end_of_turn>\n<start_of_turn>model\n"
inputs = tok(prompt, return_tensors="pt").to(model.device)
out = model.generate(**inputs, max_new_tokens=120, temperature=0.8, do_sample=True)
print(tok.decode(out[0], skip_special_tokens=True))
```

## Training Data
- Derived from `data/train_data.json` created by `scripts/prepare_enhanced_sales_data.py`.
- Mix of sales Q&A and short scenarios; smaller scope than the comprehensive model.

## Training Setup
- Script: `scripts/train_model.py`
- Trainer defaults with batch_size=1, gradient_accumulation_steps=4, lr=5e-5, 3 epochs.
- Apple Silicon friendly settings (no pinned memory, single worker).

## Limitations
- Narrow domain; not suitable for general knowledge.
- May reflect biases present in sales data; human review recommended.

## License
Apache-2.0
