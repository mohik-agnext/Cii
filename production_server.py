#!/usr/bin/env python3
"""
PRODUCTION-READY Chandigarh Policy Assistant for Railway Deployment

Optimized for cloud deployment with:
- Dynamic port binding
- Persistent cache handling
- Production WSGI server
- Enhanced error handling
- Memory optimization
"""

import os
import sys
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import time
import config
from performance_fix_hybrid_search import PerformanceOptimizedHybridSearch
import json
import groq
from waitress import serve
import logging

# Configure logging for production
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Global variables for the fast searcher and LLM
fast_searcher = None
groq_client = None

def create_optimized_prompt(query, context, search_results):
    """Create an optimized prompt specifically for Chandigarh policy questions"""
    
    query_lower = query.lower().strip()
    
    # Check for ONLY simple greetings - be very specific
    greeting_keywords = ['hello', 'hi', 'hey', 'good morning', 'good afternoon', 'good evening', 'namaste', 'namaskar']
    
    # Only trigger greeting if it's a simple greeting (without policy keywords)
    is_simple_greeting = any(query_lower.startswith(greet) for greet in greeting_keywords)
    is_very_short_greeting = len(query.split()) <= 3 and any(greet in query_lower for greet in greeting_keywords)
    has_policy_words = any(word in query_lower for word in ['policy', 'quota', 'incentive', 'license', 'permit', 'regulation', 'scheme', 'rate', 'fee', 'amount', 'excise', 'ev', 'industrial'])
    
    # Only treat as greeting if it's clearly a greeting AND doesn't contain policy terms
    if (is_simple_greeting or is_very_short_greeting) and not has_policy_words and len(query.split()) <= 5:
        return f"""You are the Chandigarh Policy Assistant, a friendly government AI assistant specializing in Chandigarh policies and services.

The user said: "{query}"

This appears to be a greeting or general inquiry. Respond warmly and welcomingly as a government service representative would. Be conversational, friendly, and helpful.

PROVIDE A WARM GREETING RESPONSE that:
- Welcomes them to the Chandigarh Policy Assistant
- Briefly mentions you can help with government policies, business regulations, industrial policies, permits, and civic services
- Encourages them to ask specific questions about Chandigarh policies
- Uses a warm, conversational tone suitable for government services
- Keeps it brief and friendly (2-3 sentences)

Example tone: "Hello! Welcome to the Chandigarh Policy Assistant. I'm here to help you with information about government policies, business regulations, permits, and civic services in Chandigarh. Please feel free to ask me any specific questions about policies or services you need assistance with!"

DO NOT provide detailed policy information unless specifically requested."""

    # Standard policy response prompt
    base_prompt = f"""You are the Chandigarh Policy Assistant, an expert AI system specializing in Chandigarh municipal policies, business regulations, industrial policies, and government schemes.

**USER QUESTION:** {query}

**AVAILABLE POLICY INFORMATION:**
{context}

**RESPONSE GUIDELINES:**
- Provide detailed, factual answers using ONLY the information from the policy documents above
- Be helpful and comprehensive - users need complete information for important decisions
- Always specify exact amounts, dates, percentages, and conditions when available
- Never hallucinate or invent information not present in the documents
- Use bullet points, numbers, and clear headings for complex responses
- Include relevant contact information when available

**YOUR COMPREHENSIVE RESPONSE:**"""
    
    return base_prompt

def initialize_services():
    """Initialize the fast hybrid search and LLM services once."""
    global fast_searcher, groq_client
    
    logger.info("🚀 Initializing Production Chandigarh Policy Assistant...")
    start_time = time.time()
    
    try:
        # Initialize fast searcher with production cache settings
        logger.info("⚡ Loading performance-optimized hybrid search...")
        fast_searcher = PerformanceOptimizedHybridSearch(
            pinecone_api_key=config.PINECONE_API_KEY,
            pinecone_index=config.PINECONE_INDEX,
            alpha=config.DEFAULT_ALPHA,
            fusion_method=config.DEFAULT_FUSION_METHOD,
            cache_dir="cache"
        )
        
        # Initialize Groq client
        logger.info("🤖 Initializing Groq LLM client...")
        groq_client = groq.Groq(api_key=config.GROQ_API_KEY)
        
        total_time = time.time() - start_time
        logger.info(f"✅ Production server initialization complete in {total_time:.2f}s")
        logger.info(f"🎯 Ready for production traffic")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize services: {e}")
        return False

