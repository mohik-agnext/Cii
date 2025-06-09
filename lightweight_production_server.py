#!/usr/bin/env python3
"""
LIGHTWEIGHT Chandigarh Policy Assistant for Railway Deployment
Using OpenAI embeddings instead of sentence-transformers to reduce image size
"""

import os
import sys
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import time
import config
import json
import groq
import openai
from waitress import serve
import logging
import pinecone
from rank_bm25 import BM25Okapi
import pickle
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import numpy as np

# Configure logging for production
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Global variables
groq_client = None
openai_client = None
pc = None
index = None
bm25 = None
documents = []

def create_optimized_prompt(query, context):
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

def preprocess_text(text):
    """Simple text preprocessing without heavy dependencies"""
    try:
        # Download required NLTK data if not present
        try:
            stopwords.words('english')
        except LookupError:
            nltk.download('stopwords', quiet=True)
        
        try:
            word_tokenize("test")
        except LookupError:
            nltk.download('punkt', quiet=True)
        
        # Tokenize and remove stopwords
        tokens = word_tokenize(text.lower())
        stop_words = set(stopwords.words('english'))
        tokens = [token for token in tokens if token.isalnum() and token not in stop_words]
        return tokens
    except Exception as e:
        logger.warning(f"NLTK preprocessing failed: {e}, using simple split")
        # Fallback to simple preprocessing
        return text.lower().split()

def search_documents(query, top_k=6):
    """Lightweight search using BM25 and OpenAI embeddings"""
    try:
        # BM25 search
        query_tokens = preprocess_text(query)
        bm25_scores = bm25.get_scores(query_tokens)
        
        # Get OpenAI embedding for semantic search
        embedding_response = openai_client.embeddings.create(
            model="text-embedding-ada-002",
            input=query
        )
        query_embedding = embedding_response.data[0].embedding
        
        # Search Pinecone
        search_results = index.query(
            vector=query_embedding,
            top_k=top_k,
            include_metadata=True
        )
        
        results = []
        for match in search_results.matches:
            results.append({
                'metadata': match.metadata,
                'score': match.score
            })
        
        return results
        
    except Exception as e:
        logger.error(f"Search error: {e}")
        # Fallback to BM25 only
        query_tokens = preprocess_text(query)
        bm25_scores = bm25.get_scores(query_tokens)
        top_indices = np.argsort(bm25_scores)[-top_k:][::-1]
        
        results = []
        for i, idx in enumerate(top_indices):
            if idx < len(documents):
                results.append({
                    'metadata': {'content': documents[idx]},
                    'score': float(bm25_scores[idx])
                })
        return results

def initialize_services():
    """Initialize the lightweight search and LLM services"""
    global groq_client, openai_client, pc, index, bm25, documents
    
    logger.info("🚀 Initializing Lightweight Chandigarh Policy Assistant...")
    start_time = time.time()
    
    try:
        # Initialize API clients
        logger.info("🤖 Initializing API clients...")
        groq_client = groq.Groq(api_key=config.GROQ_API_KEY)
        openai_client = openai.OpenAI(api_key=getattr(config, 'OPENAI_API_KEY', 'dummy'))
        
        # Initialize Pinecone
        logger.info("🔗 Connecting to Pinecone...")
        pc = pinecone.Pinecone(api_key=config.PINECONE_API_KEY)
        index = pc.Index(config.PINECONE_INDEX)
        
        # Load or create BM25 index
        logger.info("📦 Loading BM25 index...")
        try:
            with open('cache/bm25_index.pkl', 'rb') as f:
                bm25 = pickle.load(f)
            with open('cache/documents.pkl', 'rb') as f:
                documents = pickle.load(f)
            logger.info(f"✅ BM25 cache loaded ({len(documents)} documents)")
        except FileNotFoundError:
            logger.warning("BM25 cache not found, creating minimal index...")
            # Create minimal BM25 index
            sample_docs = ["Chandigarh policy documents", "EV policy information", "Industrial policy details"]
            tokenized_docs = [preprocess_text(doc) for doc in sample_docs]
            bm25 = BM25Okapi(tokenized_docs)
            documents = sample_docs
        
        total_time = time.time() - start_time
        logger.info(f"✅ Lightweight server initialization complete in {total_time:.2f}s")
        logger.info(f"🎯 Ready for production traffic")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize services: {e}")
        return False

@app.route('/')
def index_route():
    """Serve the frontend interface."""
    return send_from_directory('.', 'hybrid_search_frontend.html')

@app.route('/api/search', methods=['POST'])
def search():
    """Lightweight search endpoint"""
    start_time = time.time()
    
    try:
        data = request.get_json()
        if not data or 'message' not in data:
            return jsonify({'error': 'No message provided'}), 400
            
        query = data['message'].strip()
        if not query:
            return jsonify({'error': 'Empty query'}), 400
        
        logger.info(f"⚡ LIGHTWEIGHT SEARCH: '{query[:50]}...'")
        
        # Perform search
        search_start = time.time()
        results = search_documents(query, top_k=6)
        search_time = time.time() - search_start
        
        # Prepare context
        context = ""
        for result in results:
            content = result.get('metadata', {}).get('content', '')
            if content:
                context += f"\n{content}\n"
        
        # Generate optimized prompt
        prompt = create_optimized_prompt(query, context)
        
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
    """Health check endpoint for Railway"""
    try:
        # Basic health checks
        health_status = {
            'status': 'healthy',
            'timestamp': time.time(),
            'groq_ready': groq_client is not None,
            'pinecone_ready': index is not None,
            'bm25_ready': bm25 is not None
        }
        
        return jsonify(health_status), 200
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({
            'status': 'unhealthy',
            'error': str(e)
        }), 500

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Performance statistics endpoint"""
    try:
        stats = {
            'server_type': 'lightweight',
            'dependencies': 'minimal',
            'image_size': 'optimized',
            'timestamp': time.time()
        }
        return jsonify(stats), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def main():
    """Main function to run the production server"""
    # Get port from environment (Railway sets this)
    port = int(os.environ.get('PORT', 8080))
    
    # Initialize services
    if not initialize_services():
        logger.error("Failed to initialize services, exiting...")
        sys.exit(1)
    
    # Run production server
    logger.info(f"🚀 Starting lightweight production server on port {port}")
    serve(app, host='0.0.0.0', port=port, threads=4)

if __name__ == '__main__':
    main() 