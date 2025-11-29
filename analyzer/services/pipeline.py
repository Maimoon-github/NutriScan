"""
NutriScan Analysis Pipeline - Phase 2 Production Implementation
----------------------------------------------------------------
This module orchestrates the complete food label analysis workflow:
1. OCR Text Extraction (PaddleOCR)
2. Ingredient Parsing & Normalization
3. Regulatory Retrieval (RAG with Pinecone)
4. Health Impact Analysis (Agentic LLM with Ollama + LangChain)
5. Response Generation

Phase 2: Production-ready with real AI integrations.
"""

import os
import uuid
import logging
from datetime import datetime
from typing import Dict, List, Optional
import time
from abc import ABC, abstractmethod
import json

# Disable tokenizers parallelism warning and optional transformers dependency
os.environ["TOKENIZERS_PARALLELISM"] = "false"
os.environ["TRANSFORMERS_OFFLINE"] = "1"

# Import production OCR service
from .ocr import OCRService

# LangChain imports for LLM orchestration - defer to avoid heavy imports at module load
Ollama = None
PromptTemplate = None
LLMChain = None

def _import_langchain():
    """Lazy import of LangChain to avoid loading heavy dependencies at module load time."""
    global Ollama, PromptTemplate, LLMChain
    if Ollama is not None:
        return True
    try:
        from langchain_community.llms import Ollama as _Ollama
        from langchain.prompts import PromptTemplate as _PromptTemplate
        from langchain.chains import LLMChain as _LLMChain
        Ollama = _Ollama
        PromptTemplate = _PromptTemplate
        LLMChain = _LLMChain
        return True
    except Exception as e:
        logging.warning(f"LangChain not available: {e}. Using mock mode.")
        return False

# OpenAI imports - defer to avoid heavy imports
openai = None

def _import_openai():
    """Lazy import of OpenAI to avoid loading heavy dependencies at module load time."""
    global openai
    if openai is not None:
        return True
    try:
        import openai as _openai
        openai = _openai
        return True
    except Exception as e:
        logging.warning(f"OpenAI not available: {e}. Using mock mode.")
        return False

# Pinecone for vector database
try:
    from pinecone import Pinecone, ServerlessSpec
    import pinecone
except ImportError:
    Pinecone = None
    logging.warning("Pinecone not installed. Install with: pip install pinecone-client")

# Sentence transformers for embeddings
try:
    from sentence_transformers import SentenceTransformer
except ImportError:
    SentenceTransformer = None
    logging.warning("Sentence transformers not installed. Install with: pip install sentence-transformers")


logger = logging.getLogger(__name__)


class RAGServiceInterface(ABC):
    """Abstract interface for RAG services."""
    
    @abstractmethod
    def search_regulations(self, keywords: List[str], region: str, top_k: int = 5) -> List[Dict]:
        """Search for relevant regulations."""
        pass
    
    @abstractmethod
    def ingest_document(self, doc_id: str, content: str, metadata: Dict):
        """Ingest a document into the knowledge base."""
        pass


class MockRAGService(RAGServiceInterface):
    """
    Mock RAG service that returns hardcoded regulatory context for demo purposes.
    Use this when ENABLE_RAG=False or Pinecone is not available.
    """
    
    def __init__(self):
        logger.info("MockRAGService initialized - using hardcoded regulatory context")
        self.mock_regulations = {
            "sugar": [
                {
                    "source": "WHO Guidelines on Complementary Feeding",
                    "content": "Added sugars should not be introduced before 2 years of age to prevent obesity and dental caries.",
                    "id": "WHO-2023-SUGAR",
                    "url": "https://www.who.int/nutrition/guidelines",
                    "score": 0.95
                },
                {
                    "source": "American Academy of Pediatrics",
                    "content": "Infants under 12 months should not consume foods with added sugars.",
                    "id": "AAP-2017-SUGAR",
                    "url": "https://pediatrics.aappublications.org",
                    "score": 0.93
                }
            ],
            "sodium": [
                {
                    "source": "PSQCA Standards for Infant Foods",
                    "content": "Sodium content must not exceed 100mg per serving for infant cereals.",
                    "id": "PSQCA-2021-SODIUM",
                    "url": "https://psqca.com.pk/",
                    "score": 0.89
                },
                {
                    "source": "WHO Salt Reduction Guidelines",
                    "content": "Children under 2 years should consume less than 2g salt per day.",
                    "id": "WHO-2012-SALT",
                    "url": "https://www.who.int/dietphysicalactivity/reducingsalt",
                    "score": 0.87
                }
            ],
            "additives": [
                {
                    "source": "Punjab Pure Food Rules",
                    "content": "Artificial colors and flavors are restricted in infant food products.",
                    "id": "PFA-RULES-2018",
                    "url": "https://pfa.gop.pk/",
                    "score": 0.92
                },
                {
                    "source": "EU Food Additives Regulation",
                    "content": "E-number additives must be declared and limited in baby foods.",
                    "id": "EU-1333-2008",
                    "url": "https://eur-lex.europa.eu",
                    "score": 0.88
                }
            ],
            "allergens": [
                {
                    "source": "FDA Food Allergen Labeling Act",
                    "content": "Must declare presence of milk, eggs, fish, shellfish, tree nuts, peanuts, wheat, and soybeans.",
                    "id": "FDA-FALCPA-2004",
                    "url": "https://www.fda.gov/food/food-allergensgluten-free",
                    "score": 0.96
                },
                {
                    "source": "Pakistan Food Safety Standards",
                    "content": "Allergen cross-contamination must be prevented in food processing facilities.",
                    "id": "PFSA-2015-ALLERGEN",
                    "url": "https://mocc.gov.pk/",
                    "score": 0.84
                }
            ]
        }
    
    def search_regulations(self, keywords: List[str], region: str, top_k: int = 5) -> List[Dict]:
        """Return mock regulations based on keywords."""
        results = []
        
        # Keyword matching logic
        keywords_lower = [k.lower() for k in keywords]
        
        for category, regulations in self.mock_regulations.items():
            if any(keyword in category or category in keyword for keyword in keywords_lower):
                results.extend(regulations)
        
        # If no specific matches, return general food safety guidelines
        if not results:
            results = [
                {
                    "source": "General Food Safety Guidelines",
                    "content": "All food products must meet safety standards for intended consumer demographic.",
                    "id": "GENERAL-SAFETY-2023",
                    "url": "https://www.who.int/food-safety",
                    "score": 0.70
                }
            ]
        
        # Sort by score and limit results
        results = sorted(results, key=lambda x: x.get("score", 0), reverse=True)[:top_k]
        
        logger.info(f"MockRAGService returned {len(results)} regulations for keywords: {keywords}")
        return results
    
    def ingest_document(self, doc_id: str, content: str, metadata: Dict):
        """Mock document ingestion - logs the action but doesn't store."""
        logger.info(f"MockRAGService: Simulated ingestion of document {doc_id}")