@app.route('/')
def index():
    """Serve the frontend interface."""
    return send_from_directory('.', 'hybrid_search_frontend.html')

@app.route('/api/search', methods=['POST'])
def search():
    """Production search endpoint with enhanced error handling."""
    start_time = time.time()
    
    try:
        data = request.get_json()
        if not data or 'message' not in data:
            return jsonify({'error': 'No message provided'}), 400
            
        query = data['message'].strip()
        if not query:
            return jsonify({'error': 'Empty query'}), 400
        
        logger.info(f"⚡ PRODUCTION SEARCH: '{query[:50]}...'")
        
        # Perform fast search
        search_start = time.time()
        results = fast_searcher.fast_search(query, top_k=6)
        search_time = time.time() - search_start
        
        # Prepare context
        context = ""
        for result in results:
            content = result.get('metadata', {}).get('content', '')
            if content:
                context += f"\n{content}\n"
        
        # Generate optimized prompt
        prompt = create_optimized_prompt(query, context, results)
        
        # Get LLM response
        llm_start = time.time()
        completion = groq_client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            max_tokens=2000
        )
        llm_time = time.time() - llm_start
        
        response_text = completion.choices[0].message.content
        total_time = time.time() - start_time
        
        # Performance assessment
        if total_time <= 3:
            status = "🟢 EXCELLENT"
        elif total_time <= 5:
            status = "🟡 GOOD"
        else:
            status = "🟠 ACCEPTABLE"
        
        logger.info(f"⚡ TOTAL RESPONSE TIME: {total_time:.2f}s - {status}")
        
        return jsonify({
            'response': response_text,
            'performance': {
                'total_time': f"{total_time:.2f}s",
                'search_time': f"{search_time:.2f}s",
                'llm_time': f"{llm_time:.2f}s",
                'status': status,
                'results_count': len(results)
            }
        })
        
    except Exception as e:
        logger.error(f"❌ Search error: {e}")
        return jsonify({
            'error': 'Search failed',
            'message': 'Please try again or contact support'
        }), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Production health check endpoint."""
    try:
        health_status = {
            'status': 'healthy',
            'timestamp': time.time(),
            'searcher_ready': fast_searcher is not None,
            'llm_ready': groq_client is not None,
            'cache_status': 'loaded' if fast_searcher else 'not_loaded'
        }
        
        if fast_searcher:
            stats = fast_searcher.get_performance_stats()
            health_status.update({
                'queries_processed': stats.get('queries_processed', 0),
                'avg_response_time': stats.get('avg_response_time', 0),
                'production_ready': stats.get('production_ready', False)
            })
        
        return jsonify(health_status)
        
    except Exception as e:
        logger.error(f"❌ Health check failed: {e}")
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': time.time()
        }), 500

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Production statistics endpoint."""
    try:
        if not fast_searcher:
            return jsonify({'error': 'Searcher not initialized'}), 503
            
        stats = fast_searcher.get_performance_stats()
        return jsonify({
            'performance': stats,
            'system': {
                'cache_dir': 'cache',
                'model': 'BAAI/bge-large-en-v1.5',
                'llm': 'llama3-70b-8192',
                'fusion_method': 'rrf'
            }
        })
        
    except Exception as e:
        logger.error(f"❌ Stats error: {e}")
        return jsonify({'error': 'Stats unavailable'}), 500

def main():
    """Main production server entry point."""
    
    # Get port from environment (Railway sets this)
    port = int(os.environ.get('PORT', 3003))
    host = '0.0.0.0'
    
    logger.info(f"🌐 Starting production server on {host}:{port}")
    
    # Initialize services
    if not initialize_services():
        logger.error("❌ Failed to initialize services. Exiting.")
        sys.exit(1)
    
    # Use Waitress for production WSGI serving
    logger.info("🚀 Starting production WSGI server...")
    serve(
        app,
        host=host,
        port=port,
        threads=4,  # Handle multiple requests
        connection_limit=100,
        cleanup_interval=30,
        channel_timeout=120
    )

if __name__ == "__main__":
    main() 