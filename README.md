# Chandigarh Policy Assistant - Hybrid Search System

A production-ready hybrid search system that combines vector search with BM25 for intelligent policy document retrieval and question answering.

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Pinecone API key
- Groq API key

### Installation & Setup

1. **Clone or copy the final folder contents**
2. **Configure environment variables:**
   ```bash
   cp env.sample .env
   # Edit .env with your API keys
   ```

3. **Configure the system:**
   ```bash
   cp config.py.example config.py
   # Edit config.py with your settings
   ```

4. **Start the system:**
   ```bash
   ./start.sh
   ```
   
   Or manually:
   ```bash
   pip install -r requirements.txt
   python run_server.py
   ```

## 📁 Core Files

| File | Description |
|------|-------------|
| `hybrid_search_server.py` | Main Flask server with hybrid search implementation |
| `run_server.py` | Server startup script |
| `config.py` | Configuration settings (create from config.py.example) |
| `hybrid_search_frontend.html` | Web interface for the search system |
| `requirements.txt` | Python dependencies |
| `start.sh` | Automated startup script |
| `.gitignore` | Git ignore rules |

## 📚 Policy Documents

The `txt_files/` directory contains all Chandigarh government policy documents that the system can search through:

| Document | Description |
|----------|-------------|
| `SEZ Policy Chandigarh - 2015.txt` | Special Economic Zone policy |
| `Chandigarh Industrial Policy 2015.txt` | Industrial development guidelines |
| `Chandigarh Electric Vehicle Policy 2022.txt` | EV adoption and incentives |
| `Chandigarh IT Policy 2013.txt` | Information Technology sector policies |
| `Chandigarh ITeS Policy 2003.txt` | IT Enabled Services policies |
| `Chandigarh Parking Policy 2020.txt` | Vehicle parking regulations |
| `Chandigarh Data Sharing & Accessibility Policy.txt` | Government data policies |
| `Excise Policy Chandigarh 2024-25.txt` | Current excise regulations |
| `Chandigarh Policy for managing Construction & Demolition (C&D) waste.txt` | Waste management guidelines |
| `Guidelines - Disposal of Obsolete IT Equipment 2014.txt` | IT equipment disposal procedures |
| `Amendment - Chandigarh Industrial Policy 2019.txt` | Industrial policy updates |
| `Amendments - Chandigarh EV Policy 2022.txt` | EV policy modifications |

**Note**: These documents are preprocessed and indexed in the Pinecone vector database for efficient searching.

## 🔧 Configuration

### Environment Variables (.env)
```bash
PINECONE_API_KEY=your_pinecone_api_key
GROQ_API_KEY=your_groq_api_key
```

### System Configuration (config.py)
- **Embedding Model**: BAAI/bge-large-en-v1.5 (1024 dimensions)
- **Vector Database**: Pinecone
- **LLM Provider**: Groq (llama3-70b-8192)
- **Search Method**: Hybrid (Vector + BM25 with RRF fusion)
- **Fusion Weight**: 50% vector, 50% BM25

## 🌐 Usage

1. **Start the server:**
   ```bash
   python run_server.py
   ```

2. **Access the web interface:**
   - Open `http://localhost:3002` in your browser
   - Or use the API endpoint: `POST /api/search`

3. **API Usage:**
   ```bash
   curl -X POST http://localhost:3002/api/search \
     -H "Content-Type: application/json" \
     -d '{"query": "tell me about ev policy"}'
   ```

## 📊 Performance

- **Search Time**: 4-12 seconds (depending on query complexity)
- **Vector Search**: ~4-6 seconds
- **BM25 Search**: ~6-8 seconds  
- **Document Index**: 309 documents across 12 policy domains
- **Accuracy**: 90%+ for policy-specific queries

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Web Frontend  │───▶│  Flask Server    │───▶│   Pinecone DB   │
│                 │    │                  │    │                 │
└─────────────────┘    │  Hybrid Search   │    └─────────────────┘
                       │  - Vector Search │    
                       │  - BM25 Search   │    ┌─────────────────┐
                       │  - RRF Fusion    │───▶│   Groq LLM      │
                       │                  │    │                 │
                       └──────────────────┘    └─────────────────┘
```

## 🔍 Search Features

- **Hybrid Search**: Combines semantic vector search with keyword-based BM25
- **RRF Fusion**: Reciprocal Rank Fusion for optimal result ranking
- **Context-Aware**: Maintains conversation history for follow-up questions
- **Policy-Specific**: Optimized for Chandigarh government policy documents
- **Real-time**: Fast response times with efficient caching

## 📋 Supported Policy Domains

1. Electric Vehicle Policy
2. SEZ (Special Economic Zone) Policy  
3. Industrial Policy
4. IT/ITES Policy
5. Parking Policy
6. Data Sharing Policy
7. Construction & Demolition Waste Policy
8. Excise Policy
9. Disposal Policy

## 🛠️ Troubleshooting

### Common Issues

1. **Server won't start:**
   - Check if config.py exists and is properly configured
   - Verify API keys in .env file
   - Ensure all dependencies are installed

2. **No search results:**
   - Verify Pinecone index is accessible
   - Check if documents are properly indexed
   - Confirm embedding model is loaded

3. **Slow performance:**
   - Check network connectivity to Pinecone and Groq
   - Monitor system resources (CPU/Memory)
   - Consider reducing batch sizes in config

### Logs
- Server logs are displayed in the console
- Debug information includes timing breakdowns
- Error messages provide specific failure details

## 🔒 Security

- API keys stored in environment variables
- No sensitive data in source code
- CORS configured for web interface
- Input validation on all endpoints

## 📈 Monitoring

The system provides detailed performance metrics:
- Search timing breakdowns
- Result quality scores  
- Cache hit rates
- Error tracking

## 🤝 Support

For issues or questions:
1. Check the troubleshooting section
2. Review server logs for error details
3. Verify configuration settings
4. Test with simple queries first

---

**Note**: This is the production-ready version of the Chandigarh Policy Assistant. All experimental and development files have been moved to the `extra` folder. 