class LLMProviderInterface(ABC):
    """Abstract interface for LLM providers."""
    
    @abstractmethod
    def generate_analysis(self, ocr_text: str, user_profile: Dict, regulations: List[Dict]) -> Dict:
        """Generate health analysis."""
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if the provider is available and properly configured."""
        pass


class MockLLMProvider(LLMProviderInterface):
    """
    Mock LLM provider that returns static analysis matching api_contract.json.
    Use this as the default fallback when no LLM is available.
    """
    
    def __init__(self):
        logger.info("MockLLMProvider initialized - using rule-based analysis")
    
    def is_available(self) -> bool:
        return True
    
    def generate_analysis(self, ocr_text: str, user_profile: Dict, regulations: List[Dict]) -> Dict:
        """Generate mock analysis using simple rules."""
        is_infant = user_profile.get("age_months", 24) < 12
        contains_sugar = any(term in ocr_text.lower() for term in ["sugar", "syrup", "sweetener"])
        contains_salt = any(term in ocr_text.lower() for term in ["salt", "sodium"])
        contains_additives = any(term in ocr_text.lower() for term in ["e1", "e2", "e3", "artificial", "preservative"])
        
        # Simple rule-based verdict
        risk_factors = 0
        if is_infant and contains_sugar:
            risk_factors += 3
        elif contains_sugar:
            risk_factors += 1
        if contains_salt:
            risk_factors += 1
        if contains_additives:
            risk_factors += 1
        
        if risk_factors >= 3:
            verdict = "poor"
        elif risk_factors >= 2:
            verdict = "fair"
        elif risk_factors >= 1:
            verdict = "good"
        else:
            verdict = "excellent"
        
        # Generate summary based on analysis
        if is_infant and contains_sugar:
            summary = "Not recommended for your infant due to added sugar."
            detail = "This product contains added sugar, which WHO guidelines recommend avoiding for infants under 2 years to prevent metabolic issues and dental problems."
        elif contains_sugar and contains_additives:
            summary = "Product contains sugar and additives requiring caution."
            detail = "While not immediately harmful, the combination of added sugars and artificial additives may not align with optimal nutrition guidelines."
        else:
            summary = "Product appears suitable with standard dietary considerations."
            detail = "Based on visible ingredients, this product meets basic safety standards. Always check for personal allergens and dietary restrictions."
        
        # Detect allergens from text
        allergens = []
        allergen_map = {
            "wheat": "Wheat (Gluten)",
            "milk": "Milk",
            "soy": "Soy",
            "egg": "Eggs",
            "peanut": "Peanuts",
            "tree nut": "Tree Nuts",
            "fish": "Fish",
            "shellfish": "Shellfish"
        }
        
        for allergen_key, allergen_name in allergen_map.items():
            if allergen_key in ocr_text.lower():
                allergens.append({
                    "substance": allergen_name,
                    "severity": "high",
                    "evidence": f"Contains {allergen_key.title()}"
                })
        
        return {
            "verdict": verdict,
            "summary": summary,
            "detail": detail,
            "allergens": allergens,
            "dietary_flags": {
                "is_halal": None,  # Cannot determine from OCR alone
                "is_vegan": not any(term in ocr_text.lower() for term in ["milk", "egg", "honey", "gelatin"]),
                "is_infant_safe": not (is_infant and (contains_sugar or contains_salt))
            },
            "flags": [
                flag for flag in [
                    "Contains Added Sugar" if contains_sugar else None,
                    "Contains Sodium" if contains_salt else None,
                    "Contains Additives" if contains_additives else None,
                    "Not Infant Safe" if is_infant and (contains_sugar or contains_salt) else None
                ] if flag is not None
            ]
        }


class OllamaLLMProvider(LLMProviderInterface):
    """
    Ollama LLM provider for local AI inference.
    Connects to http://localhost:11434 by default.
    """
    
    def __init__(self, model_name: str = "qwen2.5:7b-instruct-q4_K_M", base_url: str = "http://localhost:11434"):
        self.model_name = model_name
        self.base_url = base_url
        self.llm = None
        self.prompt_template = None
        
        if _import_langchain() and Ollama is not None and PromptTemplate is not None:
            try:
                self.llm = Ollama(
                    model=model_name,
                    base_url=base_url,
                    temperature=0.3,
                    timeout=60
                )
                
                # Test connection
                test_response = self.llm.invoke("Hello")
                logger.info(f"OllamaLLMProvider initialized: {model_name}")
                
                # Setup prompt template
                self.prompt_template = PromptTemplate(
                    input_variables=["ocr_text", "user_age_months", "dietary_restrictions", "regulations"],
                    template="""You are a food safety expert analyzing a product label for health impact.

PRODUCT LABEL TEXT:
{ocr_text}

USER CONTEXT:
- Age: {user_age_months} months old
- Dietary Restrictions: {dietary_restrictions}

RELEVANT REGULATIONS:
{regulations}

TASK: Analyze this product and provide a structured health assessment.

OUTPUT FORMAT (JSON):
{{
    "verdict": "excellent|good|fair|poor|hazardous",
    "short_summary": "One sentence summary (max 150 chars)",
    "detailed_analysis": "Detailed explanation with regulatory citations",
    "allergens": [
        {{"substance": "name", "severity": "high|medium|low", "evidence": "where found in label"}}
    ],
    "is_halal": true|false|null,
    "is_vegan": true|false,
    "is_infant_safe": true|false,
    "dietary_flags": ["flag1", "flag2"]
}}

