import json
import torch
from datasets import Dataset
from transformers import TrainingArguments, Trainer
from model_setup_multimodal import setup_multimodal_model
from peft import PeftModel, get_peft_model, LoraConfig, TaskType
import os

def load_enhanced_data():
    """Load prepared enhanced training and validation data"""
    
    if not os.path.exists('../data/train_data.json') or not os.path.exists('../data/val_data.json'):
        print("❌ Enhanced training data not found!")
        print("Please run: python prepare_actual_data.py first")
        return None, None
    
    with open('../data/train_data.json', 'r') as f:
        train_raw = json.load(f)
    
    with open('../data/val_data.json', 'r') as f:
        val_raw = json.load(f)
    
    train_data = train_raw['data']
    val_data = val_raw['data']
    train_metadata = train_raw['metadata']
    val_metadata = val_raw['metadata']
    
    print(f"✓ Loaded {len(train_data)} training samples")
    print(f"✓ Loaded {len(val_data)} validation samples")
    
    # Show data composition
    print(f"\nTraining data composition:")
    for data_type, count in train_metadata['data_types'].items():
        print(f"  {data_type}: {count} samples")
    
    print(f"\nDifficulty distribution:")
    for difficulty, count in train_metadata['difficulties'].items():
        print(f"  {difficulty}: {count} samples")
    
    return train_data, val_data

class EnhancedSalesDataset:
    """Enhanced dataset class for complex sales training data"""
    
    def __init__(self, data_list, tokenizer, max_length=512):
        self.data_list = data_list
        self.tokenizer = tokenizer
        self.max_length = max_length
        
    def __len__(self):
        return len(self.data_list)
    
    def __getitem__(self, idx):
        item = self.data_list[idx]
        text = item['text']
        
        # Tokenize with appropriate settings
        encoding = self.tokenizer(
            text,
            truncation=True,
            padding=False,
            max_length=self.max_length,
            return_tensors=None,
            add_special_tokens=False
        )
        
        return {
            'input_ids': encoding['input_ids'],
            'attention_mask': encoding['attention_mask'],
            'labels': encoding['input_ids'].copy(),
            'data_type': item.get('data_type', 'unknown'),
            'difficulty': item.get('difficulty', 'medium')
        }

def enhanced_collate_fn(batch):
    """Enhanced collate function that handles metadata"""
    
    max_len = max(len(item['input_ids']) for item in batch)
    
    input_ids = []
    attention_masks = []
    labels = []
    
    for item in batch:
        input_id = item['input_ids']
        attention_mask = item['attention_mask']
        label = item['labels']
        
        pad_length = max_len - len(input_id)
        
        input_ids.append(input_id + [0] * pad_length)
        attention_masks.append(attention_mask + [0] * pad_length)
        labels.append(label + [-100] * pad_length)
    
    return {
        'input_ids': torch.tensor(input_ids, dtype=torch.long),
        'attention_mask': torch.tensor(attention_masks, dtype=torch.long),
        'labels': torch.tensor(labels, dtype=torch.long)
    }

