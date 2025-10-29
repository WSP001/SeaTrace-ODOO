# 🤖 Code Embeddings & Semantic Search Setup

This directory contains the workflow and scripts for generating semantic embeddings of the codebase using OpenAI's API. These embeddings enable AI-powered semantic code search for IDE assistants and agents.

## 📁 Files

- **`update-embeddings.yml`** - GitHub Actions workflow (runs after PR merge to `main`)
- **`../scripts/create_embeddings.py`** - Python script to generate embeddings
- **`embedding-requirements.txt`** - Python dependencies (OpenAI, Pinecone, Weaviate, etc.)

## 🚀 Usage

### **Local Development (One-time setup)**

```bash
# Install dependencies
pip install -r .github/embedding-requirements.txt

# Set OpenAI API key
export OPENAI_API_KEY="sk-..."

# Generate embeddings locally
python .github/scripts/create_embeddings.py \
  --root . \
  --index-name seatrace-index \
  --vector-db local \
  --output-dir .github/embeddings

# Output: .github/embeddings/seatrace-index.jsonl
```

### **CI/CD (Automatic)**

The `update-embeddings.yml` workflow runs automatically:
- **Trigger:** After merge to `main` branch
- **Paths:** Changes to `src/**`, `docs/**`, `README.md`
- **Output:** Embeddings uploaded to Pinecone/Weaviate OR saved as artifact

### **Manual Trigger**

```bash
# Trigger workflow manually via GitHub Actions UI or CLI
gh workflow run update-embeddings.yml -f vector_db=local
```

## 🔧 Configuration

### **Required Secrets (GitHub Repository Settings → Secrets)**

| Secret | Description | Required For |
|--------|-------------|--------------|
| `OPENAI_API_KEY` | OpenAI API key for embeddings generation | All vector DBs |
| `PINECONE_API_KEY` | Pinecone API key | Pinecone only |
| `PINECONE_ENVIRONMENT` | Pinecone environment (e.g., `us-west1-gcp`) | Pinecone only |
| `WEAVIATE_URL` | Weaviate instance URL | Weaviate only |
| `WEAVIATE_API_KEY` | Weaviate API key (optional) | Weaviate only |

### **Vector Database Options**

1. **`local`** (default) - Saves embeddings to `.github/embeddings/seatrace-index.jsonl`
   - No external service required
   - Good for testing and IDE integrations
   - GitHub Actions artifact (90-day retention)

2. **`pinecone`** - Uploads to Pinecone vector database
   - Requires `PINECONE_API_KEY` and `PINECONE_ENVIRONMENT`
   - Managed service, automatic scaling
   - Best for production semantic search

3. **`weaviate`** - Uploads to Weaviate vector database
   - Requires `WEAVIATE_URL` (and optionally `WEAVIATE_API_KEY`)
   - Self-hosted or cloud
   - Good for complex querying and GraphQL

## 📊 What Gets Indexed

**File Types:**
- Python: `*.py`
- Markdown: `*.md`
- TypeScript/JavaScript: `*.ts`, `*.tsx`, `*.js`, `*.jsx`
- Configuration: `*.json`, `*.yml`, `*.yaml`
- Scripts: `*.sh`, `*.ps1`

**Excluded Directories:**
- `.git`, `node_modules`, `__pycache__`, `.venv`, `venv`
- `.pytest_cache`, `.mypy_cache`, `dist`, `build`, `.next`

**Chunking:**
- Max tokens per chunk: 1000
- Overlap: 100 tokens
- Model: `text-embedding-3-small` (1536 dimensions)

## 🔍 Using Embeddings for Semantic Search

Once generated, embeddings can be used for:

1. **IDE Assistant Context** - Load `.ai/assistant_context.json` which references embedding index
2. **Semantic Code Search** - Find similar code patterns: "Find all fish ticket indexing implementations"
3. **Documentation Discovery** - Search docs by intent: "How does DockSide reconcile incoming/outgoing forks?"
4. **Agent Navigation** - Help agents discover relevant code without exact file paths

