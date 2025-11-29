# Phase 2: AI Service Layer Integration - Implementation Prompt
**NutriScan Production Upgrade: From Mock to Real AI**

---

## Objective

Transform the mock implementations in `backend_logic.py` into production-ready AI services by integrating:
1. **PaddleOCR** for real text extraction from food labels (English + Urdu)
2. **LangChain/CrewAI + Ollama (Qwen 2.5 7B)** for agentic health impact analysis
3. **Pinecone/ChromaDB** for RAG-based regulatory retrieval

The integration must maintain the existing API contract defined in `api_contract.json` while achieving performance targets: **OCR accuracy >95%**, **latency <4s**, and **zero false negatives** for major allergens.

---

## Current Architecture Overview

### Mock Implementation (backend_logic.py)
The current `backend_logic.py` contains three mock classes that simulate the complete workflow:

```python
class OCRService:           # Returns hardcoded ingredient text
class VectorDatabase:       # Returns hardcoded WHO/PFA regulations
class LLMAgent:             # Returns hardcoded verdict based on simple if/else
class NutriScanPipeline:    # Orchestrates all three services
```

### Target Production Files
Replace mock implementations with real AI integrations in:
- **`analyzer/services/ocr.py`** → Real PaddleOCR implementation
- **`analyzer/services/pipeline.py`** → Real LangChain/Ollama + Pinecone integration
- **`analyzer/views.py`** → Already configured to call pipeline (no changes needed)

### API Contract (api_contract.json)
The response schema defines the expected output structure:

**Critical Fields:**
- `status`: `success` | `partial_ocr_failure` | `unreadable`
- `health_impact_summary.verdict`: `excellent` | `good` | `fair` | `poor` | `hazardous`
- `parsed_ingredients`: Array with `name`, `risk_level`, `category`
- `allergen_alerts`: Array with `substance`, `severity`, `evidence`
- `dietary_compliance`: `is_halal`, `is_vegan`, `is_infant_safe`
- `sources`: Array of regulatory citations

**The pipeline MUST return this exact structure** regardless of internal implementation.

---

## Component 1: OCR Service Integration (PaddleOCR)

### Technical Specifications

**Model:** PaddleOCR v2.7.3 with PaddlePaddle 2.6.2

**Languages:** English (primary) + Urdu (secondary for Pakistani market)

**Configuration:**
```python
from paddleocr import PaddleOCR

# English OCR engine
ocr_en = PaddleOCR(
    use_angle_cls=True,      # Handle rotated/curved text on packaging
    lang='en',
    use_gpu=False,           # CPU mode (set True if CUDA available)
    show_log=False,
    det_db_score_mode='slow' # Higher accuracy for small fonts
)

# Urdu OCR engine (for multilingual labels)
ocr_ur = PaddleOCR(
    use_angle_cls=True,
    lang='ur',               # Nastaliq/Naskh script support
    use_gpu=False,
    show_log=False
)
```

### Implementation Requirements

#### File: `analyzer/services/ocr.py`

**Class:** `OCRService`

**Methods:**
1. **`__init__(self, use_gpu: bool = False, confidence_threshold: float = 0.5)`**
   - Initialize both English and Urdu PaddleOCR engines
   - Set confidence threshold for filtering low-quality text
   - Enable angle classification for handling curved labels

2. **`extract_text(self, image_path: str) -> str`**
   - **Input:** Path to uploaded food label image (JPEG/PNG)
   - **Output:** Clean concatenated text string
   - **Process:**
     - Run English OCR first (primary language)
     - Run Urdu OCR if `detect_language=True`
     - Merge multilingual results (English takes priority for overlapping regions)
     - Filter out text with confidence < threshold
     - Return normalized text (handle OCR errors like "Slat" → "Salt" using fuzzy matching)