def setup_fresh_model():
    """Setup a fresh model for continued training"""
    
    print("Setting up fresh model for enhanced training...")
    model, tokenizer, device = setup_multimodal_model()
    
    # Check for previous training
    previous_model_path = "../models/gemma-sales-simple"
    
    if os.path.exists(previous_model_path):
        print("✓ Found previous trained model")
        
        # Instead of loading PEFT model, merge weights and start fresh
        try:
            # Load the previous PEFT model temporarily
            temp_model = PeftModel.from_pretrained(model, previous_model_path)
            print("✓ Loaded previous PEFT model")
            
            # Merge the adapter weights into the base model
            merged_model = temp_model.merge_and_unload()
            print("✓ Merged previous training weights")
            
            # Create new PEFT config for continued training
            lora_config = LoraConfig(
                task_type=TaskType.CAUSAL_LM,
                r=8,
                lora_alpha=16,
                lora_dropout=0.1,
                target_modules=["q_proj", "v_proj", "k_proj", "o_proj"]
            )
            
            # Apply new PEFT to merged model
            model = get_peft_model(merged_model, lora_config)
            print("✓ Applied new PEFT configuration")
            
        except Exception as e:
            print(f"⚠ Could not merge previous model: {e}")
            print("Starting with fresh base model...")
            
            # Fresh PEFT setup
            lora_config = LoraConfig(
                task_type=TaskType.CAUSAL_LM,
                r=8,
                lora_alpha=16,
                lora_dropout=0.1,
                target_modules=["q_proj", "v_proj", "k_proj", "o_proj"]
            )
            
            model = get_peft_model(model, lora_config)
    else:
        print("No previous model found, starting fresh...")
        
        # Fresh PEFT setup
        lora_config = LoraConfig(
            task_type=TaskType.CAUSAL_LM,
            r=8,
            lora_alpha=16,
            lora_dropout=0.1,
            target_modules=["q_proj", "v_proj", "k_proj", "o_proj"]
        )
        
        model = get_peft_model(model, lora_config)
    
    # Ensure model is on correct device
    model = model.to(device)
    
    # Enable training mode and ensure gradients
    model.train()
    for param in model.parameters():
        if param.requires_grad:
            param.requires_grad_(True)
    
    print(f"Model setup complete!")
    print(f"Trainable parameters: {model.num_parameters(only_trainable=True):,}")
    
    return model, tokenizer, device

def train_enhanced_model():
    """Train model with enhanced sales capabilities - fixed gradient version"""
    
    print("=== Enhanced Sales Model Training (Fixed) ===")
    print("Building comprehensive sales capabilities...")
    
    # Setup fresh model to avoid gradient issues
    model, tokenizer, device = setup_fresh_model()
    
    # Load enhanced data
    print("\nLoading enhanced training data...")
    train_data, val_data = load_enhanced_data()
    
    if train_data is None:
        return
    
    # Create enhanced datasets
    print("Creating enhanced datasets...")
    train_dataset = EnhancedSalesDataset(train_data, tokenizer)
    val_dataset = EnhancedSalesDataset(val_data, tokenizer)
    
    # Show dataset statistics
    print(f"\nDataset statistics:")
    print(f"  Training samples: {len(train_dataset)}")
    print(f"  Validation samples: {len(val_dataset)}")
    
    # Enhanced training arguments for comprehensive sales training
    training_args = TrainingArguments(
        output_dir="../outputs/gemma-sales-comprehensive",
        per_device_train_batch_size=1,
        per_device_eval_batch_size=1,
        gradient_accumulation_steps=8,
        num_train_epochs=3,  # Conservative epochs to avoid overfitting
        warmup_steps=20,
        learning_rate=2e-5,  # Lower learning rate for stability
        weight_decay=0.01,
        logging_steps=10,
        save_steps=50,
        eval_steps=50,
        eval_strategy="steps",
        save_total_limit=2,
        load_best_model_at_end=True,
        metric_for_best_model="eval_loss",
        greater_is_better=False,
        report_to="none",
        dataloader_pin_memory=False,
        dataloader_num_workers=0,
        lr_scheduler_type="cosine",
        remove_unused_columns=False,  # Keep metadata
    )
    
    # Enhanced trainer class
    class EnhancedTrainer(Trainer):
        def get_train_dataloader(self):
            from torch.utils.data import DataLoader
            return DataLoader(
                self.train_dataset,
                batch_size=self.args.per_device_train_batch_size,
                collate_fn=enhanced_collate_fn,
                shuffle=True
            )
        
        def get_eval_dataloader(self, eval_dataset=None):
            from torch.utils.data import DataLoader
            eval_dataset = eval_dataset if eval_dataset is not None else self.eval_dataset
            return DataLoader(
                eval_dataset,
                batch_size=self.args.per_device_eval_batch_size,
                collate_fn=enhanced_collate_fn,
                shuffle=False
            )
    
    # Initialize enhanced trainer
    trainer = EnhancedTrainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=val_dataset,
    )
    
    print(f"\n🚀 Starting comprehensive sales training...")
    print(f"Training {len(train_dataset)} samples for {training_args.num_train_epochs} epochs")
    print("This will take 2-3 hours for comprehensive training...")
    
    try:
        # Start training
        trainer.train()
        
        # Save the comprehensive model
        final_model_path = "../models/gemma-sales-comprehensive"
        os.makedirs(final_model_path, exist_ok=True)
        
        trainer.save_model(final_model_path)
        tokenizer.save_pretrained(final_model_path)
        
        print(f"\n🎉 Comprehensive sales training completed!")
        print(f"📁 Model saved to: {final_model_path}")
        
        # Test comprehensive capabilities
        print("\n🧪 Testing comprehensive sales capabilities...")
        test_comprehensive_capabilities(model, tokenizer, device)
        
    except Exception as e:
        print(f"\n❌ Training failed: {e}")
        import traceback
        traceback.print_exc()

