#!/usr/bin/env python3
"""
FAST Hybrid Search Server for Chandigarh Policy Assistant

This server uses the performance-optimized hybrid search implementation
to provide sub-5-second responses for production use.
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import time
import config
from performance_fix_hybrid_search import PerformanceOptimizedHybridSearch
import json
import groq

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

    # Analyze query for policy-related content
    question_indicators = {
        'detailed': ['explain', 'details', 'comprehensive', 'complete', 'all about', 'everything about'],
        'specific': ['amount', 'rate', 'fee', 'cost', 'price', 'incentive', 'benefit'],
        'procedure': ['how to', 'process', 'procedure', 'steps', 'apply', 'register'],
        'eligibility': ['eligible', 'qualify', 'criteria', 'requirements', 'conditions'],
        'comparison': ['difference', 'compare', 'vs', 'versus', 'better'],
        'list': ['types', 'categories', 'kinds', 'list', 'what are']
    }
    
    response_style = 'general'
    for style, indicators in question_indicators.items():
        if any(indicator in query_lower for indicator in indicators):
            response_style = style
            break
    
    # Count sources for context richness
    source_count = len([r for r in search_results if r.get('metadata', {}).get('content')])
    
    # Base prompt optimized for Chandigarh policy assistant
    base_prompt = f"""You are the Chandigarh Policy Assistant, an expert AI system specializing in Chandigarh municipal policies, business regulations, industrial policies, and government schemes. Your role is to provide accurate, comprehensive, and helpful information to residents, business owners, and stakeholders.

**USER QUESTION:** {query}

**AVAILABLE POLICY INFORMATION:**
{context}

**RESPONSE GUIDELINES:**

🎯 **PRIMARY OBJECTIVES:**
- Provide detailed, factual answers using ONLY the information from the policy documents above
- Be helpful and comprehensive - users need complete information for important decisions
- Always specify exact amounts, dates, percentages, and conditions when available
- Never hallucinate or invent information not present in the documents

📝 **RESPONSE STRUCTURE (adapt based on question type):**"""

    # Add specific instructions based on query type
    if response_style == 'detailed':
        base_prompt += """
- Start with a comprehensive overview
- Break down information into clear sections with headings
- Include all relevant details, conditions, and requirements
- Mention related policies or cross-references
- Provide contact information if available"""
        
    elif response_style == 'specific':
        base_prompt += """
- Lead with the specific amounts/rates/fees requested
- Present information in clear bullet points or tables if multiple items
- Include any conditions, limitations, or eligibility criteria
- Specify validity periods and update dates"""
        
    elif response_style == 'procedure':
        base_prompt += """
- Provide step-by-step instructions
- List required documents and prerequisites
- Include timelines and processing periods
- Mention relevant departments and contact details
- Note any fees or costs involved"""
        
    elif response_style == 'eligibility':
        base_prompt += """
- List all eligibility criteria clearly
- Separate mandatory vs. optional requirements
- Include any exceptions or special cases
- Mention documentation requirements
- Specify application deadlines if any"""
        
    elif response_style == 'list':
        base_prompt += """
- Provide comprehensive lists with brief descriptions
- Organize information logically (by category, importance, etc.)
- Include relevant details for each item
- Mention any special conditions or limitations"""

    base_prompt += f"""

💡 **CONTENT QUALITY STANDARDS:**
- **Accuracy**: Use exact quotes and figures from policies
- **Completeness**: Include all relevant information ({source_count} sources available)
- **Clarity**: Use bullet points, numbers, and clear headings
- **Practicality**: Focus on actionable information users can use
- **Transparency**: If information is incomplete, clearly state what's missing

🚫 **STRICT PROHIBITIONS:**
- Never invent policy details, amounts, or procedures
- Don't provide outdated information without noting it
- Avoid vague responses like "contact authorities" without specific details
- Don't assume information not explicitly stated in the documents

📋 **FORMATTING:**
- Use bullet points for lists and multiple items
- Bold important amounts, dates, and deadlines
- Include section headers for complex responses
- End with relevant contact information when available

**IMPORTANT:** This is an official policy assistant. Users rely on this information for business decisions, applications, and compliance. Accuracy and completeness are critical.