3. **`extract_structured(self, image_path: str) -> Dict`**
   - **Input:** Image path
   - **Output:** Dictionary with:
     ```python
     {
       'raw_text': str,              # Full concatenated text
       'lines': List[Dict],           # Each line with bbox, confidence, text
       'nutrition_table': Dict,       # Extracted table structure (if detected)
       'confidence_avg': float,       # Average confidence score
       'status': str                  # 'success' | 'partial_ocr_failure' | 'unreadable'
     }
     ```
   - **Process:**
     - Parse bounding boxes for layout analysis
     - Detect "INGREDIENTS:" vs "NUTRITION:" sections
     - Extract tabular data for nutrition facts (use PaddleOCR table recognition if available)
     - Calculate average confidence score across all detected text

### Performance Targets

| Metric | Target | Validation Method |
|--------|--------|-------------------|
| **Accuracy** | >95% on ingredient names | Test on 100 Pakistani product labels |
| **Allergen Detection** | 100% recall (zero false negatives) | Bolded allergen text must always be captured |
| **Latency** | <2 seconds per scan | Average over 50 scans on 8-core CPU |
| **Urdu Support** | >85% accuracy | Test on 20 bilingual labels (Shan, National Foods) |

### Error Handling

**Fallback Strategy:**
- If OCR confidence < 50% → Return `status: "partial_ocr_failure"` + user prompt to retake photo
- If OCR completely fails → Return mock text from `backend_logic.py` to maintain API contract
- Log all failures with image metadata for continuous model improvement

### Dependencies (requirements.txt)
```python
paddleocr==2.7.3              # OCR engine
paddlepaddle==2.6.2           # Deep learning framework
Pillow==10.3.0                # Image processing
opencv-python==4.8.1.78       # Optional: For advanced image preprocessing
```

---

## Component 2: Vector Database Integration (RAG)

### Technical Specifications

**Primary:** Pinecone (cloud-hosted, serverless)
**Fallback:** ChromaDB (local for development)

**Purpose:** Store and retrieve food safety regulations using semantic search

### Implementation Requirements

#### File: `analyzer/services/pipeline.py`

**Class:** `VectorDatabase`

**Configuration:**
```python
from pinecone import Pinecone, ServerlessSpec
from sentence_transformers import SentenceTransformer

# Initialize Pinecone
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
index = pc.Index("nutriscan-regulations")

# Embedding model for semantic search
embedder = SentenceTransformer('all-MiniLM-L6-v2')  # 384-dim embeddings
```