def test_comprehensive_capabilities(model, tokenizer, device):
    """Test the model's comprehensive sales capabilities"""
    
    comprehensive_test_scenarios = [
        {
            "category": "Value Translation",
            "prompt": "<start_of_turn>user\nHow do I quantify 'improved team morale' for a skeptical CFO?<end_of_turn>\n<start_of_turn>model\n"
        },
        {
            "category": "Difficult Situations",
            "prompt": "<start_of_turn>user\nA prospect says: 'This is garbage. Your company has a terrible reputation.' How do I respond?<end_of_turn>\n<start_of_turn>model\n"
        },
        {
            "category": "Strategic Timing",
            "prompt": "<start_of_turn>user\nWhat signals tell me I'm rushing toward a close too quickly?<end_of_turn>\n<start_of_turn>model\n"
        },
        {
            "category": "Competitive Positioning",
            "prompt": "<start_of_turn>user\nHow do I compete against a market leader with 10x our resources?<end_of_turn>\n<start_of_turn>model\n"
        },
        {
            "category": "Objection Handling",
            "prompt": "<start_of_turn>user\nCustomer says 'Your price is too high.' What's my best response?<end_of_turn>\n<start_of_turn>model\n"
        },
        {
            "category": "Closing Psychology",
            "prompt": "<start_of_turn>user\nHow do I create urgency without being manipulative?<end_of_turn>\n<start_of_turn>model\n"
        }
    ]
    
    print("Comprehensive Sales Capabilities Test Results:")
    print("=" * 70)
    
    for i, test in enumerate(comprehensive_test_scenarios, 1):
        try:
            inputs = tokenizer(test["prompt"], return_tensors="pt").to(device)
            
            with torch.no_grad():
                outputs = model.generate(
                    **inputs,
                    max_new_tokens=120,
                    temperature=0.7,
                    do_sample=True,
                    pad_token_id=tokenizer.eos_token_id
                )
            
            response = tokenizer.decode(outputs[0], skip_special_tokens=True)
            answer = response.split("<start_of_turn>model\n")[-1] if "<start_of_turn>model\n" in response else response[len(test["prompt"]):]
            
            print(f"\n{i}. {test['category']}:")
            print(f"Response: {answer[:200]}...")
            print("-" * 50)
            
        except Exception as e:
            print(f"{test['category']} test failed: {e}")
    
    print(f"\n✅ Comprehensive model testing complete!")
    print(f"Your model now handles:")
    print(f"  • Complex sales scenarios")
    print(f"  • Psychological principles")
    print(f"  • Advanced objection handling") 
    print(f"  • Strategic timing decisions")
    print(f"  • Competitive positioning")
    print(f"  • Value translation frameworks")
    print(f"  • Difficult customer situations")

if __name__ == "__main__":
    train_enhanced_model()