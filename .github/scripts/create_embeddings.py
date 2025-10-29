#!/usr/bin/env python3
"""
SeaTrace Code Embeddings Generator
Generates semantic embeddings for code files to enable AI-powered semantic search.

Usage:
    python create_embeddings.py --root . --index-name seatrace-index --vector-db local

Dependencies:
    pip install openai tqdm tiktoken pinecone-client weaviate-client
"""

import argparse
import hashlib
import json
import os
import sys
from pathlib import Path
from typing import List, Dict, Optional

try:
    import openai
    from tqdm import tqdm
    import tiktoken
except ImportError as e:
    print(f"Error: Missing required dependency: {e}")
    print("Install with: pip install -r .github/embedding-requirements.txt")
    sys.exit(1)


class CodeEmbeddingsGenerator:
    """Generates semantic embeddings for code files."""

    def __init__(self, root_dir: str, index_name: str, vector_db: str, output_dir: str):
        self.root_dir = Path(root_dir).resolve()
        self.index_name = index_name
        self.vector_db = vector_db
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # OpenAI setup
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        if not self.openai_api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set")
        
        openai.api_key = self.openai_api_key
        self.embedding_model = "text-embedding-3-small"  # 1536 dimensions, cost-effective
        self.tokenizer = tiktoken.get_encoding("cl100k_base")

        # File patterns to index
        self.file_patterns = [
            "*.py", "*.md", "*.ts", "*.tsx", "*.js", "*.jsx",
            "*.json", "*.yml", "*.yaml", "*.sh", "*.ps1"
        ]

        # Directories to exclude
        self.exclude_dirs = {
            ".git", "node_modules", "__pycache__", ".venv", "venv",
            ".pytest_cache", ".mypy_cache", "dist", "build", ".next"
        }

    def get_files_to_index(self) -> List[Path]:
        """Recursively find all files matching patterns."""
        files = []
        for pattern in self.file_patterns:
            for file_path in self.root_dir.rglob(pattern):
                # Skip excluded directories
                if any(excl in file_path.parts for excl in self.exclude_dirs):
                    continue
                if file_path.is_file():
                    files.append(file_path)
        return sorted(files)

    def count_tokens(self, text: str) -> int:
        """Count tokens using tiktoken."""
        return len(self.tokenizer.encode(text))

    def chunk_text(self, text: str, max_tokens: int = 1000, overlap: int = 100) -> List[str]:
        """Split text into chunks with overlap."""
        tokens = self.tokenizer.encode(text)
        chunks = []
        
        for i in range(0, len(tokens), max_tokens - overlap):
            chunk_tokens = tokens[i:i + max_tokens]
            chunk_text = self.tokenizer.decode(chunk_tokens)
            chunks.append(chunk_text)
        
        return chunks

    def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding using OpenAI API."""
        try:
            response = openai.embeddings.create(
                model=self.embedding_model,
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            print(f"Error generating embedding: {e}")
            return []

    def create_document_id(self, file_path: Path, chunk_idx: int = 0) -> str:
        """Create unique document ID."""
        relative_path = file_path.relative_to(self.root_dir)
        content = f"{relative_path}:chunk{chunk_idx}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]

    def process_file(self, file_path: Path) -> List[Dict]:
        """Process a single file and generate embeddings for its chunks."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except (UnicodeDecodeError, PermissionError):
            return []

        relative_path = file_path.relative_to(self.root_dir)
        
        # Add metadata header
        metadata = f"# File: {relative_path}\n# Type: {file_path.suffix}\n\n"
        full_content = metadata + content

        # Chunk the content
        chunks = self.chunk_text(full_content, max_tokens=1000, overlap=100)

        documents = []
        for idx, chunk in enumerate(chunks):
            doc_id = self.create_document_id(file_path, idx)
            embedding = self.generate_embedding(chunk)
            
            if not embedding:
                continue

            doc = {
                "id": doc_id,
                "file_path": str(relative_path),
                "chunk_index": idx,
                "total_chunks": len(chunks),
                "content": chunk,
                "embedding": embedding,
                "metadata": {
                    "file_type": file_path.suffix,
                    "file_name": file_path.name,
                    "token_count": self.count_tokens(chunk)
                }
            }
            documents.append(doc)

        return documents

    def save_local(self, documents: List[Dict]):
        """Save embeddings to local JSONL file."""
        output_file = self.output_dir / f"{self.index_name}.jsonl"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            for doc in documents:
                f.write(json.dumps(doc) + '\n')
        
        print(f"✅ Saved {len(documents)} embeddings to {output_file}")

    def upload_to_pinecone(self, documents: List[Dict]):
        """Upload embeddings to Pinecone."""
        try:
            import pinecone
        except ImportError:
            print("Error: pinecone-client not installed")
            return

        api_key = os.getenv("PINECONE_API_KEY")
        environment = os.getenv("PINECONE_ENVIRONMENT")

        if not api_key or not environment:
            print("Error: PINECONE_API_KEY or PINECONE_ENVIRONMENT not set")
            return

        pinecone.init(api_key=api_key, environment=environment)

        # Create index if it doesn't exist
        if self.index_name not in pinecone.list_indexes():
            pinecone.create_index(
                name=self.index_name,
                dimension=1536,  # text-embedding-3-small dimension
                metric="cosine"
            )

        index = pinecone.Index(self.index_name)

        # Upload in batches
        batch_size = 100
        for i in tqdm(range(0, len(documents), batch_size), desc="Uploading to Pinecone"):
            batch = documents[i:i + batch_size]
            vectors = [
                (doc["id"], doc["embedding"], {
                    "file_path": doc["file_path"],
                    "chunk_index": doc["chunk_index"],
                    "content": doc["content"][:1000]  # Metadata size limit
                })
                for doc in batch
            ]
            index.upsert(vectors=vectors)

        print(f"✅ Uploaded {len(documents)} embeddings to Pinecone")

    def upload_to_weaviate(self, documents: List[Dict]):
        """Upload embeddings to Weaviate."""
        try:
            import weaviate
        except ImportError:
            print("Error: weaviate-client not installed")
            return

        url = os.getenv("WEAVIATE_URL")
        api_key = os.getenv("WEAVIATE_API_KEY")

        if not url:
            print("Error: WEAVIATE_URL not set")
            return

        auth_config = weaviate.auth.AuthApiKey(api_key=api_key) if api_key else None
        client = weaviate.Client(url=url, auth_client_secret=auth_config)

        # Create schema if it doesn't exist
        schema = {
            "class": "CodeDocument",
            "vectorizer": "none",  # We provide embeddings
            "properties": [
                {"name": "file_path", "dataType": ["text"]},
                {"name": "chunk_index", "dataType": ["int"]},
                {"name": "content", "dataType": ["text"]},
                {"name": "file_type", "dataType": ["text"]}
            ]
        }

        try:
            client.schema.create_class(schema)
        except Exception:
            pass  # Class may already exist

        # Upload documents
        with client.batch(batch_size=100) as batch:
            for doc in tqdm(documents, desc="Uploading to Weaviate"):
                batch.add_data_object(
                    data_object={
                        "file_path": doc["file_path"],
                        "chunk_index": doc["chunk_index"],
                        "content": doc["content"],
                        "file_type": doc["metadata"]["file_type"]
                    },
                    class_name="CodeDocument",
                    vector=doc["embedding"]
                )

        print(f"✅ Uploaded {len(documents)} embeddings to Weaviate")

    def run(self):
        """Main execution."""
        print(f"🔍 Finding files to index in {self.root_dir}...")
        files = self.get_files_to_index()
        print(f"Found {len(files)} files")

        print("📝 Processing files and generating embeddings...")
        all_documents = []
        for file_path in tqdm(files, desc="Processing files"):
            documents = self.process_file(file_path)
            all_documents.extend(documents)

        print(f"✅ Generated {len(all_documents)} embeddings from {len(files)} files")

        # Save/upload based on vector DB choice
        if self.vector_db == "local":
            self.save_local(all_documents)
        elif self.vector_db == "pinecone":
            self.upload_to_pinecone(all_documents)
        elif self.vector_db == "weaviate":
            self.upload_to_weaviate(all_documents)
        else:
            print(f"Error: Unknown vector DB: {self.vector_db}")
            sys.exit(1)

        print("✅ Done!")


def main():
    parser = argparse.ArgumentParser(description="Generate code embeddings for semantic search")
    parser.add_argument("--root", required=True, help="Root directory to index")
    parser.add_argument("--index-name", required=True, help="Name of the index/collection")
    parser.add_argument("--vector-db", choices=["local", "pinecone", "weaviate"],
                        default="local", help="Vector database to use")
    parser.add_argument("--output-dir", default=".github/embeddings",
                        help="Output directory for local embeddings")

    args = parser.parse_args()

    generator = CodeEmbeddingsGenerator(
        root_dir=args.root,
        index_name=args.index_name,
        vector_db=args.vector_db,
        output_dir=args.output_dir
    )

    generator.run()


if __name__ == "__main__":
    main()