**Methods:**
1. **`__init__(self, api_key: str, index_name: str = "nutriscan-regulations")`**
   - Connect to Pinecone index (create if doesn't exist)
   - Load sentence transformer model for text embeddings
   - Set up namespace filters for regional regulations (PK-Punjab, Global, US-FDA)

2. **`search_regulations(self, keywords: List[str], region: str, top_k: int = 5) -> List[Dict]`**
   - **Input:**
     - `keywords`: List of ingredients/concerns extracted from OCR (e.g., ["Sugar", "Vanillin", "Infant"])
     - `region`: User's region from profile (e.g., "PK-Punjab")
     - `top_k`: Number of regulations to retrieve
   - **Output:**
     ```python
     [
       {
         "source": "WHO Guidelines on Complementary Feeding",
         "content": "Added sugars should not be introduced before 2 years of age.",
         "id": "WHO-2023-SUGAR",
         "url": "https://www.who.int/...",
         "score": 0.92  # Cosine similarity score
       },
       ...
     ]
     ```
   - **Process:**
     - Join keywords into a single query string
     - Generate embedding using SentenceTransformer
     - Query Pinecone with region filter: `filter={"region": {"$eq": region}}`
     - Return top_k results sorted by relevance score

3. **`ingest_document(self, doc_id: str, content: str, metadata: Dict)`**
   - **Purpose:** Add new regulatory documents to the database
   - **Input:**
     - `doc_id`: Unique identifier (e.g., "PFA-2024-SODIUM")
     - `content`: Full text of the regulation
     - `metadata`: `{"source": "PFA", "region": "PK-Punjab", "url": "...", "date": "2024-01-15"}`
   - **Process:**
     - Generate embedding for content
     - Upsert to Pinecone with metadata
     - Log ingestion for audit trail

### Data Sources to Ingest (Phase 2)

**Priority Documents:**
1. **WHO Complementary Feeding Guidelines** (Global)
   - Focus: Infant nutrition (0-24 months)
   - Source: `https://www.who.int/publications/i/item/9789241549622`

2. **Punjab Food Authority Regulations** (PK-Punjab)
   - Banned additives list
   - Halal certification requirements
   - Source: `https://pfa.gop.pk/`

3. **PSQCA Standards** (Pakistan)
   - Standards for packaged infant foods
   - E-number approvals

4. **FDA Allergen Labeling** (Global reference)
   - Major allergen list (FALCPA)
   - Source: `https://www.fda.gov/food/food-allergensgluten-free-guidance-documents-regulatory-information/food-allergen-labeling`

**Ingestion Script:** `scripts/ingest_regulations.py` (already exists in workspace)

### Fallback Strategy

If Pinecone is unavailable:
- Use hardcoded regulations from `backend_logic.py`
- Log warning for monitoring
- Set `sources[].score = 0.0` to indicate mock data

### Dependencies (requirements.txt)
```python
pinecone-client==3.0.0        # Vector database
sentence-transformers==2.3.1  # Text embeddings
chromadb==0.4.22              # Local fallback vector DB
```

---

## Component 3: LLM Agent Integration (LangChain + Ollama)

### Technical Specifications

**Model:** Qwen 2.5 7B Instruct (Q4_K_M quantization)
**Framework:** LangChain (for prompt chaining and RAG)
**Inference:** Ollama (local model serving)

**Why Qwen 2.5 7B?**
- **Multilingual:** Strong English + Urdu support (critical for Pakistani market)
- **Context Window:** 32K tokens (can fit full ingredient lists + regulations)
- **Quantization:** Q4_K_M balances speed (<1s inference) with quality
- **Cost:** Free local inference (no API costs)

### Setup Instructions

**1. Install Ollama:**
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

**2. Pull Qwen 2.5 7B:**
```bash
ollama pull qwen2.5:7b-instruct-q4_K_M
```

**3. Verify model:**
```bash
ollama run qwen2.5:7b-instruct-q4_K_M "Hello, analyze this ingredient: Sugar"
```

### Implementation Requirements

#### File: `analyzer/services/pipeline.py`

**Class:** `LLMAgent`

**Configuration:**
```python
from langchain.llms import Ollama
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

# Initialize Ollama LLM
llm = Ollama(
    model="qwen2.5:7b-instruct-q4_K_M",
    base_url="http://localhost:11434",
    temperature=0.3,          # Low temperature for consistent health advice
    num_ctx=4096,             # Context window (adjust based on needs)
    timeout=60                # 60-second timeout
)
```

**Methods:**
1. **`__init__(self, model_name: str, temperature: float = 0.3)`**
   - Initialize Ollama client via LangChain
   - Load prompt templates for different analysis tasks
   - Set up streaming callbacks for real-time response (optional)

2. **`generate_analysis(self, ocr_text: str, user_profile: Dict, regulations: List[Dict]) -> Dict`**
   - **Input:**
     - `ocr_text`: Raw text from OCR service
     - `user_profile`: `{"age_months": 8, "dietary_restrictions": ["vegan"], "region": "PK-Punjab"}`
     - `regulations`: Retrieved documents from VectorDatabase
   - **Output:**
     ```python
     {
       "verdict": "poor",
       "summary": "Not recommended for your 8-month-old due to added sugar.",
       "detail": "This product lists Sugar as the second ingredient. WHO guidelines recommend...",
       "allergens": [
         {"substance": "Milk", "severity": "high", "evidence": "Ingredient: Skimmed Milk Powder"}
       ],
       "dietary_flags": {
         "is_halal": True,
         "is_vegan": False,
         "is_infant_safe": False
       },
       "flags": ["Contains Dairy", "Added Sugar"]
     }
     ```
   - **Process:**
     - Construct prompt with OCR text, user context, and regulatory citations
     - Send to Ollama via LangChain
     - Parse JSON response from LLM
     - Validate output structure (ensure all required fields exist)
     - Apply safety guardrails (infant safety checks)

### Prompt Engineering

**System Prompt Template:**
```python
ANALYSIS_PROMPT = PromptTemplate(
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
2. Cite specific regulations in detailed_analysis (use provided IDs like WHO-2023-SUGAR)
3. Identify ALL allergens (milk, wheat, soy, nuts, eggs, fish, shellfish)
4. Check for artificial additives and provide E-codes where applicable
5. For Halal assessment, flag gelatin, alcohol derivatives, non-Halal enzymes
6. ALWAYS return valid JSON, no additional text

Respond ONLY with valid JSON, no markdown code blocks."""
)
```

**Usage:**
```python
chain = LLMChain(llm=llm, prompt=ANALYSIS_PROMPT)
response = chain.run(
    ocr_text=raw_text,
    user_age_months=8,
    dietary_restrictions="None",
    regulations="- WHO: No added sugar for infants\n- PFA: Vanillin permitted"
)
analysis = json.loads(response)
```

### Agentic Safety Guardrails

**Post-Processing Rules (Applied After LLM Response):**

1. **Infant Safety Override:**
   ```python
   if user_profile["age_months"] < 12:
       if any(term in ocr_text.lower() for term in ["sugar", "honey", "salt"]):
           analysis["verdict"] = "hazardous"
           analysis["is_infant_safe"] = False
   ```

2. **Allergen Validation:**
   - Cross-reference LLM-detected allergens with known allergen keywords
   - If LLM misses a bolded allergen in OCR text → Force add to `allergen_alerts`

3. **Hallucination Prevention:**
   - If LLM cites a regulation ID not in the retrieved `regulations` list → Remove citation
   - If verdict is "hazardous" but analysis lacks evidence → Downgrade to "poor"

### Performance Targets

| Metric | Target | Validation Method |
|--------|--------|-------------------|
| **Inference Latency** | <1.5 seconds | Average over 50 prompts on 8-core CPU |
| **Accuracy (Verdict)** | 90% agreement with expert nutritionist | Test on 100 labeled products |
| **Allergen Recall** | 100% (zero false negatives) | Must catch all major allergens |
| **Citation Accuracy** | >95% citations match retrieved regulations | Audit 50 responses |

### Fallback Strategy

If Ollama fails (model not running, timeout, etc.):
- Use rule-based mock analysis from `backend_logic.py`
- Log failure with error details
- Return `status: "partial_ocr_failure"` to indicate degraded mode

### Dependencies (requirements.txt)
```python
langchain==0.1.0              # LLM orchestration
langchain-community==0.0.12   # Ollama integration
ollama==0.1.6                 # Ollama Python SDK
```

---

## Component 4: Pipeline Orchestration

### Implementation Requirements

#### File: `analyzer/services/pipeline.py`

**Class:** `NutriScanPipeline`

**Purpose:** Orchestrate the complete workflow while maintaining API contract

**Methods:**
1. **`__init__(self, ocr_threshold: float = 0.5, enable_gpu: bool = False)`**
   - Initialize all three services (OCR, VectorDB, LLM)
   - Set performance monitoring flags
   - Configure fallback modes

2. **`process_scan(self, image_path: str, user_profile: Dict) -> Dict`**
   - **Process Flow:**
     ```
     1. OCR Extraction (target: <2s)
        ↓
     2. Keyword Extraction (parse ingredients)
        ↓
     3. RAG Retrieval (search regulations, target: <1s)
        ↓
     4. LLM Analysis (generate verdict, target: <1.5s)
        ↓
     5. Response Formatting (match api_contract.json)
     ```
   - **Output:** Complete response matching `api_contract.json` schema

**Performance Monitoring:**
```python
import time

def process_scan(self, image_path, user_profile):
    start_time = time.time()
    
    # Step 1: OCR
    ocr_start = time.time()
    ocr_result = self.ocr.extract_structured(image_path)
    ocr_time = time.time() - ocr_start
    logger.info(f"OCR: {ocr_time:.2f}s")
    
    # Step 2: RAG
    rag_start = time.time()
    regulations = self.db.search_regulations(keywords, region)
    rag_time = time.time() - rag_start
    logger.info(f"RAG: {rag_time:.2f}s")
    
    # Step 3: LLM
    llm_start = time.time()
    analysis = self.agent.generate_analysis(ocr_text, user_profile, regulations)
    llm_time = time.time() - llm_start
    logger.info(f"LLM: {llm_time:.2f}s")
    
    total_time = time.time() - start_time
    if total_time > 4.0:
        logger.warning(f"Performance target exceeded: {total_time:.2f}s")
    
    return response
```

### API Contract Compliance

**Validation Before Return:**
```python
from .serializers import AnalysisResponseSerializer

# Validate response matches schema
serializer = AnalysisResponseSerializer(data=response)
if not serializer.is_valid():
    logger.error(f"API contract violation: {serializer.errors}")
    # Fix missing fields
    response = self._enforce_contract(response)

return response
```

---

## Testing Strategy

### Test Suite Requirements

#### 1. Unit Tests (pytest)

**File:** `tests/test_ocr_service.py`
```python
def test_ocr_accuracy_on_pakistani_labels():
    """Test OCR on 20 local product images."""
    ocr = OCRService()
    
    test_images = [
        "tests/fixtures/shan_masala.jpg",
        "tests/fixtures/national_pickle.jpg",
        # ... 18 more
    ]
    
    for img_path in test_images:
        result = ocr.extract_structured(img_path)
        assert result['confidence_avg'] > 0.85
        assert "INGREDIENTS" in result['raw_text']

def test_allergen_detection_recall():
    """Ensure 100% recall on bolded allergens."""
    ocr = OCRService()
    
    # Test image with bolded "Contains: Milk, Wheat"
    result = ocr.extract_text("tests/fixtures/allergen_label.jpg")
    
    assert "Milk" in result
    assert "Wheat" in result
```

**File:** `tests/test_llm_agent.py`
```python
def test_infant_safety_guardrail():
    """Verify LLM flags sugar for infants."""
    agent = LLMAgent()
    
    ocr_text = "INGREDIENTS: Sugar, Wheat Flour"
    user_profile = {"age_months": 8}
    regulations = [{"source": "WHO", "content": "No sugar <2 years", "id": "WHO-123"}]
    
    analysis = agent.generate_analysis(ocr_text, user_profile, regulations)
    
    assert analysis['verdict'] in ['poor', 'hazardous']
    assert analysis['is_infant_safe'] == False
    assert "WHO-123" in analysis['detail']  # Must cite regulation
```

#### 2. Integration Tests

**File:** `tests/test_pipeline_integration.py`
```python
def test_full_pipeline_latency():
    """Verify end-to-end latency <4s."""
    pipeline = NutriScanPipeline()
    
    import time
    start = time.time()
    
    result = pipeline.process_scan(
        "tests/fixtures/cerelac_label.jpg",
        {"age_months": 10, "region": "PK-Punjab"}
    )
    
    latency = time.time() - start
    assert latency < 4.0, f"Pipeline took {latency:.2f}s (target: 4s)"
    assert result['status'] in ['success', 'partial_ocr_failure']

def test_api_contract_compliance():
    """Ensure response matches api_contract.json schema."""
    pipeline = NutriScanPipeline()
    
    result = pipeline.process_scan("tests/fixtures/test.jpg", {})
    
    # Required fields
    assert 'scan_id' in result
    assert 'health_impact_summary' in result
    assert 'verdict' in result['health_impact_summary']
    assert result['health_impact_summary']['verdict'] in [
        'excellent', 'good', 'fair', 'poor', 'hazardous'
    ]
```

#### 3. Accuracy Benchmarking

**Dataset:** 100 Pakistani food products with expert-labeled ground truth

**Metrics:**
- **OCR Accuracy:** Character-level accuracy on ingredient names
- **Verdict Agreement:** % agreement with expert nutritionist ratings
- **Allergen Recall:** True Positives / (True Positives + False Negatives)

**Script:** `tests/benchmark_accuracy.py`
```python
def benchmark_against_ground_truth():
    pipeline = NutriScanPipeline()
    
    ground_truth = load_json("tests/ground_truth_100_products.json")
    
    results = []
    for product in ground_truth:
        prediction = pipeline.process_scan(product['image'], product['user_profile'])
        
        results.append({
            'product_id': product['id'],
            'verdict_match': prediction['health_impact_summary']['verdict'] == product['expected_verdict'],
            'allergens_match': set(prediction['allergen_alerts']) == set(product['expected_allergens'])
        })
    
    accuracy = sum(r['verdict_match'] for r in results) / len(results)
    print(f"Verdict Accuracy: {accuracy:.2%}")
```

---

## Dependency Management

### Updated requirements.txt

Add these to existing `requirements.txt`:

```python
# OCR (already present, verify versions)
paddleocr==2.7.3
paddlepaddle==2.6.2
Pillow==10.3.0

# LLM & Agent Framework (NEW)
langchain==0.1.0
langchain-community==0.0.12
ollama==0.1.6

# Vector Database (already present)
pinecone-client==3.0.0
sentence-transformers==2.3.1
chromadb==0.4.22

# Text Processing (NEW for better parsing)
spacy==3.7.2
ftfy==6.1.3                   # Text encoding fixes for Urdu

# Utilities
python-dotenv==1.0.1          # Environment variables
requests==2.31.0
```

### Environment Variables

**File:** `.env` (create in project root)
```bash
# Pinecone Configuration
PINECONE_API_KEY=your-pinecone-api-key-here
PINECONE_ENVIRONMENT=us-east-1-aws

# Ollama Configuration
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=qwen2.5:7b-instruct-q4_K_M

# Performance Settings
ENABLE_GPU=False
OCR_CONFIDENCE_THRESHOLD=0.5
LLM_TEMPERATURE=0.3
LLM_TIMEOUT=60

# Feature Flags
USE_MOCK_FALLBACK=True        # Fallback to mock if AI services fail
ENABLE_URDU_OCR=True
ENABLE_TABLE_RECOGNITION=True
```

### Installation Instructions

**1. Install Python dependencies:**
```bash
cd /home/maimoon/Documents/Project\ Repos/NutriScan
pip install -r requirements.txt
```

**2. Download spaCy model:**
```bash
python -m spacy download en_core_web_sm
```

**3. Install and start Ollama:**
```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Pull Qwen 2.5 7B model
ollama pull qwen2.5:7b-instruct-q4_K_M

# Start Ollama server (runs in background)
ollama serve
```

**4. Initialize Pinecone:**
```bash
# Run initialization script
python scripts/init_pinecone.py

# Ingest regulatory documents
python scripts/ingest_regulations.py
```

---

## Deployment Considerations

### Phase 2 Deployment Strategy

**Development Environment:**
- All services run locally (Ollama, ChromaDB fallback)
- Use mock fallbacks when AI services unavailable
- Test with sample Pakistani product images

**Staging Environment:**
- Deploy Ollama on GPU-enabled server (optional for faster inference)
- Use Pinecone cloud (serverless tier - 1M vectors free)
- Test with 100-product benchmark dataset

**Production Environment:**
- OCR: Cloud-based for better Urdu support (consider Google Cloud Vision API in Phase 3)
- Vector DB: Pinecone production tier (auto-scaling)
- LLM: Keep Ollama local OR migrate to cloud provider (Replicate, Modal)

### Performance Optimization

**If latency >4s:**
1. **OCR Optimization:**
   - Resize images to max 1024x1024 before processing
   - Use GPU acceleration (`use_gpu=True`)
   - Cache OCR results for duplicate images

2. **LLM Optimization:**
   - Reduce context window (`num_ctx=2048` instead of 4096)
   - Use streaming responses (show partial results to user)
   - Consider smaller model (Qwen 1.8B) for simple products

3. **RAG Optimization:**
   - Cache common regulation queries
   - Reduce `top_k` from 5 to 3
   - Pre-filter by region before embedding search

### Error Monitoring

**Log all failures to track quality:**
```python
import logging

logger = logging.getLogger('nutriscan.pipeline')

# Log OCR failures
if ocr_confidence < 0.5:
    logger.warning(f"Low OCR confidence: {ocr_confidence:.2f} for image {image_path}")

# Log LLM failures
if llm_response_invalid:
    logger.error(f"LLM returned invalid JSON: {llm_response}")

# Log performance issues
if total_time > 4.0:
    logger.warning(f"Latency SLA violated: {total_time:.2f}s")
```

---

## Success Criteria

### Definition of Done (Phase 2)

- [ ] **OCR Integration Complete:**
  - PaddleOCR extracts text from 20 test images with >95% accuracy
  - Urdu text detected on bilingual labels
  - `ocr.py` passes all unit tests

- [ ] **RAG Integration Complete:**
  - Pinecone index contains 50+ regulatory documents
  - Semantic search returns relevant regulations for test queries
  - `VectorDatabase` class passes integration tests

- [ ] **LLM Integration Complete:**
  - Ollama Qwen 2.5 7B generates valid JSON responses
  - Infant safety guardrails correctly flag hazardous products
  - `LLMAgent` passes all unit tests

- [ ] **Pipeline Integration Complete:**
  - End-to-end latency <4s on average (50 test scans)
  - API response matches `api_contract.json` schema
  - All integration tests pass

- [ ] **Fallback Mechanisms Working:**
  - Mock fallbacks activate when AI services unavailable
  - No crashes or exceptions reaching API layer

### Post-Phase 2 Roadmap

**Phase 3 Enhancements (Future):**
- Replace PaddleOCR with Google Cloud Vision API (better Urdu support)
- Add spaCy NER for better ingredient parsing
- Implement CrewAI multi-agent system (specialized agents for OCR validation, allergen detection, nutrition analysis)
- Add user feedback loop (correct OCR errors, verify verdicts)
- Implement "Community Verify" feature (crowdsourced corrections)

---

## Quick Start Commands

**To begin Phase 2 implementation:**

```bash
# 1. Ensure you're on the main branch
cd /home/maimoon/Documents/Project\ Repos/NutriScan
git checkout main

# 2. Install dependencies
pip install -r requirements.txt
python -m spacy download en_core_web_sm

# 3. Setup Ollama
curl -fsSL https://ollama.com/install.sh | sh
ollama pull qwen2.5:7b-instruct-q4_K_M
ollama serve &  # Run in background

# 4. Initialize Pinecone
export PINECONE_API_KEY="your-key-here"
python scripts/init_pinecone.py
python scripts/ingest_regulations.py

# 5. Test OCR service
python -c "from analyzer.services.ocr import OCRService; ocr = OCRService(); print('OCR Ready')"

# 6. Test LLM agent
python -c "from analyzer.services.pipeline import LLMAgent; agent = LLMAgent(); print('LLM Ready')"

# 7. Run integration tests
pytest tests/ -v

# 8. Start Django server
python manage.py runserver
```

**Test the API:**
```bash
curl -X POST http://localhost:8000/api/v1/scan/ \
  -F "image=@tests/fixtures/test_label.jpg" \
  -F "user_profile={\"age_months\": 8, \"region\": \"PK-Punjab\"}"
```

---

## Questions & Support

**If you encounter issues:**

1. **OCR not detecting text?**
   - Check image quality (min 640x480, clear lighting)
   - Verify PaddleOCR installation: `python -c "from paddleocr import PaddleOCR"`
   - Try increasing confidence threshold: `OCRService(confidence_threshold=0.3)`

2. **Ollama connection error?**
   - Ensure Ollama server is running: `curl http://localhost:11434/api/tags`
   - Check model is downloaded: `ollama list`
   - Verify firewall not blocking port 11434

3. **Pinecone 401 Unauthorized?**
   - Check API key in `.env` file
   - Verify key permissions on Pinecone dashboard
   - Test connection: `python -c "from pinecone import Pinecone; Pinecone(api_key='your-key').list_indexes()"`

4. **Performance >4s?**
   - Enable GPU for OCR: `OCRService(use_gpu=True)`
   - Reduce LLM context window: `num_ctx=2048`
   - Profile with: `python -m cProfile -o profile.stats pipeline_test.py`

---

**End of Phase 2 Integration Prompt**

This document provides a comprehensive guide for transforming mock implementations into production-ready AI services. Follow the specifications exactly to ensure API contract compliance and performance targets are met.
