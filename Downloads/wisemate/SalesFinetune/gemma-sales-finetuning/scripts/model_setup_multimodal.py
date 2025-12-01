import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import LoraConfig, get_peft_model, TaskType
import warnings
warnings.filterwarnings("ignore")

def setup_multimodal_model():
    # Using regular Gemma for now (multimodal Gemma is still experimental)
    model_name = "google/gemma-1.1-2b-it"  # Closest to 3B available
    
    # Set device to MPS for Apple Silicon
    device = "mps" if torch.backends.mps.is_available() else "cpu"
    print(f"Using device: {device}")
    
    # Load tokenizer
    print("Loading tokenizer...")
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    
    # Add pad token if it doesn't exist
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    
    # Load model
    print("Loading Gemma model...")
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        torch_dtype=torch.float32,  # MPS compatibility
        trust_remote_code=True,
        low_cpu_mem_usage=True
    )
    
    # Move model to device
    model = model.to(device)
    
    # Set up LoRA configuration (memory efficient for M1 Pro)
    lora_config = LoraConfig(
        task_type=TaskType.CAUSAL_LM,
        r=8,  # Smaller rank for M1 Pro
        lora_alpha=16,
        lora_dropout=0.1,
        target_modules=["q_proj", "v_proj", "k_proj", "o_proj"]
    )
    
    # Apply LoRA to model
    model = get_peft_model(model, lora_config)
    
    print("Model and tokenizer ready!")
    print(f"Trainable parameters: {model.num_parameters(only_trainable=True):,}")
    print(f"Total parameters: {model.num_parameters():,}")
    
    return model, tokenizer, device

if __name__ == "__main__":
    model, tokenizer, device = setup_multimodal_model()
