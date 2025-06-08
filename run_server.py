#!/usr/bin/env python3
"""
Simple server runner for Chandigarh Policy Assistant
Starts the optimized fast hybrid search server
"""

import os
import sys

if __name__ == "__main__":
    print("🚀 Starting Chandigarh Policy Assistant...")
    
    # Check if config.py exists
    if not os.path.exists('config.py'):
        print("❌ config.py not found. Please copy config.py.example to config.py and configure your settings.")
        sys.exit(1)
    
    # Start the fast server
    os.system("python fast_hybrid_search_server.py") 