import json
import os
from sklearn.model_selection import train_test_split

def load_sales_framework_data(json_file_path):
    """
    Load your sales data - handles both formats:
    1. Direct array: [{id, question, answer}, ...]  
    2. Wrapped format: {"SalesFramework": [{...}]}
    """
    with open(json_file_path, 'r') as f:
        data = json.load(f)
    
    # Check if it's wrapped in SalesFramework or direct array
    if isinstance(data, dict) and 'SalesFramework' in data:
        sales_data = data['SalesFramework']
        print(f"✓ Loaded {len(sales_data)} Q&A pairs from SalesFramework wrapper")
    elif isinstance(data, list):
        sales_data = data
        print(f"✓ Loaded {len(sales_data)} Q&A pairs from direct array")
    else:
        raise ValueError("❌ Unexpected JSON format. Expected array or {SalesFramework: array}")
    
    # Verify the structure
    if sales_data and len(sales_data) > 0:
        first_item = sales_data[0]
        required_keys = ['id', 'question', 'answer']
        missing_keys = [key for key in required_keys if key not in first_item]
        
        if missing_keys:
            print(f"❌ Missing keys in data: {missing_keys}")
            print(f"Available keys: {list(first_item.keys())}")
            return None
    
    return sales_data

def prepare_gemma_format(sales_data):
    """
    Convert your data to Gemma training format
    """
    formatted_data = []
    
    for item in sales_data:
        # Create the conversation format that Gemma expects
        formatted_text = f"<start_of_turn>user\n{item['question']}<end_of_turn>\n<start_of_turn>model\n{item['answer']}<end_of_turn>"
        
        formatted_data.append({
            "text": formatted_text,
            "id": item['id'],
            "data_type": "text_only"
        })
    
    return formatted_data

def split_and_save_data(formatted_data, train_ratio=0.8):
    """
    Split data into train/validation and save
    """
    # Make sure data directory exists
    os.makedirs('../data', exist_ok=True)
    
    # Split the data
    train_data, val_data = train_test_split(
        formatted_data, 
        train_size=train_ratio,
        random_state=42,
        shuffle=True
    )
    
    # Create metadata
    train_metadata = {
        "total_samples": len(train_data),
        "original_ids": [item['id'] for item in train_data],
        "format": "gemma_sales_framework"
    }
    
    val_metadata = {
        "total_samples": len(val_data),
        "original_ids": [item['id'] for item in val_data],
        "format": "gemma_sales_framework"
    }
    
    # Save training data
    with open('../data/train_data.json', 'w') as f:
        json.dump({"data": train_data, "metadata": train_metadata}, f, indent=2)
    
    # Save validation data
    with open('../data/val_data.json', 'w') as f:
        json.dump({"data": val_data, "metadata": val_metadata}, f, indent=2)
    
    print(f"✓ Training samples: {len(train_data)}")
    print(f"✓ Validation samples: {len(val_data)}")
    print(f"✓ Train/Val split: {train_ratio:.0%}/{(1-train_ratio):.0%}")
    print("✓ Data saved to ../data/ directory")
    
    # Show sample
    print(f"\nSample training example (ID: {train_data[0]['id']}):")
    print("-" * 60)
    print("Question:", train_data[0]['text'].split('<end_of_turn>')[0].replace('<start_of_turn>user\n', ''))
    print("Answer:", train_data[0]['text'].split('<start_of_turn>model\n')[1].replace('<end_of_turn>', ''))
    
    return train_data, val_data

def main():
    print("=== Sales Framework Data Preparation ===")
    
    # Look for JSON files in the parent directory
    possible_files = [f for f in os.listdir('..') if f.endswith('.json')]
    
    if possible_files:
        print(f"Found JSON files: {possible_files}")
        json_file = input(f"Enter filename (or press Enter for first file '{possible_files[0]}'): ").strip()
        if not json_file:
            json_file = possible_files[0]
        json_file_path = f"../{json_file}"
    else:
        json_file_path = input("Enter the full path to your sales JSON file: ").strip()
    
    if not os.path.exists(json_file_path):
        print(f"❌ File not found: {json_file_path}")
        return
    
    try:
        # Load your data
        sales_data = load_sales_framework_data(json_file_path)
        
        if sales_data is None:
            return
        
        # Convert to Gemma format
        formatted_data = prepare_gemma_format(sales_data)
        
        # Split and save
        train_data, val_data = split_and_save_data(formatted_data)
        
        print(f"\n✅ Data preparation complete!")
        print(f"Ready for training with {len(sales_data)} total Q&A pairs")
        print(f"\nNext step: python train_model.py")
        
    except Exception as e:
        print(f"❌ Error processing data: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()