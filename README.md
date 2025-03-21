# Agentic Memory 🧠

A novel agentic memory system for LLM agents that can dynamically organize memories in an agentic way.

## Introduction 🌟

Large Language Model (LLM) agents have demonstrated remarkable capabilities in handling complex real-world tasks through external tool usage. However, to effectively leverage historical experiences, they require sophisticated memory systems. Traditional memory systems, while providing basic storage and retrieval functionality, often lack advanced memory organization capabilities.

Our project introduces an innovative **Agentic Memory** system that revolutionizes how LLM agents manage and utilize their memories:

<div align="center">
  <img src="Figure/intro-a.jpg" alt="Traditional Memory System" width="600"/>
  <img src="Figure/intro-b.jpg" alt="Our Proposed Agentic Memory" width="600"/>
  <br>
  <em>Comparison between traditional memory system (top) and our proposed agentic memory (bottom). Our system enables dynamic memory operations and flexible agent-memory interactions.</em>
</div>

> **Note:** This repository provides a memory system to facilitate agent construction. If you want to reproduce the results presented in our paper, please refer to: [https://github.com/WujiangXu/AgenticMemory](https://github.com/WujiangXu/AgenticMemory)

For more details, please refer to our paper: [A-MEM: Agentic Memory for LLM Agents](https://arxiv.org/pdf/2502.12110)


## Key Features ✨

- 🔄 Dynamic memory organization based on Zettelkasten principles
- 🔍 Intelligent indexing and linking of memories
- 📝 Comprehensive note generation with structured attributes
- 🌐 Interconnected knowledge networks
- 🧬 Continuous memory evolution and refinement
- 🤖 Agent-driven decision making for adaptive memory management

## Framework 🏗️

<div align="center">
  <img src="Figure/framework.jpg" alt="Agentic Memory Framework" width="800"/>
  <br>
  <em>The framework of our Agentic Memory system showing the dynamic interaction between LLM agents and memory components.</em>
</div>

## How It Works 🛠️

When a new memory is added to the system:
1. Generates comprehensive notes with structured attributes
2. Creates contextual descriptions and tags
3. Analyzes historical memories for relevant connections
4. Establishes meaningful links based on similarities
5. Enables dynamic memory evolution and updates

## Results 📊

Empirical experiments conducted on six foundation models demonstrate superior performance compared to existing SOTA baselines.

## Getting Started 🚀

1. Clone the repository:
```bash
git clone https://github.com/agiresearch/A-mem.git
cd A-mem
```

2. Install dependencies:
Option 1: Using venv (Python virtual environment)
```bash
# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt
```

Option 2: Using Conda
```bash
# Create and activate conda environment
conda create -n myenv python=3.9
conda activate myenv

# Install dependencies
pip install -r requirements.txt
```

3. Usage Examples 💡

Here's how to use the Agentic Memory system for basic operations:

```python
from memory_system import AgenticMemorySystem

# Initialize the memory system 🚀
memory_system = AgenticMemorySystem(
    model_name='all-MiniLM-L6-v2',  # Embedding model for semantic search
    llm_backend="openai",           # LLM backend (openai/mock/ollama)
    llm_model="gpt-4"              # LLM model name
)

# Create (Add) Memories ➕
# Simple creation
memory_id = memory_system.create("Deep learning neural networks")

# Creation with metadata
memory_id = memory_system.create(
    content="Machine learning project notes",
    tags=["ml", "project"],
    category="Research",
    timestamp="202503021500"  # YYYYMMDDHHmm format
)

# Read (Retrieve) Memories 📖
# Get memory by ID
memory = memory_system.read(memory_id)
print(f"Content: {memory.content}")
print(f"Tags: {memory.tags}")
print(f"Context: {memory.context}")
print(f"Keywords: {memory.keywords}")

# Search memories
results = memory_system.search("neural networks", k=5)
for result in results:
    print(f"ID: {result['id']}")
    print(f"Content: {result['content']}")
    print(f"Score: {result['score']}")
    print("---")

# Update Memories 🔄
memory_system.update(memory_id, "Updated content about deep learning")

# Delete Memories ❌
memory_system.delete(memory_id)

# Memory Evolution 🧬
# The system automatically evolves memories by:
# 1. Finding semantic relationships
# 2. Updating metadata and context
# 3. Creating connections between related memories
# This happens automatically when creating or updating memories!
```

### Advanced Features 🌟

1. **Hybrid Search** 🔍
   - Combines ChromaDB vector search and embedding-based retrieval
   - Automatically deduplicates and ranks results
   - Returns most relevant memories first

2. **Memory Evolution** 🧬
   - Automatically analyzes content relationships
   - Updates tags and context based on related memories
   - Creates semantic connections between memories

3. **Flexible Metadata** 📋
   - Custom tags and categories
   - Automatic keyword extraction
   - Context generation
   - Timestamp tracking

4. **Multiple LLM Backends** 🤖
   - OpenAI (GPT-4, GPT-3.5)
   - Ollama (for local deployment)

### Best Practices 💪

1. **Memory Creation** ✨:
   - Provide clear, specific content
   - Add relevant tags for better organization
   - Let the system handle context and keyword generation

2. **Memory Retrieval** 🔍:
   - Use specific search queries
   - Adjust 'k' parameter based on needed results
   - Consider both exact and semantic matches

3. **Memory Evolution** 🧬:
   - Allow automatic evolution to organize memories
   - Review generated connections periodically
   - Use consistent tagging conventions

4. **Error Handling** ⚠️:
   - Always check return values
   - Handle potential KeyError for non-existent memories
   - Use try-except blocks for LLM operations

## Citation 📚

If you use this code in your research, please cite our work:

```bibtex
@article{xu2025mem,
  title={A-mem: Agentic memory for llm agents},
  author={Xu, Wujiang and Liang, Zujie and Mei, Kai and Gao, Hang and Tan, Juntao and Zhang, Yongfeng},
  journal={arXiv preprint arXiv:2502.12110},
  year={2025}
}
```

## License 📄

This project is licensed under the MIT License. See LICENSE for details.

## MCP Server (Memory Control Protocol) 🖥️

This repository includes a FastAPI-based MCP server that exposes A-MEM's functionality through a REST API.

### Server Setup 🔧

1. Configure environment variables in the `.env` file:
```bash
# Edit your OpenAI API key in the .env file
OPENAI_API_KEY=your_openai_api_key_here

# Optional: For OpenAI-compatible APIs (like LiteLLM, vLLM, etc.)
OPENAI_API_URL=https://your-custom-api-endpoint.com/v1
```

2. Run the server:
```bash
uvicorn server:app --host 0.0.0.0 --port 8000 --reload
```

3. Access API documentation:
   - Swagger UI: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

### API Endpoints 🔌

- **Create Memory**: `POST /api/v1/memories`
- **Get Memory**: `GET /api/v1/memories/{id}`
- **Update Memory**: `PUT /api/v1/memories/{id}`
- **Delete Memory**: `DELETE /api/v1/memories/{id}`
- **Search Memories**: `GET /api/v1/search?query={query}&k={k}`

### Using OpenAI-Compatible APIs 🔄

The MCP server supports using alternative OpenAI-compatible APIs. This is useful if you want to:
- Use local models through services like LiteLLM or vLLM
- Connect to a self-hosted model server
- Use other commercial API providers with OpenAI-compatible endpoints

To use a custom API endpoint:
1. Set the `OPENAI_API_URL` environment variable in your `.env` file
2. Make sure your API endpoint is compatible with the OpenAI API format
3. Your API must support the chat completions endpoint and JSON response formats

Example configuration for different backends:

**Local server with LiteLLM:**
```
OPENAI_API_URL=http://localhost:8000/v1
```

**Local server with vLLM:**
```
OPENAI_API_URL=http://localhost:8000/v1
```

**NVIDIA AI Playground:**
```
OPENAI_API_URL=https://api.nvcf.nvidia.com/v1
```

### Sample Usage with cURL 🔄

**Create a memory**:
```bash
curl -X POST "http://localhost:8000/api/v1/memories" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Large Language Models require sophisticated memory systems for effective operation.",
    "tags": ["llm", "memory", "ai"],
    "category": "Research"
  }'
```

**Search memories**:
```bash
curl -X GET "http://localhost:8000/api/v1/search?query=language%20models&k=3"
```