CRITICAL RULES:
1. For infants (<12 months), flag ANY added sugar, salt, or honey as hazardous
2. Cite specific regulations in detailed_analysis
3. Identify ALL allergens (milk, wheat, soy, nuts, eggs, fish, shellfish)
4. Check for artificial additives and provide E-codes where applicable

Respond ONLY with valid JSON, no additional text."""
                )
                
            except Exception as e:
                logger.error(f"Failed to initialize Ollama: {e}")
                self.llm = None
        else:
            logger.warning("LangChain or Ollama not available")
    
    def is_available(self) -> bool:
        return self.llm is not None
    
    def generate_analysis(self, ocr_text: str, user_profile: Dict, regulations: List[Dict]) -> Dict:
        """Generate analysis using Ollama."""
        if not self.is_available():
            raise Exception("Ollama LLM not available")
        
        try:
            # Prepare inputs
            user_age_months = user_profile.get("age_months", 24)
            dietary_restrictions = ", ".join(user_profile.get("dietary_restrictions", []))
            
            # Format regulations for prompt
            reg_text = "\n".join([
                f"- {reg['source']}: {reg['content']} (ID: {reg['id']})"
                for reg in regulations[:3]  # Top 3 most relevant
            ])
            
            # Create chain and run
            from langchain.chains import LLMChain
            chain = LLMChain(llm=self.llm, prompt=self.prompt_template)
            
            response = chain.run(
                ocr_text=ocr_text,
                user_age_months=user_age_months,
                dietary_restrictions=dietary_restrictions or "None",
                regulations=reg_text
            )
            
            # Parse JSON response
            analysis = json.loads(response.strip())
            
            logger.info(f"Ollama analysis generated: {analysis['verdict']}")
            return self._format_analysis(analysis)
            
        except Exception as e:
            logger.error(f"Ollama analysis failed: {e}")
            raise
    
    def _format_analysis(self, llm_output: Dict) -> Dict:
        """Format LLM output to match expected structure."""
        return {
            "verdict": llm_output.get("verdict", "fair"),
            "summary": llm_output.get("short_summary", "Product analysis completed"),
            "detail": llm_output.get("detailed_analysis", ""),
            "allergens": llm_output.get("allergens", []),
            "dietary_flags": {
                "is_halal": llm_output.get("is_halal"),
                "is_vegan": llm_output.get("is_vegan", False),
                "is_infant_safe": llm_output.get("is_infant_safe", True)
            },
            "flags": llm_output.get("dietary_flags", [])
        }


class OpenAILLMProvider(LLMProviderInterface):
    """
    OpenAI LLM provider for cloud-based AI inference.
    Uses GPT models via OpenAI API.
    """
    
    def __init__(self, api_key: str = None, model: str = "gpt-4o-mini"):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model = model
        self.client = None
        
        if _import_openai() and self.api_key:
            try:
                self.client = openai.OpenAI(api_key=self.api_key)
                
                # Test connection
                response = self.client.chat.completions.create(
                    model=model,
                    messages=[{"role": "user", "content": "Hello"}],
                    max_tokens=10
                )
                logger.info(f"OpenAILLMProvider initialized: {model}")
                
            except Exception as e:
                logger.error(f"Failed to initialize OpenAI: {e}")
                self.client = None
        else:
            logger.warning("OpenAI not available or API key missing")
    
    def is_available(self) -> bool:
        return self.client is not None
    
    def generate_analysis(self, ocr_text: str, user_profile: Dict, regulations: List[Dict]) -> Dict:
        """Generate analysis using OpenAI."""
        if not self.is_available():
            raise Exception("OpenAI not available")
        
        try:
            user_age_months = user_profile.get("age_months", 24)
            dietary_restrictions = ", ".join(user_profile.get("dietary_restrictions", []))
            
            reg_text = "\n".join([
                f"- {reg['source']}: {reg['content']} (ID: {reg['id']})"
                for reg in regulations[:3]
            ])
            
            prompt = f"""You are a food safety expert analyzing a product label.

PRODUCT LABEL TEXT:
{ocr_text}

USER CONTEXT:
- Age: {user_age_months} months old
- Dietary Restrictions: {dietary_restrictions}

RELEVANT REGULATIONS:
{reg_text}

Analyze this product and provide a JSON response with:
- verdict: excellent|good|fair|poor|hazardous
- short_summary: One sentence (max 150 chars)
- detailed_analysis: Full explanation with citations
- allergens: Array of {{substance, severity, evidence}}
- is_halal: true|false|null
- is_vegan: true|false
- is_infant_safe: true|false
- dietary_flags: Array of strings

