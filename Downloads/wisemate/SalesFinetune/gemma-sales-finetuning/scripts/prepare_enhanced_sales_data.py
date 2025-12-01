import json
import os
from sklearn.model_selection import train_test_split

def load_complex_sales_data(json_file_path):
    """
    Load your complex sales data structure
    """
    with open(json_file_path, 'r') as f:
        data = json.load(f)
    
    all_training_examples = []
    
    # Handle the direct array format from your data.json
    if isinstance(data, list):
        for item in data:
            # Handle simple Q&A format (your Q1-Q54 entries)
            if 'question' in item and 'answer' in item:
                all_training_examples.append({
                    'id': item.get('id', 'unknown'),
                    'question': item['question'],
                    'answer': item['answer'],
                    'type': 'simple_qa'
                })
            
            # Handle nested structures within the array
            elif 'sales_training_dataset' in item:
                # Process conversation starters, qualification scenarios, etc.
                dataset = item['sales_training_dataset']
                
                for category_name, category_data in dataset.items():
                    if category_name == 'metadata':
                        continue
                    
                    if isinstance(category_data, list):
                        for training_item in category_data:
                            all_training_examples.append({
                                'id': training_item.get('id', f"{category_name}_unknown"),
                                'question': training_item.get('question', ''),
                                'answer': training_item.get('answer', ''),
                                'type': 'enhanced_skill',
                                'category': category_name
                            })
            
            # Handle missing_critical_skills sections
            elif 'missing_critical_skills' in item:
                skills = item['missing_critical_skills']
                for skill_category, skill_data in skills.items():
                    if isinstance(skill_data, list):
                        for skill_item in skill_data:
                            all_training_examples.append({
                                'id': skill_item.get('id', f"{skill_category}_unknown"),
                                'question': skill_item.get('question', ''),
                                'answer': skill_item.get('answer', ''),
                                'type': 'critical_skill',
                                'category': skill_category
                            })
            
            # Handle complex scenario data
            elif 'training_data' in item:
                for scenario in item['training_data']:
                    # Use expert_response if available, otherwise answer
                    response = scenario.get('expert_response', scenario.get('answer', ''))
                    
                    all_training_examples.append({
                        'id': scenario.get('id', 'scenario_unknown'),
                        'question': scenario.get('question', ''),
                        'answer': response,
                        'type': 'rich_scenario',
                        'category': scenario.get('category', 'general'),
                        'context': scenario.get('context', ''),
                        'psychological_principle': scenario.get('psychological_principle', ''),
                        'difficulty': scenario.get('difficulty', 'medium'),
                        'success_factors': scenario.get('success_factors', []),
                        'common_mistakes': scenario.get('common_mistakes', [])
                    })
    
    print(f"✓ Loaded {len(all_training_examples)} training examples")
    
    # Show breakdown by type
    type_counts = {}
    for example in all_training_examples:
        example_type = example['type']
        type_counts[example_type] = type_counts.get(example_type, 0) + 1
    
    print("Data breakdown:")
    for type_name, count in type_counts.items():
        print(f"  {type_name}: {count} examples")
    
    return all_training_examples

def format_for_gemma_training(training_examples):
    """
    Convert to Gemma conversation format with enhanced context
    """
    formatted_data = []
    
    for example in training_examples:
        base_text = ""
        
        if example['type'] == 'simple_qa':
            # Basic Q&A format
            base_text = f"<start_of_turn>user\n{example['question']}<end_of_turn>\n<start_of_turn>model\n{example['answer']}<end_of_turn>"
            
        elif example['type'] in ['enhanced_skill', 'critical_skill']:
            # Enhanced format
            base_text = f"<start_of_turn>user\n{example['question']}<end_of_turn>\n<start_of_turn>model\n{example['answer']}<end_of_turn>"
            
        elif example['type'] == 'rich_scenario':
            # Rich scenario with context and principles
            context_part = f"\n\nContext: {example['context']}" if example.get('context') else ""
            principle_part = f"\n\nKey principle: {example['psychological_principle']}" if example.get('psychological_principle') else ""
            
            base_text = f"<start_of_turn>user\n{example['question']}{context_part}<end_of_turn>\n<start_of_turn>model\n{example['answer']}{principle_part}<end_of_turn>"
        
        else:
            # Fallback
            base_text = f"<start_of_turn>user\n{example['question']}<end_of_turn>\n<start_of_turn>model\n{example['answer']}<end_of_turn>"
        
        formatted_data.append({
            "text": base_text,
            "id": example['id'],
            "data_type": example['type'],
            "category": example.get('category', 'general'),
            "difficulty": example.get('difficulty', 'medium')
        })
    
    return formatted_data

