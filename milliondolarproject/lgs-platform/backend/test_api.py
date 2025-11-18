#!/usr/bin/env python3
"""Quick test script to check Anthropic API availability and models."""

import os
from anthropic import Anthropic

def test_anthropic_api():
    """Test basic Anthropic API functionality."""
    
    # Check if API key is available
    api_key = os.getenv('ANTHROPIC_API_KEY')
    if not api_key:
        print("✗ ANTHROPIC_API_KEY environment variable not set")
        return
    
    print("✓ API key found")
    
    # Test simple API call with different model names
    client = Anthropic(api_key=api_key)
    
    models_to_try = [
        "claude-3-5-sonnet-20241022",
        "claude-3-5-sonnet-20240620", 
        "claude-3-5-sonnet",
        "claude-3-sonnet-20240229",
        "claude-3-sonnet",
        "claude-3-haiku-20240307",
        "claude-3-haiku",
        "claude-3-opus-20240229",
        "claude-3-opus"
    ]
    
    test_prompt = "Hello! Please respond with just 'API working' to confirm."
    
    for model in models_to_try:
        try:
            print(f"🧪 Testing model: {model}")
            response = client.messages.create(
                model=model,
                max_tokens=20,
                messages=[{"role": "user", "content": test_prompt}]
            )
            print(f"✅ {model} - Working!")
            print(f"   Response: {response.content[0].text}")
            return model  # Return first working model
            
        except Exception as e:
            print(f"❌ {model} - Error: {e}")
            continue
    
    print("✗ No working models found")
    return None

if __name__ == "__main__":
    working_model = test_anthropic_api()
    if working_model:
        print(f"\n🎯 Recommended model: {working_model}")