For infants <12 months, flag sugar/salt as hazardous. Respond only with valid JSON."""

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a food safety expert. Respond only with valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=2000
            )
            
            analysis = json.loads(response.choices[0].message.content)
            logger.info(f"OpenAI analysis generated: {analysis['verdict']}")
            return self._format_analysis(analysis)
            
        except Exception as e:
            logger.error(f"OpenAI analysis failed: {e}")
            raise
    
    def _format_analysis(self, llm_output: Dict) -> Dict:
        """Format LLM output to match expected structure."""
        return {
            "verdict": llm_output.get("verdict", "fair"),
            "summary": llm_output.get("short_summary", "Product analysis completed"),
            "detail": llm_output.get("detailed_analysis", ""),
            "allergens": llm_output.get("allergens", []),
            "dietary_flags": {
                "is_halal": llm_output.get("is_halal"),
                "is_vegan": llm_output.get("is_vegan", False),
                "is_infant_safe": llm_output.get("is_infant_safe", True)
            },
            "flags": llm_output.get("dietary_flags", [])
        }


class LLMProviderFactory:
    """
    Factory class for creating LLM providers based on configuration.
    Supports mock, ollama, and openai providers.
    """
    
    @staticmethod
    def create_provider(provider_type: str = None) -> LLMProviderInterface:
        """
        Create an LLM provider based on the LLM_PROVIDER environment variable.
        
        Args:
            provider_type: Override for provider type (mock, ollama, openai)
            
        Returns:
            LLMProviderInterface instance
        """
        provider_type = provider_type or os.getenv("LLM_PROVIDER", "mock").lower()
        
        logger.info(f"Creating LLM provider: {provider_type}")
        
        if provider_type == "ollama":
            provider = OllamaLLMProvider()
            if provider.is_available():
                return provider
            else:
                logger.warning("Ollama not available, falling back to mock")
                return MockLLMProvider()
        
        elif provider_type == "openai":
            provider = OpenAILLMProvider()
            if provider.is_available():
                return provider
            else:
                logger.warning("OpenAI not available, falling back to mock")
                return MockLLMProvider()
        
        elif provider_type == "mock":
            return MockLLMProvider()
        
        else:
            logger.warning(f"Unknown provider type: {provider_type}, falling back to mock")
            return MockLLMProvider()


class RAGProviderFactory:
    """
    Factory class for creating RAG providers based on configuration.
    Supports mock and pinecone providers.
    """
    
    @staticmethod
    def create_provider(enable_rag: bool = None) -> RAGServiceInterface:
        """
        Create a RAG provider based on the ENABLE_RAG environment variable.
        
        Args:
            enable_rag: Override for RAG enablement
            
        Returns:
            RAGServiceInterface instance
        """
        enable_rag = enable_rag if enable_rag is not None else os.getenv("ENABLE_RAG", "false").lower() == "true"
        
        if enable_rag and os.getenv("PINECONE_API_KEY"):
            logger.info("Creating Pinecone RAG provider")
            try:
                # Use the existing VectorDatabase class as Pinecone provider
                return VectorDatabase()
            except Exception as e:
                logger.error(f"Failed to create Pinecone provider: {e}")
                logger.info("Falling back to MockRAGService")
                return MockRAGService()
        else:
            logger.info("Creating Mock RAG provider")
            return MockRAGService()


class VectorDatabase(RAGServiceInterface):
    """
    Production RAG system using Pinecone for regulatory knowledge retrieval.
    
    Features:
    - Stores and indexes regulatory documents (WHO, FDA, PFA, PSQCA)
    - Semantic search for relevant food safety guidelines
    - Supports regional filtering (Pakistan, Global)
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        index_name: str = "nutriscan-regulations",
        embedding_model: str = "all-MiniLM-L6-v2"
    ):
        """
        Initialize Pinecone vector database connection.
        
        Args:
            api_key: Pinecone API key (from environment if not provided)
            index_name: Name of the Pinecone index
            embedding_model: SentenceTransformer model for embeddings
        """
        self.index_name = index_name
        self.api_key = api_key or os.getenv("PINECONE_API_KEY")
        
        # Initialize embedding model
        if SentenceTransformer is None:
            logger.warning("SentenceTransformer not available, using mock mode")
            self.embedder = None
            self.use_mock = True
        else:
            try:
                self.embedder = SentenceTransformer(embedding_model)
                logger.info(f"Loaded embedding model: {embedding_model}")
                self.use_mock = False
            except Exception as e:
                logger.error(f"Failed to load embedding model: {e}")
                self.embedder = None
                self.use_mock = True
        
        # Initialize Pinecone
        if Pinecone is None or self.api_key is None:
            logger.warning("Pinecone not configured, using mock mode")
            self.pc = None
            self.index = None
            self.use_mock = True
        else:
            try:
                self.pc = Pinecone(api_key=self.api_key)
                
                # Check if index exists, create if not
                existing_indexes = [idx.name for idx in self.pc.list_indexes()]
                
                if self.index_name not in existing_indexes:
                    logger.info(f"Creating Pinecone index: {self.index_name}")
                    self.pc.create_index(
                        name=self.index_name,
                        dimension=384,  # all-MiniLM-L6-v2 dimension
                        metric="cosine",
                        spec=ServerlessSpec(cloud="aws", region="us-east-1")
                    )
                
                self.index = self.pc.Index(self.index_name)
                logger.info(f"Connected to Pinecone index: {self.index_name}")
                
            except Exception as e:
                logger.error(f"Failed to initialize Pinecone: {e}")
                self.pc = None
                self.index = None
                self.use_mock = True
    
    def search_regulations(self, keywords: List[str], region: str, top_k: int = 5) -> List[Dict]:
        """
        Search for relevant food safety regulations using semantic search.
        
        Args:
            keywords: List of ingredient names or health concerns
            region: Geographic region (e.g., 'PK-Punjab', 'Global', 'US-FDA')
            top_k: Number of top results to return
            
        Returns:
            List of relevant regulatory documents with citations
        """
        if self.use_mock:
            return self._get_mock_regulations(keywords, region)
        
        try:
            # Create search query from keywords
            query_text = " ".join(keywords)
            
            # Generate embedding for query
            query_embedding = self.embedder.encode(query_text).tolist()
            
            # Search Pinecone
            results = self.index.query(
                vector=query_embedding,
                top_k=top_k,
                include_metadata=True,
                filter={"region": region} if region != "Global" else {}
            )
            
            # Parse results
            regulations = []
            for match in results.matches:
                regulations.append({
                    "source": match.metadata.get("source", "Unknown"),
                    "content": match.metadata.get("content", ""),
                    "id": match.metadata.get("doc_id", match.id),
                    "url": match.metadata.get("url", ""),
                    "score": float(match.score)
                })
            
            logger.info(f"Retrieved {len(regulations)} regulations from Pinecone")
            return regulations
            
        except Exception as e:
            logger.error(f"Pinecone search failed: {e}")
            return self._get_mock_regulations(keywords, region)
    
    def _get_mock_regulations(self, keywords: List[str], region: str) -> List[Dict]:
        """Fallback mock regulations when Pinecone is unavailable."""
        return [
            {
                "source": "WHO Guidelines on Complementary Feeding",
                "content": "Added sugars should not be introduced before 2 years of age.",
                "id": "WHO-2023-SUGAR",
                "url": "https://www.who.int/nutrition/guidelines",
                "score": 0.92
            },
            {
                "source": "Punjab Pure Food Rules",
                "content": "Vanillin is permitted, but natural flavors are preferred for infants.",
                "id": "PFA-RULES-2018",
                "url": "https://pfa.gop.pk/",
                "score": 0.85
            },
            {
                "source": "PSQCA Standards for Infant Foods",
                "content": "Sodium content must not exceed 100mg per serving for infant cereals.",
                "id": "PSQCA-2021-SODIUM",
                "url": "https://psqca.com.pk/",
                "score": 0.78
            }
        ]
    
    def ingest_document(self, doc_id: str, content: str, metadata: Dict):
        """
        Add a new regulatory document to the vector database.
        
        Args:
            doc_id: Unique document identifier
            content: Text content of the regulation
            metadata: Additional metadata (source, region, url, etc.)
        """
        if self.use_mock:
            logger.warning("Mock mode: Document ingestion skipped")
            return
        
        try:
            # Generate embedding
            embedding = self.embedder.encode(content).tolist()
            
            # Upsert to Pinecone
            self.index.upsert(
                vectors=[(doc_id, embedding, metadata)]
            )
            
            logger.info(f"Ingested document: {doc_id}")
            
        except Exception as e:
            logger.error(f"Document ingestion failed: {e}")


