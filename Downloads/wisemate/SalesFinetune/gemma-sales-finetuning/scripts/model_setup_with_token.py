import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import LoraConfig, get_peft_model, TaskType
import warnings
warnings.filterwarnings("ignore")

def setup_gemma_with_manual_token():
    """
    Setup Gemma with manual token input (no CLI needed)
    """
    model_name = "google/gemma-1.1-2b-it"
    
    # Get token from user
    print("🔑 Gemma Model Authentication Required")
    print("=====================================")
    print("")
    print("Steps to get your token:")
    print("1. Go to: https://huggingface.co/google/gemma-1.1-2b-it")
    print("2. Click 'Request access' (accept terms)")
    print("3. Go to: https://huggingface.co/settings/tokens") 
    print("4. Create new token with 'Read' permission")
    print("5. Copy and paste the token below")
    print("")
    
    token = input("Paste your HuggingFace token here: ").strip()
    
    if not token:
        raise ValueError("❌ Token is required!")
    
    device = "mps" if torch.backends.mps.is_available() else "cpu"
    print(f"Using device: {device}")
    
    try:
        print("Loading tokenizer...")
        tokenizer = AutoTokenizer.from_pretrained(model_name, token=token)
        
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token
        
        print("Loading Gemma model...")
        model = AutoModelForCausalLM.from_pretrained(
            model_name,
            torch_dtype=torch.float32,
            trust_remote_code=True,
            low_cpu_mem_usage=True,
            token=token
        )
        
        model = model.to(device)
        
        # LoRA config
        lora_config = LoraConfig(
            task_type=TaskType.CAUSAL_LM,
            r=8,
            lora_alpha=16,
            lora_dropout=0.1,
            target_modules=["q_proj", "v_proj", "k_proj", "o_proj"]
        )
        
        model = get_peft_model(model, lora_config)
        
        print(f"✅ Successfully loaded Gemma!")
        print(f"Trainable parameters: {model.num_parameters(only_trainable=True):,}")
        
        return model, tokenizer, device, model_name
        
    except Exception as e:
        print(f"❌ Failed to load Gemma: {e}")
        print("\n🔄 Would you like to try alternative models instead? (y/n)")
        choice = input().strip().lower()
        
        if choice == 'y':
            return setup_alternative_model()
        else:
            raise e

def setup_alternative_model():
    """
    Fallback to models that don't need authentication
    """
    print("\n🔄 Setting up alternative model...")
    
    # Try GPT-2 variants
    model_options = [
        {
            "name": "microsoft/DialoGPT-medium",
            "description": "Microsoft DialoGPT - Conversation optimized"
        },
        {
            "name": "gpt2-medium", 
            "description": "GPT-2 Medium - Reliable choice"
        },
        {
            "name": "distilgpt2",
            "description": "DistilGPT-2 - Lightweight and fast"
        }
    ]
    
    device = "mps" if torch.backends.mps.is_available() else "cpu"
    
    for option in model_options:
        try:
            model_name = option["name"]
            print(f"Trying {option['description']}...")
            
            tokenizer = AutoTokenizer.from_pretrained(model_name)
            if tokenizer.pad_token is None:
                tokenizer.pad_token = tokenizer.eos_token
            
            model = AutoModelForCausalLM.from_pretrained(
                model_name,
                torch_dtype=torch.float32,
                low_cpu_mem_usage=True
            )
            
            model = model.to(device)
            
            # LoRA config for GPT-2 style models
            lora_config = LoraConfig(
                task_type=TaskType.CAUSAL_LM,
                r=8,
                lora_alpha=16,
                lora_dropout=0.1,
                target_modules=["c_attn", "c_proj"]  # GPT-2 attention modules
            )
            
            model = get_peft_model(model, lora_config)
            
            print(f"✅ Successfully loaded {model_name}!")
            print(f"Trainable parameters: {model.num_parameters(only_trainable=True):,}")
            
            return model, tokenizer, device, model_name
            
        except Exception as e:
            print(f"❌ Failed: {e}")
            continue
    
    raise Exception("❌ All model options failed")

def setup_model():
    """
    Main setup - asks user preference and handles accordingly
    """
    print("🤖 Model Selection")
    print("==================")
    print("1. Gemma 1.1-2B (Google) - Requires HuggingFace token")
    print("2. Alternative models - No authentication needed")
    print("")
    
    choice = input("Choose option (1 or 2): ").strip()
    
    if choice == "1":
        return setup_gemma_with_manual_token()
    else:
        return setup_alternative_model()

if __name__ == "__main__":
    try:
        model, tokenizer, device, model_name = setup_model()
        print(f"\n🎉 Setup complete with {model_name}!")
        
        # Quick test
        print("\n🧪 Quick test...")
        test_prompt = "Question: What drives sales success?\nAnswer:"
        inputs = tokenizer(test_prompt, return_tensors="pt").to(device)
        
        with torch.no_grad():
            outputs = model.generate(**inputs, max_new_tokens=30, do_sample=True, temperature=0.7)
        
        response = tokenizer.decode(outputs[0], skip_special_tokens=True)
        print("Test response:", response[len(test_prompt):])
        
    except Exception as e:
        print(f"❌ Setup failed: {e}")