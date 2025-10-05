# Environment Setup Guide

How to configure your environment for Graphbrain development and LLM integration.

## Table of Contents
- [Environment Variables](#environment-variables)
- [Configuration File (.env)](#configuration-file-env)
- [API Keys Setup](#api-keys-setup)
- [IDE Configuration](#ide-configuration)
- [Docker Setup (Optional)](#docker-setup-optional)

---

## Environment Variables

### Core Graphbrain Variables

```bash
# Optional: Set default backend
export GRAPHBRAIN_BACKEND=sqlite  # or leveldb

# Optional: Set default database location
export GRAPHBRAIN_DB_PATH=/path/to/your/graphs
```

### Python Environment

```bash
# Recommended: Use specific Python version
export PYTHON_VERSION=3.12

# Virtual environment location (optional)
export VENV_PATH=./venv
```

---

## Configuration File (.env)

Create a `.env` file in your project root for sensitive data and API keys.

### Template

Create `.env`:
```bash
# Graphbrain Configuration
GRAPHBRAIN_BACKEND=sqlite
GRAPHBRAIN_DEFAULT_DB=knowledge.db

# LLM API Keys
GOOGLE_API_KEY=your_gemini_api_key_here
OPENAI_API_KEY=your_openai_api_key_here

# Vertex AI Configuration (Google Cloud)
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account-key.json
VERTEX_AI_LOCATION=us-central1

# Vector Store Configuration
CHROMA_PERSIST_DIR=./chroma_db
CHROMA_COLLECTION_NAME=graphbrain_embeddings

# Optional: Embedding Model Configuration
EMBEDDING_PROVIDER=sentence-transformers  # or vertex-ai, openai
EMBEDDING_MODEL=all-MiniLM-L6-v2  # for sentence-transformers

# spaCy Configuration
SPACY_MODEL=en_core_web_lg  # or en_core_web_trf

# Development Settings
DEBUG=true
LOG_LEVEL=INFO
```

### Loading .env in Python

```python
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Access variables
google_api_key = os.getenv('GOOGLE_API_KEY')
project_id = os.getenv('GOOGLE_CLOUD_PROJECT')
```

**Install python-dotenv:**
```bash
pip install python-dotenv
```

---

## API Keys Setup

### Google Gemini API

1. **Get API Key:**
   - Go to https://makersuite.google.com/app/apikey
   - Click "Create API Key"
   - Copy the key

2. **Configure:**
   ```bash
   export GOOGLE_API_KEY="your-api-key"
   # Or add to .env file
   ```

3. **Test:**
   ```python
   import google.generativeai as genai
   import os

   genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))
   model = genai.GenerativeModel('gemini-pro')
   response = model.generate_content('Hello!')
   print(response.text)
   ```

### Google Cloud / Vertex AI

1. **Setup Google Cloud Project:**
   ```bash
   # Install gcloud CLI
   curl https://sdk.cloud.google.com | bash
   exec -l $SHELL

   # Initialize
   gcloud init

   # Create project (if needed)
   gcloud projects create your-project-id

   # Enable APIs
   gcloud services enable aiplatform.googleapis.com
   ```

2. **Create Service Account:**
   ```bash
   gcloud iam service-accounts create graphbrain-sa \
       --display-name="Graphbrain Service Account"

   # Grant permissions
   gcloud projects add-iam-policy-binding your-project-id \
       --member="serviceAccount:graphbrain-sa@your-project-id.iam.gserviceaccount.com" \
       --role="roles/aiplatform.user"

   # Create key
   gcloud iam service-accounts keys create ~/graphbrain-key.json \
       --iam-account=graphbrain-sa@your-project-id.iam.gserviceaccount.com
   ```

3. **Configure Environment:**
   ```bash
   export GOOGLE_APPLICATION_CREDENTIALS="$HOME/graphbrain-key.json"
   export GOOGLE_CLOUD_PROJECT="your-project-id"
   export VERTEX_AI_LOCATION="us-central1"
   ```

4. **Test:**
   ```python
   from vertexai.language_models import TextEmbeddingModel
   from google.cloud import aiplatform

   aiplatform.init(
       project=os.getenv('GOOGLE_CLOUD_PROJECT'),
       location=os.getenv('VERTEX_AI_LOCATION')
   )

   model = TextEmbeddingModel.from_pretrained('text-embedding-004')
   embeddings = model.get_embeddings(['Test text'])
   print(f"Embedding dimension: {len(embeddings[0].values)}")
   ```

### OpenAI API

1. **Get API Key:**
   - Go to https://platform.openai.com/api-keys
   - Create new secret key
   - Copy the key (shown only once)

2. **Configure:**
   ```bash
   export OPENAI_API_KEY="sk-..."
   ```

3. **Test:**
   ```python
   from openai import OpenAI
   import os

   client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

   response = client.embeddings.create(
       input="Test text",
       model="text-embedding-3-small"
   )
   print(f"Embedding dimension: {len(response.data[0].embedding)}")
   ```

---

## IDE Configuration

### Visual Studio Code

Create `.vscode/settings.json`:
```json
{
  "python.defaultInterpreterPath": "${workspaceFolder}/venv/bin/python",
  "python.envFile": "${workspaceFolder}/.env",
  "python.testing.pytestEnabled": true,
  "python.testing.pytestArgs": [
    "graphbrain/tests"
  ],
  "python.linting.enabled": true,
  "python.linting.pylintEnabled": false,
  "python.linting.flake8Enabled": true,
  "python.formatting.provider": "black",
  "editor.formatOnSave": true,
  "files.exclude": {
    "**/__pycache__": true,
    "**/*.pyc": true,
    "**/.pytest_cache": true,
    "**/*.db": true,
    "**/*.hg": true
  }
}
```

Create `.vscode/launch.json` for debugging:
```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Python: Current File",
      "type": "python",
      "request": "launch",
      "program": "${file}",
      "console": "integratedTerminal",
      "envFile": "${workspaceFolder}/.env"
    },
    {
      "name": "Python: LLM Demo",
      "type": "python",
      "request": "launch",
      "program": "${workspaceFolder}/examples/llm_integration_demo.py",
      "console": "integratedTerminal",
      "envFile": "${workspaceFolder}/.env"
    }
  ]
}
```

### PyCharm

1. **Configure Python Interpreter:**
   - File → Settings → Project → Python Interpreter
   - Add interpreter → Existing environment
   - Select `venv/bin/python`

2. **Configure Environment Variables:**
   - Run → Edit Configurations
   - Add environment variables from `.env`

3. **Configure .env Plugin:**
   - Install "EnvFile" plugin
   - In run configuration, enable EnvFile
   - Select your `.env` file

### Jupyter Notebook

```bash
# Install Jupyter
pip install jupyter ipykernel

# Add kernel
python -m ipykernel install --user --name=graphbrain

# Start Jupyter
jupyter notebook
```

In notebook, load environment:
```python
%load_ext dotenv
%dotenv

import os
print(os.getenv('GOOGLE_API_KEY'))  # Should show your key
```

---

## Project Structure

Recommended project structure for Graphbrain projects:

```
my-graphbrain-project/
├── .env                      # API keys and config (DO NOT COMMIT)
├── .env.example              # Template (safe to commit)
├── .gitignore               # Ignore .env, *.db, venv/
├── requirements.txt          # Dependencies
├── venv/                     # Virtual environment
├── data/
│   ├── raw/                 # Raw documents
│   ├── graphs/              # Graph databases (*.db, *.hg)
│   └── embeddings/          # Vector stores
├── src/
│   ├── __init__.py
│   ├── parser.py            # Text parsing logic
│   ├── knowledge_base.py    # Graph operations
│   └── llm_agent.py         # LLM integration
├── notebooks/               # Jupyter notebooks
│   └── exploration.ipynb
├── tests/
│   └── test_knowledge_base.py
└── scripts/
    ├── ingest_documents.py
    └── query_knowledge.py
```

### .gitignore

Add to `.gitignore`:
```
# Environment
.env
venv/
*.pyc
__pycache__/

# Graphbrain databases
*.db
*.hg
*.sqlite
*.sqlite3

# Vector stores
chroma_db/
*.faiss

# API keys and credentials
*.json
*-key.json
credentials/

# IDE
.vscode/
.idea/
*.swp

# OS
.DS_Store
Thumbs.db
```

### .env.example

Create `.env.example` (safe to commit):
```bash
# Copy this file to .env and fill in your values

# Graphbrain Configuration
GRAPHBRAIN_BACKEND=sqlite
GRAPHBRAIN_DEFAULT_DB=knowledge.db

# LLM API Keys
GOOGLE_API_KEY=your_gemini_api_key_here
OPENAI_API_KEY=your_openai_api_key_here

# Vertex AI (Google Cloud)
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account-key.json
VERTEX_AI_LOCATION=us-central1

# Vector Store
CHROMA_PERSIST_DIR=./chroma_db
EMBEDDING_PROVIDER=sentence-transformers
```

---

## Docker Setup (Optional)

For reproducible environments and deployment.

### Dockerfile

Create `Dockerfile`:
```dockerfile
FROM python:3.12-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Install Graphbrain
RUN pip install -e .

# Download spaCy model
RUN python -m spacy download en_core_web_lg

# Expose port (if running API)
EXPOSE 8000

# Default command
CMD ["python", "-m", "jupyter", "notebook", "--ip=0.0.0.0", "--allow-root"]
```

### docker-compose.yml

```yaml
version: '3.8'

services:
  graphbrain:
    build: .
    volumes:
      - ./data:/app/data
      - ./.env:/app/.env
    environment:
      - PYTHONUNBUFFERED=1
    ports:
      - "8888:8888"  # Jupyter
      - "8000:8000"  # API (if applicable)
    command: python examples/llm_integration_demo.py

  chroma:
    image: chromadb/chroma:latest
    volumes:
      - ./chroma_data:/chroma/chroma
    environment:
      - IS_PERSISTENT=TRUE
    ports:
      - "8001:8000"
```

### Usage

```bash
# Build
docker-compose build

# Run
docker-compose up

# Run specific service
docker-compose run graphbrain python examples/llm_integration_demo.py

# Shell access
docker-compose run graphbrain bash
```

---

## Best Practices

### 1. Separate Environments

```bash
# Development
python -m venv venv-dev
source venv-dev/bin/activate
pip install -e .[dev]

# Production
python -m venv venv-prod
source venv-prod/bin/activate
pip install -e .
```

### 2. Version Pinning

Create `requirements.txt`:
```txt
# Core
graphbrain @ git+https://github.com/your-username/graphbrain.git@main

# LLM Integration
sentence-transformers==2.2.2
chromadb==0.4.15
google-generativeai==0.3.1
openai==1.3.5

# Optional: Vertex AI
google-cloud-aiplatform==1.36.0

# Development
pytest==7.4.3
black==23.11.0
ruff==0.1.6
```

Install:
```bash
pip install -r requirements.txt
```

### 3. Secrets Management

**Never commit:**
- API keys
- Service account credentials
- Database files
- `.env` file

**Do commit:**
- `.env.example` (template)
- `requirements.txt`
- Documentation

### 4. Environment Switching

Create shell aliases in `~/.bashrc` or `~/.zshrc`:
```bash
# Graphbrain aliases
alias gb-dev='source ~/projects/graphbrain/venv-dev/bin/activate'
alias gb-prod='source ~/projects/graphbrain/venv-prod/bin/activate'
alias gb-test='python test_installation.py'
```

---

## Troubleshooting

### Issue: Environment variables not loading

```python
# Debug .env loading
from dotenv import load_dotenv
import os

load_dotenv(verbose=True)  # Shows which .env file is loaded
print(os.getenv('GOOGLE_API_KEY'))
```

### Issue: API key not recognized

```bash
# Check if set
echo $GOOGLE_API_KEY

# Export in current shell
export GOOGLE_API_KEY="your-key"

# Add to shell profile for persistence
echo 'export GOOGLE_API_KEY="your-key"' >> ~/.bashrc
source ~/.bashrc
```

### Issue: Permission denied for credentials file

```bash
# Fix file permissions
chmod 600 ~/graphbrain-key.json

# Verify
ls -la ~/graphbrain-key.json
# Should show: -rw------- (only you can read/write)
```

---

## Next Steps

- [Installation Guide](installation.md) - If you haven't installed yet
- [Features Overview](features.md) - Learn about capabilities
- [Tutorials](tutorials/) - Hands-on examples

## Additional Resources

- [Python dotenv documentation](https://pypi.org/project/python-dotenv/)
- [Google Cloud setup guide](https://cloud.google.com/docs/authentication/getting-started)
- [OpenAI API documentation](https://platform.openai.com/docs)