class LLMAgent:
    """
    Production Agentic AI using Ollama + LangChain for health impact analysis.
    
    Model: Qwen 2.5 7B (Q4_K_M quantized)
    Framework: LangChain
    Purpose: Analyze ingredients against regulations and generate health verdicts
    """
    
    def __init__(
        self,
        model_name: str = "qwen2.5:7b-instruct-q4_K_M",
        base_url: str = "http://localhost:11434",
        temperature: float = 0.3,
        timeout: int = 60
    ):
        """
        Initialize Ollama LLM with LangChain.
        
        Args:
            model_name: Ollama model identifier
            base_url: Ollama server URL
            temperature: LLM temperature (0.0-1.0, lower = more deterministic)
            timeout: Request timeout in seconds
        """
        self.model_name = model_name
        self.temperature = temperature
        
        # Try to import LangChain components
        langchain_available = _import_langchain()
        
        if not langchain_available or Ollama is None:
            logger.warning("LangChain/Ollama not available, using mock mode")
            self.llm = None
            self.use_mock = True
        else:
            try:
                # Initialize Ollama LLM
                self.llm = Ollama(
                    model=model_name,
                    base_url=base_url,
                    temperature=temperature,
                    timeout=timeout
                )
                
                # Test connection
                test_response = self.llm.invoke("Hello")
                logger.info(f"LLM initialized: {model_name}")
                self.use_mock = False
                
            except Exception as e:
                logger.error(f"Failed to initialize Ollama: {e}")
                self.llm = None
                self.use_mock = True
        
        # Define prompt template for health analysis
        if PromptTemplate is not None:
            self.analysis_prompt = PromptTemplate(
                input_variables=["ocr_text", "user_age_months", "dietary_restrictions", "regulations"],
                template="""You are a food safety expert analyzing a product label for health impact.

PRODUCT LABEL TEXT:
{ocr_text}

USER CONTEXT:
- Age: {user_age_months} months old
- Dietary Restrictions: {dietary_restrictions}

RELEVANT REGULATIONS:
{regulations}

TASK: Analyze this product and provide a structured health assessment.

OUTPUT FORMAT (JSON):
{{
    "verdict": "excellent|good|fair|poor|hazardous",
    "short_summary": "One sentence summary (max 150 chars)",
    "detailed_analysis": "Detailed explanation with regulatory citations",
    "allergens": [
        {{"substance": "name", "severity": "high|medium|low", "evidence": "where found in label"}}
    ],
    "is_halal": true|false|null,
    "is_vegan": true|false,
    "is_infant_safe": true|false,
    "dietary_flags": ["flag1", "flag2"]
}}

CRITICAL RULES:
1. For infants (<12 months), flag ANY added sugar, salt, or honey as hazardous
2. Cite specific regulations in detailed_analysis
3. Identify ALL allergens (milk, wheat, soy, nuts, eggs, fish, shellfish)
4. Check for artificial additives and provide E-codes where applicable

Respond ONLY with valid JSON, no additional text."""
            )
        else:
            self.analysis_prompt = None
            logger.warning("PromptTemplate not available, using mock mode")
    
    def generate_analysis(
        self, 
        ocr_text: str, 
        user_profile: Dict, 
        regulations: List[Dict]
    ) -> Dict:
        """
        Generate health impact analysis using LLM with regulatory context.
        
        Args:
            ocr_text: Raw text from OCR
            user_profile: User demographics and preferences
            regulations: Retrieved regulatory documents from VectorDB
            
        Returns:
            Structured analysis with verdict, allergens, and recommendations
        """
        if self.use_mock:
            return self._generate_mock_analysis(ocr_text, user_profile, regulations)
        
        try:
            # Prepare inputs
            user_age_months = user_profile.get("age_months", 24)
            dietary_restrictions = ", ".join(user_profile.get("dietary_restrictions", []))
            
            # Format regulations for prompt
            reg_text = "\n".join([
                f"- {reg['source']}: {reg['content']} (ID: {reg['id']})"
                for reg in regulations[:3]  # Top 3 most relevant
            ])
            
            # Create chain
            chain = LLMChain(llm=self.llm, prompt=self.analysis_prompt)
            
            # Generate analysis
            response = chain.run(
                ocr_text=ocr_text,
                user_age_months=user_age_months,
                dietary_restrictions=dietary_restrictions or "None",
                regulations=reg_text
            )
            
            # Parse JSON response
            import json
            analysis = json.loads(response.strip())
            
            logger.info(f"LLM analysis generated: {analysis['verdict']}")
            return self._format_analysis(analysis)
            
        except Exception as e:
            logger.error(f"LLM analysis failed: {e}")
            return self._generate_mock_analysis(ocr_text, user_profile, regulations)
    
    def _format_analysis(self, llm_output: Dict) -> Dict:
        """Format LLM output to match expected structure."""
        return {
            "verdict": llm_output.get("verdict", "fair"),
            "summary": llm_output.get("short_summary", "Product analysis completed"),
            "detail": llm_output.get("detailed_analysis", ""),
            "allergens": llm_output.get("allergens", []),
            "dietary_flags": {
                "is_halal": llm_output.get("is_halal"),
                "is_vegan": llm_output.get("is_vegan", False),
                "is_infant_safe": llm_output.get("is_infant_safe", True)
            },
            "flags": llm_output.get("dietary_flags", [])
        }
    
    def _generate_mock_analysis(
        self, 
        ocr_text: str, 
        user_profile: Dict, 
        regulations: List[Dict]
    ) -> Dict:
        """Fallback rule-based analysis when LLM is unavailable."""
        is_infant = user_profile.get("age_months", 24) < 12
        contains_sugar = "Sugar" in ocr_text or "sugar" in ocr_text
        
        # Simple rule-based logic for fallback
        if is_infant and contains_sugar:
            verdict = "poor"
            summary = "Not recommended for your infant due to added sugar."
            detail = "This product lists Sugar as a primary ingredient. WHO guidelines recommend zero added sugar for infants under 2 years to prevent metabolic issues."
        else:
            verdict = "fair"
            summary = "Product contains some ingredients that require caution."
            detail = "While generally safe, be mindful of sugar content and allergens."
        
        return {
            "verdict": verdict,
            "summary": summary,
            "detail": detail,
            "allergens": [
                {
                    "substance": "Wheat",
                    "severity": "high",
                    "evidence": "Ingredient: Wheat Flour"
                },
                {
                    "substance": "Milk",
                    "severity": "high",
                    "evidence": "Ingredient: Skimmed Milk Powder"
                }
            ],
            "dietary_flags": {
                "is_halal": None,
                "is_vegan": False,
                "is_infant_safe": not (is_infant and contains_sugar)
            },
            "flags": ["Contains Milk", "Contains Gluten"]
        }


