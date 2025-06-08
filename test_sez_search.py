#!/usr/bin/env python3
"""Direct test of SEZ industry search to debug the issue"""

import sys
sys.path.append('.')

from performance_fix_hybrid_search import PerformanceOptimizedHybridSearch
import config

def test_sez_search():
    """Test direct search for SEZ industries"""
    
    print("🔍 Testing SEZ Industry Search...")
    
    # Initialize searcher
    searcher = PerformanceOptimizedHybridSearch(
        pinecone_api_key=config.PINECONE_API_KEY,
        pinecone_index=config.PINECONE_INDEX,
        alpha=0.5,
        fusion_method="rrf",
        cache_dir="cache"
    )
    
    # Test queries
    test_queries = [
        "What industries are allowed in SEZ in Chandigarh?",
        "SEZ industry list Chandigarh",
        "information technology SEZ industry",
        "biotechnology SEZ Chandigarh"
    ]
    
    for query in test_queries:
        print(f"\n📝 QUERY: {query}")
        print("=" * 50)
        
        try:
            results = searcher.fast_search(query, top_k=5)
            
            print(f"Found {len(results)} results:")
            for i, result in enumerate(results):
                print(f"\n{i+1}. Score: {result.get('score', 0):.3f}")
                print(f"   Namespace: {result.get('namespace', 'unknown')}")
                print(f"   ID: {result.get('id', 'unknown')}")
                
                # Check both 'content' and 'text' metadata
                content = result.get('metadata', {}).get('content') or result.get('metadata', {}).get('text', '')
                print(f"   Content: {content[:200]}...")
                
                if 'industries' in content.lower() or 'information technology' in content.lower():
                    print("   ⭐ RELEVANT MATCH!")
                    
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    test_sez_search() 