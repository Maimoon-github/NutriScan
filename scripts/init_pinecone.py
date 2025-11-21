#!/usr/bin/env python
"""
Initialize Pinecone Vector Database for NutriScan
--------------------------------------------------
Creates the Pinecone index for storing regulatory documents.

Usage:
    python scripts/init_pinecone.py
"""

import os
import sys
from dotenv import load_dotenv

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment variables
load_dotenv()

try:
    from pinecone import Pinecone, ServerlessSpec
except ImportError:
    print("❌ Pinecone not installed. Install with: pip install pinecone-client")
    sys.exit(1)


def main():
    print("="*60)
    print("NutriScan - Pinecone Index Initialization")
    print("="*60)
    
    # Get API key
    api_key = os.getenv("PINECONE_API_KEY")
    if not api_key:
        print("❌ PINECONE_API_KEY not found in environment")
        print("   Create .env file with: PINECONE_API_KEY=your-key-here")
        sys.exit(1)
    
    try:
        # Initialize Pinecone
        pc = Pinecone(api_key=api_key)
        print("✅ Connected to Pinecone")
        
        # Check existing indexes
        existing_indexes = [idx.name for idx in pc.list_indexes()]
        print(f"📊 Existing indexes: {existing_indexes}")
        
        index_name = "nutriscan-regulations"
        
        if index_name in existing_indexes:
            print(f"⚠️  Index '{index_name}' already exists")
            response = input("   Delete and recreate? (y/N): ")
            
            if response.lower() == 'y':
                print(f"🗑️  Deleting index '{index_name}'...")
                pc.delete_index(index_name)
                print("✅ Index deleted")
            else:
                print("ℹ️  Using existing index")
                sys.exit(0)
        
        # Create new index
        print(f"🚀 Creating index '{index_name}'...")
        pc.create_index(
            name=index_name,
            dimension=384,  # all-MiniLM-L6-v2 embedding dimension
            metric="cosine",
            spec=ServerlessSpec(
                cloud="aws",
                region="us-east-1"
            )
        )
        
        print("✅ Index created successfully!")
        print(f"\n📋 Index Details:")
        print(f"   Name: {index_name}")
        print(f"   Dimension: 384")
        print(f"   Metric: cosine")
        print(f"   Cloud: AWS (us-east-1)")
        
        print("\n✨ Next step: Run 'python scripts/ingest_regulations.py' to populate the index")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