**YOUR COMPREHENSIVE RESPONSE:**"""
    
    return base_prompt

def initialize_services():
    """Initialize the fast hybrid search and LLM services once."""
    global fast_searcher, groq_client
    
    print("🚀 Initializing Fast Hybrid Search Server...")
    start_time = time.time()
    
    try:
        # Initialize fast searcher
        print("⚡ Loading performance-optimized hybrid search...")
        fast_searcher = PerformanceOptimizedHybridSearch(
            pinecone_api_key=config.PINECONE_API_KEY,
            pinecone_index=config.PINECONE_INDEX,
            alpha=config.DEFAULT_ALPHA,
            fusion_method=config.DEFAULT_FUSION_METHOD,
            cache_dir="cache"
        )
        
        # Initialize Groq client
        print("🤖 Initializing Groq LLM client...")
        groq_client = groq.Groq(api_key=config.GROQ_API_KEY)
        
        total_time = time.time() - start_time
        print(f"✅ Fast server initialization complete in {total_time:.2f}s")
        print(f"🎯 Target response time: <5 seconds")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to initialize services: {e}")
        return False

@app.route('/')
def index():
    """Serve the frontend interface."""
    return send_from_directory('.', 'hybrid_search_frontend.html')

@app.route('/api/search', methods=['POST'])
def search():
    """Fast search endpoint with performance monitoring."""
    start_time = time.time()
    
    try:
        # Parse request
        data = request.json
        query = data.get('message', '').strip()
        
        if not query:
            return jsonify({'error': 'No query provided'}), 400
        
        print(f"\n⚡ FAST SEARCH REQUEST: '{query}'")
        
        # 1. ENHANCED HYBRID SEARCH (get more context for better responses)
        search_start = time.time()
        search_results = fast_searcher.fast_search(query, top_k=6)  # More context
        search_time = time.time() - search_start
        
        print(f"🔍 Search completed in {search_time:.2f}s with {len(search_results)} results")
        
        # 2. ENHANCED CONTEXT PREPARATION
        context_parts = []
        for i, result in enumerate(search_results[:4]):  # Top 4 results for comprehensive answers
            text = result.get('metadata', {}).get('content') or result.get('metadata', {}).get('text', '')
            if text:
                namespace = result.get('namespace', 'unknown')
                score = result.get('score', 0)
                # Longer excerpts for better context
                excerpt = text[:800] + ("..." if len(text) > 800 else "")
                context_parts.append(f"**[Source {i+1} - {namespace}]** (Relevance: {score:.3f})\n{excerpt}")
        
        context = "\n\n".join(context_parts)
        
        # 3. OPTIMIZED PROMPT GENERATION
        llm_start = time.time()
        optimized_prompt = create_optimized_prompt(query, context, search_results)
        
        # Generate LLM response with optimized settings
        try:
            completion = groq_client.chat.completions.create(
                model="llama3-70b-8192",
                messages=[{"role": "user", "content": optimized_prompt}],
                temperature=0.4,  # Balanced for accuracy and human-friendly expressiveness
                max_tokens=800,   # Increased for comprehensive responses
                top_p=0.9,
                stream=False
            )
            
            llm_response = completion.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"⚠️  LLM error: {e}")
            llm_response = "I apologize, but I'm having trouble generating a response at the moment. Please try again."
        
        llm_time = time.time() - llm_start
        total_time = time.time() - start_time
        
        print(f"🤖 Enhanced LLM response in {llm_time:.2f}s")
        print(f"⚡ TOTAL RESPONSE TIME: {total_time:.2f}s")
        
        # Performance assessment (adjusted for comprehensive responses)
        if total_time <= 4:
            performance = "🟢 EXCELLENT"
        elif total_time <= 6:
            performance = "🟡 GOOD" 
        elif total_time <= 10:
            performance = "🟠 ACCEPTABLE"
        else:
            performance = "🔴 SLOW"
        
        print(f"📊 Performance: {performance}")
        
        # Get performance stats
        perf_stats = fast_searcher.get_performance_stats()
        
        # Return comprehensive response
        response = {
            'response': llm_response,
            'query': query,
            'search_results': [
                {
                    'content': (result.get('metadata', {}).get('content') or result.get('metadata', {}).get('text', ''))[:300] + '...',
                    'score': result.get('score', 0),
                    'namespace': result.get('namespace', ''),
                    'sources': result.get('sources', [])
                }
                for result in search_results[:4]
            ],
            'performance': {
                'total_time': f"{total_time:.2f}s",
                'search_time': f"{search_time:.2f}s", 
                'llm_time': f"{llm_time:.2f}s",
                'status': performance,
                'optimization_level': 'comprehensive_v2',
                **perf_stats
            },
            'timestamp': time.time()
        }
        
        return jsonify(response)
        
    except Exception as e:
        error_time = time.time() - start_time
        print(f"❌ Error after {error_time:.2f}s: {e}")
        
        return jsonify({
            'error': str(e),
            'performance': {
                'total_time': f"{error_time:.2f}s",
                'status': '🔴 ERROR'
            }
        }), 500

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get performance statistics."""
    try:
        if fast_searcher:
            stats = fast_searcher.get_performance_stats()
            return jsonify({
                'server_status': 'running',
                'performance_stats': stats,
                'optimization_level': 'maximum'
            })
        else:
            return jsonify({'error': 'Searcher not initialized'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Simple health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'searcher_ready': fast_searcher is not None,
        'llm_ready': groq_client is not None,
        'timestamp': time.time()
    })

if __name__ == '__main__':
    print("🚀 Starting OPTIMIZED Chandigarh Policy Assistant...")
    print("✨ PROMPT OPTIMIZATION: Comprehensive, professional responses enabled!")
    
    if initialize_services():
        print("🌐 Server ready at http://localhost:3003")
        print("📊 Performance dashboard at http://localhost:3003/api/stats")
        print("🎯 Optimized for: Comprehensive, accurate policy responses")
        print("✅ UPGRADE: Enhanced prompt with professional formatting!")
        
        app.run(
            host='0.0.0.0', 
            port=3003, 
            debug=False,  # Disabled for performance
            threaded=True
        )
    else:
        print("❌ Failed to start server - initialization failed")
        exit(1) 