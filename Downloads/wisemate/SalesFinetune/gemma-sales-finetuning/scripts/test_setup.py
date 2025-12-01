import os
import sys

def test_project_structure():
    """Test that all directories and files are in place"""
    
    print("=== Testing Project Structure ===")
    
    # Check if we're in the scripts directory
    current_dir = os.getcwd()
    print(f"Current directory: {current_dir}")
    
    # Check parent directory structure
    parent_dir = os.path.dirname(current_dir)
    expected_dirs = ['data', 'models', 'outputs', 'scripts']
    
    print(f"\nChecking parent directory: {parent_dir}")
    for dir_name in expected_dirs:
        dir_path = os.path.join(parent_dir, dir_name)
        if os.path.exists(dir_path):
            print(f"✓ {dir_name}/ exists")
        else:
            print(f"❌ {dir_name}/ missing")
    
    # Check for JSON files in parent
    json_files = [f for f in os.listdir(parent_dir) if f.endswith('.json')]
    if json_files:
        print(f"✓ Found JSON files: {json_files}")
    else:
        print("⚠ No JSON files found in parent directory")
    
    # Check current scripts directory
    print(f"\nChecking scripts directory:")
    script_files = [f for f in os.listdir('.') if f.endswith('.py')]
    expected_scripts = ['model_setup_multimodal.py', 'prepare_sales_framework_data.py', 'test_setup.py']
    
    for script in expected_scripts:
        if script in script_files:
            print(f"✓ {script} exists")
        else:
            print(f"❌ {script} missing")
    
    return json_files

def test_imports():
    """Test that required packages can be imported"""
    
    print("\n=== Testing Package Imports ===")
    
    try:
        import torch
        print(f"✓ PyTorch {torch.__version__}")
        
        if torch.backends.mps.is_available():
            print("✓ MPS (Metal Performance Shaders) available")
        else:
            print("⚠ MPS not available, will use CPU")
            
    except ImportError as e:
        print(f"❌ PyTorch import failed: {e}")
        return False
    
    try:
        import transformers
        print(f"✓ Transformers {transformers.__version__}")
    except ImportError as e:
        print(f"❌ Transformers import failed: {e}")
        return False
    
    try:
        import peft
        print(f"✓ PEFT {peft.__version__}")
    except ImportError as e:
        print(f"❌ PEFT import failed: {e}")
        return False
    
    try:
        from sklearn.model_selection import train_test_split
        print("✓ Scikit-learn")
    except ImportError as e:
        print(f"❌ Scikit-learn import failed: {e}")
        return False
    
    return True

def main():
    json_files = test_project_structure()
    imports_ok = test_imports()
    
    print("\n=== Summary ===")
    if imports_ok:
        print("✅ All packages imported successfully")
    else:
        print("❌ Some package imports failed")
        
    if json_files:
        print(f"✅ Ready to process: {json_files}")
        print("\nNext steps:")
        print("1. Run: python prepare_sales_framework_data.py")
        print("2. Then: python model_setup_multimodal.py")
    else:
        print("⚠ Place your JSON file in the parent directory first")

if __name__ == "__main__":
    main()
