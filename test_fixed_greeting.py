#!/usr/bin/env python3
"""
Test script to verify the fixed greeting detection logic
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fast_hybrid_search_server import create_optimized_prompt
import groq
import config

def test_greeting_fix():
    """Test the fixed greeting detection"""
    
    groq_client = groq.Groq(api_key=config.GROQ_API_KEY)
    
    test_cases = [
        {
            'type': 'SHOULD BE GREETING',
            'query': 'hello',
            'expected': 'greeting'
        },
        {
            'type': 'SHOULD BE GREETING', 
            'query': 'hi there',
            'expected': 'greeting'
        },
        {
            'type': 'SHOULD BE POLICY (NOT GREETING)',
            'query': 'What is the total basic quota of Indian Made Foreign Liquor (IMFL), Country Liquor (CL), and Imported Foreign Liquor (Bio Brands i.e. Whisky) to be allotted as per the Excise Policy Chandigarh 2024-25?',
            'expected': 'policy'
        },
        {
            'type': 'SHOULD BE POLICY (NOT GREETING)',
            'query': 'what are the EV incentives',
            'expected': 'policy'
        },
        {
            'type': 'SHOULD BE POLICY (NOT GREETING)',
            'query': 'tell me about industrial policy',
            'expected': 'policy'
        }
    ]
    
    print("🧪 Testing Fixed Greeting Detection Logic")
    print("=" * 60)
    
    for test in test_cases:
        print(f"\n📝 {test['type']}")
        print(f"Query: '{test['query']}'")
        
        # Test the prompt creation directly
        prompt = create_optimized_prompt(test['query'], "", [])
        
        # Check if it's a greeting response
        is_greeting_response = "This appears to be a greeting" in prompt
        
        print(f"Expected: {test['expected']}")
        print(f"Detected as: {'greeting' if is_greeting_response else 'policy'}")
        
        if test['expected'] == 'greeting' and is_greeting_response:
            print("✅ CORRECT - Properly detected as greeting")
        elif test['expected'] == 'policy' and not is_greeting_response:
            print("✅ CORRECT - Properly detected as policy question")
        else:
            print("❌ WRONG - Detection failed!")
            
        print("-" * 40)

if __name__ == "__main__":
    test_greeting_fix() 