class NutriScanPipeline:
    """
    Main orchestrator for the complete analysis workflow - Phase 2 Production.
    
    Features:
    - Real OCR with PaddleOCR
    - RAG-based regulatory retrieval with Pinecone
    - LLM-powered health analysis with Ollama
    - Performance monitoring and error handling
    - Fallback mechanisms for reliability
    """
    
    def __init__(
        self,
        ocr_confidence_threshold: float = 0.5,
        enable_gpu: bool = False,
        performance_target_seconds: float = 4.0
    ):
        """
        Initialize pipeline with all AI components using factory pattern.
        
        Args:
            ocr_confidence_threshold: Minimum OCR confidence (0.0-1.0)
            enable_gpu: Enable GPU acceleration for OCR/LLM
            performance_target_seconds: Target response time (default 4s per spec)
        """
        self.performance_target = performance_target_seconds
        
        try:
            # Initialize OCR Service
            self.ocr = OCRService(
                use_gpu=enable_gpu,
                enable_table_recognition=True,
                confidence_threshold=ocr_confidence_threshold
            )
            logger.info("OCRService initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize OCR: {e}")
            self.ocr = None
        
        # Initialize RAG Service using factory
        try:
            self.rag_service = RAGProviderFactory.create_provider()
            logger.info(f"RAG service initialized: {type(self.rag_service).__name__}")
        except Exception as e:
            logger.error(f"Failed to initialize RAG service: {e}")
            self.rag_service = MockRAGService()
        
        # Initialize LLM Provider using factory
        try:
            self.llm_provider = LLMProviderFactory.create_provider()
            logger.info(f"LLM provider initialized: {type(self.llm_provider).__name__}")
        except Exception as e:
            logger.error(f"Failed to initialize LLM provider: {e}")
            self.llm_provider = MockLLMProvider()
        
        # Backward compatibility - keep old attributes for existing code
        self.db = self.rag_service
        self.agent = None  # Deprecated, use self.llm_provider instead
    
    def process_scan(self, image_path: str, user_profile: Dict) -> Dict:
        """
        Execute complete analysis pipeline with performance monitoring.
        
        Args:
            image_path: Path to uploaded food label image
            user_profile: User context (age, region, dietary restrictions)
            
        Returns:
            Complete analysis response matching api_contract.json schema
        """
        start_time = time.time()
        
        try:
            # Step 1: Extract text via OCR (Target: <2s)
            logger.info("Step 1: Running OCR extraction...")
            ocr_start = time.time()
            
            if self.ocr:
                ocr_result = self.ocr.extract_structured(image_path)
                raw_text = ocr_result['raw_text']
                ocr_confidence = ocr_result['confidence_avg']
                ocr_status = ocr_result['status']
            else:
                raw_text = self._get_fallback_ocr_text()
                ocr_confidence = 0.0
                ocr_status = "unreadable"
            
            ocr_time = time.time() - ocr_start
            logger.info(f"OCR completed in {ocr_time:.2f}s (confidence: {ocr_confidence:.2f})")
            
            # Step 2: Extract search terms for regulatory lookup
            logger.info("Step 2: Extracting ingredient keywords...")
            search_terms = self._extract_keywords(raw_text)
            
            # Step 3: Retrieve relevant regulations (RAG) (Target: <1s)
            logger.info("Step 3: Searching regulatory database...")
            rag_start = time.time()
            
            region = user_profile.get("region", "Global")
            regulations = self.rag_service.search_regulations(search_terms, region, top_k=5)
            
            rag_time = time.time() - rag_start
            logger.info(f"RAG search completed in {rag_time:.2f}s ({len(regulations)} docs)")
            
            # Step 4: Generate health analysis (Target: <1s)
            logger.info("Step 4: Generating LLM health analysis...")
            llm_start = time.time()
            
            analysis = self.llm_provider.generate_analysis(raw_text, user_profile, regulations)
            
            llm_time = time.time() - llm_start
            logger.info(f"LLM analysis completed in {llm_time:.2f}s (verdict: {analysis['verdict']})")
            
            # Step 5: Parse ingredients (Enhanced with NLP in future)
            logger.info("Step 5: Parsing ingredient list...")
            parsed_ingredients = self._parse_ingredients(raw_text, analysis)
            
            # Step 6: Extract nutrition facts
            nutrition_facts = self._extract_nutrition_facts(raw_text)
            
            # Step 7: Generate better alternatives
            suggestions = self._generate_suggestions(analysis, user_profile)
            
            # Step 8: Construct final response
            total_time_ms = int((time.time() - start_time) * 1000)
            
            # Map verdict to traffic light color
            verdict_to_traffic_light = {
                "excellent": "green",
                "good": "green",
                "fair": "yellow",
                "poor": "red",
                "hazardous": "red"
            }
            traffic_light = verdict_to_traffic_light.get(analysis["verdict"], "yellow")
            
            # Generate "why" explanation
            why_text = f"{analysis['summary']} "
            if parsed_ingredients:
                risk_ingredients = [ing["name"] for ing in parsed_ingredients if ing["risk_level"] in ["avoid", "caution"]]
                if risk_ingredients:
                    why_text += f"Contains {', '.join(risk_ingredients[:3])} which require caution."
            
            # Separate better_swaps from general suggestions
            better_swaps = [s for s in suggestions if s.get("type") == "swap"]
            
            # Format citations (same as sources but with more detail)
            citations = [
                {
                    "authority": reg["source"],
                    "doc_id": reg["id"],
                    "url": reg.get("url", ""),
                    "excerpt": reg.get("content", "")[:200]  # First 200 chars
                }
                for reg in regulations
            ]
            
            # Generate regulatory_flags if needed
            regulatory_flags = []
            if analysis["verdict"] in ["poor", "hazardous"]:
                regulatory_flags.append({
                    "regulation": "General Food Safety Standards",
                    "severity": "warning",
                    "description": "Product contains ingredients that may not meet optimal health standards."
                })
            
            response = {
                "scan_id": str(uuid.uuid4()),
                "timestamp": datetime.now().isoformat(),
                "status": ocr_status,
                "user_context_used": {
                    "age_months": user_profile.get("age_months"),
                    "dietary_restrictions": user_profile.get("dietary_restrictions", []),
                    "region": region
                },
                "ocr_raw_text": raw_text.strip(),
                "ocr_confidence": ocr_confidence,
                "parsed_ingredients": parsed_ingredients,
                "nutrition_facts": nutrition_facts,
                "allergen_alerts": analysis["allergens"],
                "dietary_compliance": {
                    "is_halal": analysis["dietary_flags"]["is_halal"],
                    "is_vegan": analysis["dietary_flags"]["is_vegan"],
                    "is_infant_safe": analysis["dietary_flags"]["is_infant_safe"],
                    "flags": analysis.get("flags", [])
                },
                "health_impact_summary": {
                    "verdict": analysis["verdict"],
                    "short_summary": analysis["summary"],
                    "detailed_analysis": analysis["detail"]
                },
                "traffic_light": traffic_light,
                "why": why_text.strip(),
                "citations": citations,
                "better_swaps": better_swaps,
                "suggestions": suggestions,
                "sources": [
                    {
                        "authority": reg["source"],
                        "doc_id": reg["id"],
                        "url": reg.get("url", "")
                    }
                    for reg in regulations
                ],
                "latency_ms": total_time_ms,
                "regulatory_flags": regulatory_flags
            }
            
            # Performance monitoring
            total_time = time.time() - start_time
            logger.info(f"Pipeline completed in {total_time:.2f}s (target: {self.performance_target}s)")
            
            if total_time > self.performance_target:
                logger.warning(f"Performance target exceeded by {total_time - self.performance_target:.2f}s")
            
            return response
            
        except Exception as e:
            logger.error(f"Pipeline processing failed: {e}", exc_info=True)
            return self._generate_error_response(str(e))
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract ingredient and health-related keywords from OCR text."""
        # Simple keyword extraction (Phase 3: Use spaCy NER)
        keywords = []
        
        # Common ingredient indicators
        common_terms = [
            "Sugar", "Salt", "Sodium", "Fat", "Wheat", "Milk", "Soy", 
            "Vanillin", "Preservative", "Colorant", "Flavor", "Vitamin",
            "Calcium", "Iron", "Protein", "Carbohydrate"
        ]
        
        text_lower = text.lower()
        for term in common_terms:
            if term.lower() in text_lower:
                keywords.append(term)
        
        # Add age-specific concerns
        keywords.extend(["Infant Nutrition", "Added Sugar", "Allergens"])
        
        return list(set(keywords))  # Remove duplicates
    
    def _parse_ingredients(self, ocr_text: str, analysis: Dict) -> List[Dict]:
        """Parse ingredient list from OCR text."""
        # Simple parsing (Phase 3: Use NLP for better extraction)
        ingredients = []
        
        # Try to find ingredients section
        if "INGREDIENTS:" in ocr_text or "Ingredients:" in ocr_text:
            # Extract ingredient line
            lines = ocr_text.split('\n')
            for i, line in enumerate(lines):
                if 'INGREDIENT' in line.upper():
                    # Get next line or same line after colon
                    if ':' in line:
                        ingredient_text = line.split(':', 1)[1]
                    elif i + 1 < len(lines):
                        ingredient_text = lines[i + 1]
                    else:
                        continue
                    
                    # Split by comma
                    items = ingredient_text.split(',')
                    for item in items[:10]:  # Limit to top 10
                        name = item.strip()
                        if name:
                            ingredients.append({
                                "name": name,
                                "category": self._categorize_ingredient(name),
                                "risk_level": self._assess_risk(name, analysis),
                                "description": f"Ingredient: {name}"
                            })
        
        # Fallback if no ingredients found
        if not ingredients:
            ingredients = [
                {"name": "Sugar", "category": "sweetener", "risk_level": "caution", "description": "Added sweetener"},
                {"name": "Wheat Flour", "category": "core_ingredient", "risk_level": "safe", "description": "Primary grain"},
                {"name": "Vanillin", "category": "additive", "risk_level": "caution", "description": "Artificial flavoring"}
            ]
        
        return ingredients
    
    def _categorize_ingredient(self, name: str) -> str:
        """Categorize ingredient by type."""
        name_lower = name.lower()
        
        if any(s in name_lower for s in ['sugar', 'syrup', 'sweetener', 'dextrose', 'fructose']):
            return "sweetener"
        elif any(s in name_lower for s in ['flavor', 'vanillin', 'artificial']):
            return "additive"
        elif any(s in name_lower for s in ['preservative', 'benzoate', 'sorbate']):
            return "preservative"
        elif any(s in name_lower for s in ['color', 'colorant', 'dye']):
            return "colorant"
        elif any(s in name_lower for s in ['flour', 'wheat', 'rice', 'corn', 'oat']):
            return "core_ingredient"
        else:
            return "unknown"
    
    def _assess_risk(self, ingredient: str, analysis: Dict) -> str:
        """Assess risk level of ingredient based on analysis."""
        verdict = analysis.get("verdict", "fair")
        
        if verdict in ["hazardous", "poor"]:
            if any(term in ingredient.lower() for term in ['sugar', 'salt', 'artificial']):
                return "avoid"
        
        if any(term in ingredient.lower() for term in ['preservative', 'colorant', 'flavor']):
            return "caution"
        
        return "safe"
    
    def _extract_nutrition_facts(self, ocr_text: str) -> Dict:
        """Extract nutrition facts from OCR text."""
        import re
        
        nutrition = {
            "serving_size": "100g",
            "calories": None,
            "sugar_g": None,
            "sodium_mg": None,
            "fat_g": None
        }
        
        # Simple regex extraction
        text_lower = ocr_text.lower()
        
        # Calories
        cal_match = re.search(r'(\d+)\s*kcal', text_lower)
        if cal_match:
            nutrition["calories"] = float(cal_match.group(1))
        
        # Sugar
        sugar_match = re.search(r'sugar[:\s]+(\d+\.?\d*)\s*g', text_lower)
        if sugar_match:
            nutrition["sugar_g"] = float(sugar_match.group(1))
        
        # Sodium
        sodium_match = re.search(r'sodium[:\s]+(\d+\.?\d*)\s*mg', text_lower)
        if sodium_match:
            nutrition["sodium_mg"] = float(sodium_match.group(1))
        
        # Fat
        fat_match = re.search(r'fat[:\s]+(\d+\.?\d*)\s*g', text_lower)
        if fat_match:
            nutrition["fat_g"] = float(fat_match.group(1))
        
        return nutrition
    
    def _generate_suggestions(self, analysis: Dict, user_profile: Dict) -> List[Dict]:
        """Generate product swap suggestions based on analysis."""
        suggestions = []
        
        verdict = analysis.get("verdict", "fair")
        is_infant = user_profile.get("age_months", 24) < 12
        
        if verdict in ["poor", "hazardous"] and is_infant:
            suggestions.append({
                "type": "swap",
                "product_name": "Organic Baby Cereal (No Added Sugar)",
                "reason": "Better for infant development without added sugars"
            })
        
        if analysis["dietary_flags"].get("is_vegan") is False:
            suggestions.append({
                "type": "usage_tip",
                "reason": "Consider checking for plant-based alternatives if avoiding animal products"
            })
        
        return suggestions
    
    def _get_fallback_ocr_text(self) -> str:
        """Fallback OCR text when service is unavailable."""
        return """
        INGREDIENTS: Wheat Flour, Sugar, Skimmed Milk Powder, 
        Vegetable Oil, Calcium Carbonate, Artificial Flavor (Vanillin), 
        Vitamin C, Iron.
        NUTRITION: Energy 400kcal, Sugar 18g, Fat 5g, Sodium 120mg.
        """
    
    def _get_fallback_regulations(self) -> List[Dict]:
        """Fallback regulations when database is unavailable."""
        return [
            {
                "source": "WHO Guidelines on Complementary Feeding",
                "content": "Added sugars should not be introduced before 2 years of age.",
                "id": "WHO-2023-SUGAR",
                "url": "https://www.who.int/nutrition/guidelines",
                "score": 0.92
            }
        ]
    
    def _get_fallback_analysis(self, ocr_text: str, user_profile: Dict) -> Dict:
        """Fallback analysis when LLM is unavailable."""
        is_infant = user_profile.get("age_months", 24) < 12
        contains_sugar = "Sugar" in ocr_text or "sugar" in ocr_text
        
        if is_infant and contains_sugar:
            verdict = "poor"
            summary = "Not recommended for your infant due to added sugar."
            detail = "This product contains added sugar, which is not recommended for infants under 2 years."
        else:
            verdict = "fair"
            summary = "Product requires caution regarding certain ingredients."
            detail = "Check allergen information and nutritional content."
        
        return {
            "verdict": verdict,
            "summary": summary,
            "detail": detail,
            "allergens": [
                {"substance": "Wheat", "severity": "high", "evidence": "Contains Wheat Flour"},
                {"substance": "Milk", "severity": "high", "evidence": "Contains Milk Powder"}
            ],
            "dietary_flags": {
                "is_halal": None,
                "is_vegan": False,
                "is_infant_safe": not (is_infant and contains_sugar)
            },
            "flags": ["Contains Gluten", "Contains Dairy"]
        }
    
    def _generate_error_response(self, error_message: str) -> Dict:
        """Generate error response that maintains API contract."""
        return {
            "scan_id": str(uuid.uuid4()),
            "timestamp": datetime.now().isoformat(),
            "status": "unreadable",
            "user_context_used": {
                "age_months": None,
                "dietary_restrictions": [],
                "region": "Global"
            },
            "ocr_raw_text": f"Error: {error_message}",
            "ocr_confidence": 0.0,
            "parsed_ingredients": [],
            "nutrition_facts": None,
            "allergen_alerts": [],
            "dietary_compliance": None,
            "health_impact_summary": {
                "verdict": "hazardous",
                "short_summary": "Unable to process image",
                "detailed_analysis": f"An error occurred during processing: {error_message}. Please retake the photo with better lighting and ensure the label is clearly visible."
            },
            "traffic_light": "red",
            "why": "Cannot verify product safety due to processing error.",
            "citations": [],
            "better_swaps": [],
            "suggestions": [
                {
                    "type": "usage_tip",
                    "reason": "Retake photo in good lighting with ingredients list clearly visible"
                }
            ],
            "sources": [],
            "latency_ms": 0,
            "regulatory_flags": []
        }

