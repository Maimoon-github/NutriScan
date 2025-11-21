#!/usr/bin/env python
"""
Ingest Regulatory Documents into Pinecone
------------------------------------------
Populates the Pinecone vector database with food safety regulations.

Usage:
    python scripts/ingest_regulations.py
"""

import os
import sys
from dotenv import load_dotenv

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nutriscan.settings')
import django
django.setup()

# Load environment variables
load_dotenv()

from analyzer.services.pipeline import VectorDatabase


# Sample regulatory documents for Phase 2
REGULATORY_DOCUMENTS = [
    {
        "doc_id": "WHO-2023-SUGAR",
        "content": "Added sugars should not be introduced before 2 years of age. Early sugar exposure can lead to metabolic disorders, obesity, and preference for sweet tastes. Zero added sugar is recommended for infants under 24 months.",
        "metadata": {
            "source": "WHO Guidelines on Complementary Feeding",
            "region": "Global",
            "url": "https://www.who.int/nutrition/guidelines",
            "year": 2023
        }
    },
    {
        "doc_id": "WHO-2023-SALT",
        "content": "No added salt should be given to infants under 12 months. Excessive sodium intake in early life can lead to hypertension and cardiovascular issues in adulthood.",
        "metadata": {
            "source": "WHO Sodium Recommendations",
            "region": "Global",
            "url": "https://www.who.int/nutrition/sodium",
            "year": 2023
        }
    },
    {
        "doc_id": "PFA-RULES-2018",
        "content": "Vanillin is permitted as flavoring agent, but natural vanilla extract is preferred for infant foods. Artificial flavors should be clearly labeled.",
        "metadata": {
            "source": "Punjab Pure Food Rules",
            "region": "PK-Punjab",
            "url": "https://pfa.gop.pk/",
            "year": 2018
        }
    },
    {
        "doc_id": "PFA-HONEY-BAN",
        "content": "Honey is strictly prohibited for infants under 12 months due to risk of botulism. All honey-containing products must carry warning labels.",
        "metadata": {
            "source": "Punjab Food Authority - Infant Safety Guidelines",
            "region": "PK-Punjab",
            "url": "https://pfa.gop.pk/",
            "year": 2020
        }
    },
    {
        "doc_id": "PSQCA-2021-SODIUM",
        "content": "Sodium content in infant cereals must not exceed 100mg per 100g serving. Products exceeding this limit require additional labeling.",
        "metadata": {
            "source": "PSQCA Standards for Infant Foods",
            "region": "PK-Punjab",
            "url": "https://psqca.com.pk/",
            "year": 2021
        }
    },
    {
        "doc_id": "FDA-2020-ALLERGENS",
        "content": "The top 9 allergens (milk, eggs, fish, shellfish, tree nuts, peanuts, wheat, soybeans, sesame) must be clearly labeled in bold or separate allergen statement.",
        "metadata": {
            "source": "FDA Food Allergen Labeling",
            "region": "US",
            "url": "https://www.fda.gov/food/allergens",
            "year": 2020
        }
    },
    {
        "doc_id": "CODEX-2019-PRESERVATIVES",
        "content": "Sodium benzoate (E211) usage should be minimized in infant foods. Maximum permitted level is 300mg/kg. Not recommended for children under 3 years.",
        "metadata": {
            "source": "Codex Alimentarius - Preservative Standards",
            "region": "Global",
            "url": "http://www.fao.org/fao-who-codexalimentarius",
            "year": 2019
        }
    },
    {
        "doc_id": "WHO-2022-IRON",
        "content": "Iron fortification is essential for infant cereals. Recommended level is 6-12mg per 100g. Iron deficiency can lead to developmental delays.",
        "metadata": {
            "source": "WHO Micronutrient Guidelines",
            "region": "Global",
            "url": "https://www.who.int/nutrition/micronutrients",
            "year": 2022
        }
    },
    {
        "doc_id": "PFA-2021-HALAL",
        "content": "All food products marketed in Pakistan must be Halal certified. Animal-derived ingredients (gelatin, rennet, enzymes) must come from Halal sources.",
        "metadata": {
            "source": "Punjab Food Authority Halal Standards",
            "region": "PK-Punjab",
            "url": "https://pfa.gop.pk/halal-certification",
            "year": 2021
        }
    },
    {
        "doc_id": "EFSA-2018-SWEETENERS",
        "content": "Artificial sweeteners (aspartame, sucralose, saccharin) are not recommended for children under 3 years. Natural sweeteners like stevia are preferred alternatives.",
        "metadata": {
            "source": "EFSA Scientific Opinion on Sweeteners",
            "region": "EU",
            "url": "https://www.efsa.europa.eu/",
            "year": 2018
        }
    },
    {
        "doc_id": "PSQCA-2020-GLUTEN",
        "content": "Gluten-free claims must be verified. Products labeled gluten-free must contain less than 20ppm gluten. Important for celiac disease management.",
        "metadata": {
            "source": "PSQCA Gluten-Free Standards",
            "region": "PK-Punjab",
            "url": "https://psqca.com.pk/",
            "year": 2020
        }
    },
    {
        "doc_id": "WHO-2021-PROTEIN",
        "content": "Protein quality in infant foods should meet amino acid requirements. Milk and soy proteins are high quality. Plant proteins should be combined for completeness.",
        "metadata": {
            "source": "WHO Protein Quality Guidelines",
            "region": "Global",
            "url": "https://www.who.int/nutrition/protein",
            "year": 2021
        }
    }
]


def main():
    print("="*60)
    print("NutriScan - Regulatory Document Ingestion")
    print("="*60)
    
    # Check environment
    api_key = os.getenv("PINECONE_API_KEY")
    if not api_key:
        print("⚠️  PINECONE_API_KEY not found")
        print("   Running in mock mode (documents will not be stored)")
        print("   To use Pinecone, add PINECONE_API_KEY to .env file")
    
    try:
        # Initialize VectorDatabase
        print("\n🚀 Initializing Vector Database...")
        db = VectorDatabase()
        
        if db.use_mock:
            print("⚠️  Running in mock mode (Pinecone not configured)")
            print("   Documents will be displayed but not stored")
        
        # Ingest documents
        print(f"\n📚 Ingesting {len(REGULATORY_DOCUMENTS)} regulatory documents...")
        
        for i, doc in enumerate(REGULATORY_DOCUMENTS, 1):
            print(f"\n[{i}/{len(REGULATORY_DOCUMENTS)}] Processing: {doc['doc_id']}")
            print(f"   Source: {doc['metadata']['source']}")
            print(f"   Region: {doc['metadata']['region']}")
            
            try:
                db.ingest_document(
                    doc_id=doc["doc_id"],
                    content=doc["content"],
                    metadata=doc["metadata"]
                )
                print(f"   ✅ Ingested successfully")
                
            except Exception as e:
                print(f"   ❌ Failed: {e}")
        
        print("\n" + "="*60)
        print("✅ Ingestion Complete!")
        print("="*60)
        
        # Test retrieval
        print("\n🔍 Testing document retrieval...")
        results = db.search_regulations(
            keywords=["Sugar", "Infant", "Added Sugar"],
            region="Global",
            top_k=3
        )
        
        print(f"\n📊 Retrieved {len(results)} documents for test query:")
        for i, result in enumerate(results[:3], 1):
            print(f"\n[{i}] {result['source']}")
            print(f"    Score: {result.get('score', 'N/A')}")
            print(f"    Content: {result['content'][:100]}...")
        
        print("\n✨ Database is ready for production use!")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
