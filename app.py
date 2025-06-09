#!/usr/bin/env python3
"""
Chandigarh Policy Assistant - Hugging Face Spaces Version
Full quality with free GPU access on HF Spaces
"""

import gradio as gr
import os
import time
import config
from performance_fix_hybrid_search import PerformanceOptimizedHybridSearch
import groq

# Global variables
searcher = None
groq_client = None

def initialize_system():
    """Initialize the full-quality system"""
    global searcher, groq_client
    
    print("🚀 Initializing FULL-QUALITY Chandigarh Policy Assistant...")
    
    # Initialize searcher with full performance
    searcher = PerformanceOptimizedHybridSearch(
        pinecone_api_key=config.PINECONE_API_KEY,
        pinecone_index=config.PINECONE_INDEX,
        alpha=config.DEFAULT_ALPHA,
        fusion_method=config.DEFAULT_FUSION_METHOD,
        cache_dir="cache"
    )
    
    # Initialize Groq
    groq_client = groq.Groq(api_key=config.GROQ_API_KEY)
    
    print("✅ Full-quality system ready!")

def create_optimized_prompt(query, context, search_results):
    """Your existing optimized prompt function"""
    query_lower = query.lower().strip()
    
    # Greeting detection logic
    greeting_keywords = ['hello', 'hi', 'hey', 'good morning', 'good afternoon', 'good evening', 'namaste', 'namaskar']
    is_simple_greeting = any(query_lower.startswith(greet) for greet in greeting_keywords)
    is_very_short_greeting = len(query.split()) <= 3 and any(greet in query_lower for greet in greeting_keywords)
    has_policy_words = any(word in query_lower for word in ['policy', 'quota', 'incentive', 'license', 'permit', 'regulation', 'scheme', 'rate', 'fee', 'amount', 'excise', 'ev', 'industrial'])
    
    if (is_simple_greeting or is_very_short_greeting) and not has_policy_words and len(query.split()) <= 5:
        return f"""You are the Chandigarh Policy Assistant, a friendly government AI assistant specializing in Chandigarh policies and services.

The user said: "{query}"

PROVIDE A WARM GREETING RESPONSE that:
- Welcomes them to the Chandigarh Policy Assistant
- Briefly mentions you can help with government policies, business regulations, industrial policies, permits, and civic services
- Encourages them to ask specific questions about Chandigarh policies
- Uses a warm, conversational tone suitable for government services
- Keeps it brief and friendly (2-3 sentences)

Example: "Hello! Welcome to the Chandigarh Policy Assistant. I'm here to help you with information about government policies, business regulations, permits, and civic services in Chandigarh. Please feel free to ask me any specific questions about policies or services you need assistance with!"

DO NOT provide detailed policy information unless specifically requested."""

    return f"""You are the Chandigarh Policy Assistant, an expert AI system specializing in Chandigarh municipal policies, business regulations, industrial policies, and government schemes.

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

def search_policies(query, history):
    """Main search function with full quality"""
    if not query.strip():
        return "", history + [[query, "Please enter a valid question about Chandigarh policies."]]
    
    start_time = time.time()
    
    try:
        # Perform high-quality search
        results = searcher.fast_search(query, top_k=6)
        
        # Prepare context
        context = ""
        for result in results:
            content = result.get('metadata', {}).get('content', '')
            if content:
                context += f"\n{content}\n"
        
        # Generate response with full prompt optimization
        prompt = create_optimized_prompt(query, context, results)
        
        completion = groq_client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            max_tokens=2000
        )
        
        response = completion.choices[0].message.content
        total_time = time.time() - start_time
        
        # Add performance info
        response += f"\n\n*Response generated in {total_time:.2f}s with {len(results)} relevant policy documents*"
        
        return "", history + [[query, response]]
        
    except Exception as e:
        error_msg = f"Sorry, I encountered an error: {str(e)}. Please try again."
        return "", history + [[query, error_msg]]

# Initialize system
initialize_system()

# Create Gradio interface
with gr.Blocks(title="Chandigarh Policy Assistant", theme=gr.themes.Soft()) as demo:
    gr.Markdown("""
    # 🏛️ Chandigarh Policy Assistant
    
    **Your AI-powered guide to Chandigarh government policies, regulations, and services**
    
    Ask questions about:
    - Industrial policies and incentives
    - EV (Electric Vehicle) policies  
    - IT and business regulations
    - Permits and licensing
    - Municipal services
    - And much more!
    """)
    
    chatbot = gr.Chatbot(height=500, placeholder="Ask me anything about Chandigarh policies...")
    msg = gr.Textbox(
        placeholder="Type your question here (e.g., 'What are the EV incentives in Chandigarh?')",
        container=False,
        scale=7
    )
    
    with gr.Row():
        submit = gr.Button("Ask Question", variant="primary")
        clear = gr.Button("Clear Chat")
    
    gr.Examples(
        examples=[
            "What are the electric vehicle incentives in Chandigarh?",
            "How can I start an IT business in Chandigarh?", 
            "What are the industrial policy benefits?",
            "Tell me about SEZ policies",
            "What permits do I need for construction?"
        ],
        inputs=msg
    )
    
    # Event handlers
    msg.submit(search_policies, [msg, chatbot], [msg, chatbot])
    submit.click(search_policies, [msg, chatbot], [msg, chatbot])
    clear.click(lambda: ([], ""), outputs=[chatbot, msg])

if __name__ == "__main__":
    demo.launch() 