def split_and_save_data(formatted_data, train_ratio=0.8):
    """
    Split and save with comprehensive metadata
    """
    os.makedirs('../data', exist_ok=True)
    
    # Split data
    train_data, val_data = train_test_split(
        formatted_data,
        train_size=train_ratio,
        random_state=42,
        shuffle=True
    )
    
    # Create metadata
    train_metadata = {
        "total_samples": len(train_data),
        "data_types": {},
        "categories": {},
        "difficulties": {},
        "format": "gemma_comprehensive_sales"
    }
    
    val_metadata = {
        "total_samples": len(val_data),
        "data_types": {},
        "categories": {},
        "difficulties": {},
        "format": "gemma_comprehensive_sales"
    }
    
    # Count distributions
    for dataset, metadata in [(train_data, train_metadata), (val_data, val_metadata)]:
        for item in dataset:
            # Data types
            dtype = item['data_type']
            metadata['data_types'][dtype] = metadata['data_types'].get(dtype, 0) + 1
            
            # Categories
            category = item['category']
            metadata['categories'][category] = metadata['categories'].get(category, 0) + 1
            
            # Difficulties
            difficulty = item['difficulty']
            metadata['difficulties'][difficulty] = metadata['difficulties'].get(difficulty, 0) + 1
    
    # Save data
    with open('../data/train_data.json', 'w') as f:
        json.dump({"data": train_data, "metadata": train_metadata}, f, indent=2)
    
    with open('../data/val_data.json', 'w') as f:
        json.dump({"data": val_data, "metadata": val_metadata}, f, indent=2)
    
    print(f"✓ Training samples: {len(train_data)}")
    print(f"✓ Validation samples: {len(val_data)}")
    print(f"✓ Train/Val split: {train_ratio:.0%}/{(1-train_ratio):.0%}")
    
    # Show distribution
    print(f"\nTraining data distribution:")
    print(f"  Data types: {train_metadata['data_types']}")
    print(f"  Top categories: {dict(list(train_metadata['categories'].items())[:5])}")
    print(f"  Difficulties: {train_metadata['difficulties']}")
    
    # Sample
    sample_item = train_data[0]
    print(f"\nSample training example (ID: {sample_item['id']}):")
    print(f"Type: {sample_item['data_type']}, Category: {sample_item['category']}")
    print("-" * 60)
    sample_text = sample_item['text']
    if len(sample_text) > 300:
        print(sample_text[:300] + "...")
    else:
        print(sample_text)
    
    return train_data, val_data

def main():
    print("=== Comprehensive Sales Data Preparation ===")
    
    # Look for data.json specifically
    json_file_path = '../data.json'
    
    if not os.path.exists(json_file_path):
        print(f"❌ File not found: {json_file_path}")
        print("Please make sure data.json is in the parent directory")
        return
    
    try:
        # Load the complex data
        training_examples = load_complex_sales_data(json_file_path)
        
        if not training_examples:
            print("❌ No training examples found")
            return
        
        # Convert to Gemma format
        formatted_data = format_for_gemma_training(training_examples)
        
        # Split and save
        train_data, val_data = split_and_save_data(formatted_data)
        
        print(f"\n✅ Comprehensive data preparation complete!")
        print(f"Ready for training with {len(training_examples)} total examples")
        print(f"Next step: python train_enhanced_model.py")
        
    except Exception as e:
        print(f"❌ Error processing data: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()