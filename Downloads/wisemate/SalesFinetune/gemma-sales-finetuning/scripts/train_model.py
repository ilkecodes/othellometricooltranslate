import json
import torch
from datasets import Dataset
from transformers import TrainingArguments, Trainer
from model_setup_multimodal import setup_multimodal_model
import os

def load_and_process_data():
    """Load and process data in a simpler way"""
    
    if not os.path.exists('../data/train_data.json') or not os.path.exists('../data/val_data.json'):
        print("❌ Training data not found!")
        return None, None, None
    
    with open('../data/train_data.json', 'r') as f:
        train_raw = json.load(f)
    
    with open('../data/val_data.json', 'r') as f:
        val_raw = json.load(f)
    
    train_data = train_raw['data']
    val_data = val_raw['data']
    
    # Extract just the text
    train_texts = [item['text'] for item in train_data]
    val_texts = [item['text'] for item in val_data]
    
    print(f"✓ Loaded {len(train_texts)} training samples")
    print(f"✓ Loaded {len(val_texts)} validation samples")
    
    return train_texts, val_texts, None

class SimpleDataset:
    """Simple dataset class that handles tokenization properly"""
    
    def __init__(self, texts, tokenizer, max_length=512):
        self.texts = texts
        self.tokenizer = tokenizer
        self.max_length = max_length
        
    def __len__(self):
        return len(self.texts)
    
    def __getitem__(self, idx):
        text = self.texts[idx]
        
        # Tokenize
        encoding = self.tokenizer(
            text,
            truncation=True,
            padding=False,
            max_length=self.max_length,
            return_tensors=None,
            add_special_tokens=False  # Gemma format already has them
        )
        
        # Return as dict with lists (not tensors yet)
        return {
            'input_ids': encoding['input_ids'],
            'attention_mask': encoding['attention_mask'],
            'labels': encoding['input_ids'].copy()  # For causal LM
        }

def simple_collate_fn(batch):
    """Custom collate function"""
    
    # Get max length in batch
    max_len = max(len(item['input_ids']) for item in batch)
    
    # Pad all sequences to max length
    input_ids = []
    attention_masks = []
    labels = []
    
    for item in batch:
        input_id = item['input_ids']
        attention_mask = item['attention_mask']
        label = item['labels']
        
        # Pad
        pad_length = max_len - len(input_id)
        
        input_ids.append(input_id + [0] * pad_length)  # 0 is pad token
        attention_masks.append(attention_mask + [0] * pad_length)
        labels.append(label + [-100] * pad_length)  # -100 for ignore in loss
    
    return {
        'input_ids': torch.tensor(input_ids, dtype=torch.long),
        'attention_mask': torch.tensor(attention_masks, dtype=torch.long),
        'labels': torch.tensor(labels, dtype=torch.long)
    }

def train_model():
    """Main training function with simplified approach"""
    
    print("=== Starting Gemma Sales Fine-tuning (Simplified) ===")
    
    # Setup model and tokenizer
    print("Setting up model...")
    model, tokenizer, device = setup_multimodal_model()
    
    # Load data
    print("Loading datasets...")
    train_texts, val_texts, _ = load_and_process_data()
    
    if train_texts is None:
        return
    
    # Create datasets
    print("Creating datasets...")
    train_dataset = SimpleDataset(train_texts, tokenizer)
    val_dataset = SimpleDataset(val_texts, tokenizer)
    
    # Show sample
    print(f"Sample data structure:")
    sample = train_dataset[0]
    print(f"  Input IDs length: {len(sample['input_ids'])}")
    print(f"  First few tokens: {sample['input_ids'][:10]}")
    
    # Training arguments - very conservative
    training_args = TrainingArguments(
        output_dir="../outputs/gemma-sales-simple",
        per_device_train_batch_size=1,  # Start with 1
        per_device_eval_batch_size=1,
        gradient_accumulation_steps=4,
        num_train_epochs=3,  # Fewer epochs
        warmup_steps=5,
        learning_rate=5e-5,
        logging_steps=5,
        save_steps=50,
        eval_steps=50,
        eval_strategy="steps",
        save_total_limit=1,
        report_to="none",
        dataloader_pin_memory=False,
        dataloader_num_workers=0,  # Disable multiprocessing
    )
    
    # Custom trainer with our collate function
    class SimpleTrainer(Trainer):
        def get_train_dataloader(self):
            from torch.utils.data import DataLoader
            return DataLoader(
                self.train_dataset,
                batch_size=self.args.per_device_train_batch_size,
                collate_fn=simple_collate_fn,
                shuffle=True
            )
        
        def get_eval_dataloader(self, eval_dataset=None):
            from torch.utils.data import DataLoader
            eval_dataset = eval_dataset if eval_dataset is not None else self.eval_dataset
            return DataLoader(
                eval_dataset,
                batch_size=self.args.per_device_eval_batch_size,
                collate_fn=simple_collate_fn,
                shuffle=False
            )
    
    # Initialize trainer
    trainer = SimpleTrainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=val_dataset,
    )
    
    print("\n🚀 Starting training...")
    print("Progress will be shown below...")
    
    try:
        trainer.train()
        
        # Save the model
        final_model_path = "../models/gemma-sales-simple"
        os.makedirs(final_model_path, exist_ok=True)
        
        trainer.save_model(final_model_path)
        tokenizer.save_pretrained(final_model_path)
        
        print(f"\n✅ Training completed!")
        print(f"📁 Model saved to: {final_model_path}")
        
        # Quick test
        print("\n🧪 Testing the model...")
        test_quick(model, tokenizer, device)
        
    except Exception as e:
        print(f"\n❌ Training failed: {e}")
        import traceback
        traceback.print_exc()

def test_quick(model, tokenizer, device):
    """Quick test of the trained model"""
    
    test_prompt = "<start_of_turn>user\nWhat drives sales success?<end_of_turn>\n<start_of_turn>model\n"
    
    try:
        inputs = tokenizer(test_prompt, return_tensors="pt").to(device)
        
        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_new_tokens=50,
                temperature=0.8,
                do_sample=True,
                pad_token_id=tokenizer.eos_token_id
            )
        
        response = tokenizer.decode(outputs[0], skip_special_tokens=True)
        answer = response.split("<start_of_turn>model\n")[-1] if "<start_of_turn>model\n" in response else response[len(test_prompt):]
        
        print("Quick test result:")
        print(f"Q: What drives sales success?")
        print(f"A: {answer[:100]}...")
        
    except Exception as e:
        print(f"Test failed: {e}")

if __name__ == "__main__":
    train_model()