### **Example Query (Pinecone)**

```python
import pinecone
import openai

# Initialize
pinecone.init(api_key="...", environment="...")
index = pinecone.Index("seatrace-index")

# Generate query embedding
query = "How does DockSide calculate fish recovery percentages for H&G and fillet processing?"
query_embedding = openai.embeddings.create(
    model="text-embedding-3-small",
    input=query
).data[0].embedding

# Search
results = index.query(vector=query_embedding, top_k=5, include_metadata=True)

for match in results['matches']:
    print(f"File: {match['metadata']['file_path']}")
    print(f"Score: {match['score']}")
    print(f"Content: {match['metadata']['content'][:200]}...")
```

## 🧪 Testing

```bash
# Dry run (local mode, no uploads)
python .github/scripts/create_embeddings.py \
  --root tests/fixtures \
  --index-name test-index \
  --vector-db local

# Verify output
cat .github/embeddings/test-index.jsonl | jq '.[0]'
```

## 📚 Integration with `.ai/assistant_context.json`

The `.ai/assistant_context.json` file at repo root tells IDE assistants:
- Where to find embeddings (`seatrace-index`)
- Important files to prioritize
- Command shortcuts
- DockSide processing context (H&G recovery %, fish ticket indexing)

**Supported IDEs:**
- GitHub Copilot Workspace
- Cursor AI
- Continue.dev
- Cody (Sourcegraph)

## 🎯 PROCEEDING Team Context

Embeddings will index critical PROCEEDING team discoveries:
- `docs/PROCEEDING_TEAM_DISCOVERIES.md` - PK1/PK2/PK3 architecture validation (27KB)
- `docs/WORKSPACE_DIRECTORY_MAP.md` - 20+ workspaces (7-year history)
- `docs/VALIDATION_REPORT.md` - Comprehensive business model validation (1000+ lines)

Agents can semantically search for:
- "What is PK2 Facility Keys and how does it relate to DockSide?"
- "Show me the packet switching handler implementation"
- "How does Roberto's 3-pillar monetization strategy map to PROCEEDING team's design?"

## 🔐 Security

**DO NOT COMMIT:**
- ✅ OpenAI API keys (use GitHub Secrets)
- ✅ Vector DB credentials (use GitHub Secrets)
- ✅ Generated embeddings with sensitive data (use `.gitignore`)

**Safe to commit:**
- ✅ `create_embeddings.py` script
- ✅ `update-embeddings.yml` workflow
- ✅ `embedding-requirements.txt`
- ✅ This README

**Gitleaks pre-commit hook** will catch any accidental secret commits.

## 📈 Monitoring

**GitHub Actions:**
- Check workflow runs: `.github/workflows/update-embeddings.yml`
- Download artifacts: Actions tab → `update-embeddings` → Artifacts

**Vector DB Status:**
- Pinecone: Check index stats in dashboard
- Weaviate: Query `GET /v1/schema` for `CodeDocument` class

## 🛠️ Troubleshooting

**Problem:** `ImportError: No module named 'openai'`
**Solution:** `pip install -r .github/embedding-requirements.txt`

**Problem:** `openai.error.AuthenticationError: Incorrect API key`
**Solution:** Set `OPENAI_API_KEY` environment variable or GitHub Secret

**Problem:** `Pinecone index does not exist`
**Solution:** Script auto-creates index on first run (1536 dimensions, cosine metric)

**Problem:** Embeddings too large (file size > 100MB)
**Solution:** Use Pinecone/Weaviate instead of local mode, or increase chunking

---

**Last Updated:** 2025-10-28  
**Maintainer:** Roberto002 (@WSP001)  
**Related:** `.ai/assistant_context.json`, `docs/PROCEEDING_TEAM_DISCOVERIES.md`
