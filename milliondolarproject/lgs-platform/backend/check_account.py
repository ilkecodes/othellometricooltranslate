#!/usr/bin/env python3
"""Check Anthropic account info and usage."""

import os
from anthropic import Anthropic

def check_account_info():
    """Check account information and available models."""
    
    api_key = os.getenv('ANTHROPIC_API_KEY')
    if not api_key:
        print("✗ ANTHROPIC_API_KEY environment variable not set")
        return
    
    print("✓ API key found")
    print(f"✓ API key starts with: {api_key[:15]}...")
    
    client = Anthropic(api_key=api_key)
    
    # Let's try to make a call and see the exact error details
    try:
        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=10,
            messages=[{"role": "user", "content": "test"}]
        )
        print("✅ Claude 3.5 Sonnet is available!")
        
    except Exception as e:
        print(f"❌ Claude 3.5 Sonnet error details:")
        print(f"   Full error: {e}")
        print(f"   Error type: {type(e)}")
        
        # Check if it's a billing issue vs model availability
        if "credit balance" in str(e).lower():
            print("🔍 Issue: Insufficient credits")
        elif "not_found_error" in str(e):
            print("🔍 Issue: Model not found/not available to your account")
        elif "permission" in str(e).lower():
            print("🔍 Issue: Permission/tier limitation")
        else:
            print("🔍 Issue: Unknown error")

if __name__ == "__main__":
    check_account_info()