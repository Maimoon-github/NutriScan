"""
NutriScan Analysis Pipeline
----------------------------
This module orchestrates the complete food label analysis workflow:
1. OCR Text Extraction
2. Ingredient Parsing & Normalization
3. Regulatory Retrieval (RAG)
4. Health Impact Analysis (Agentic LLM)
5. Response Generation

Phase 1: Returns mock data with proper structure.
Phase 2+: Will integrate real OCR, Vector DB, and LLM services.
"""

import uuid
from datetime import datetime
from typing import Dict, List, Optional


class OCRService:
    """
    Handles text extraction from food label images.
    Phase 1: Returns mock OCR data.
    Phase 2+: Integrates Google Cloud Vision or AWS Textract.
    """
    
    def extract_text(self, image_path: str) -> str:
        """
        Extract text from an uploaded image.
        
        Args:
            image_path: Path to the uploaded image file
            
        Returns:
            Raw text extracted from the image
        """
        # TODO Phase 2: Implement actual OCR
        # For now, return mock data
        return """
        INGREDIENTS: Wheat Flour, Sugar, Skimmed Milk Powder, 
        Vegetable Oil, Calcium Carbonate, Artificial Flavor (Vanillin), 
        Vitamin C, Iron.
        NUTRITION: Energy 400kcal, Sugar 18g, Fat 5g, Sodium 120mg.
        """


class VectorDatabase:
    """
    Manages regulatory knowledge base queries.
    Phase 1: Returns mock regulatory data.
    Phase 2+: Integrates Pinecone/Weaviate with real regulatory documents.
    """
    
    def search_regulations(self, keywords: List[str], region: str) -> List[Dict]:
        """
        Search for relevant food safety regulations.
        
        Args:
            keywords: List of ingredient names or health concerns
            region: Geographic region (e.g., 'PK-Punjab', 'US-FDA')
            
        Returns:
            List of relevant regulatory documents
        """
        # TODO Phase 2: Implement vector similarity search
        return [
            {
                "source": "WHO Guidelines on Complementary Feeding",
                "content": "Added sugars should not be introduced before 2 years of age.",
                "id": "WHO-2023-SUGAR",
                "url": "https://www.who.int/nutrition/guidelines"
            },
            {
                "source": "Punjab Pure Food Rules",
                "content": "Vanillin is permitted, but natural flavors are preferred for infants.",
                "id": "PFA-RULES-2018",
                "url": "https://pfa.gop.pk/"
            }
        ]


class LLMAgent:
    """
    Agentic AI for health impact analysis.
    Phase 1: Rule-based logic.
    Phase 2+: Integrates Gemini 1.5 Flash or GPT-4o-mini.
    """
    
    def generate_analysis(
        self, 
        ocr_text: str, 
        user_profile: Dict, 
        regulations: List[Dict]
    ) -> Dict:
        """
        Analyze food product health impact using regulatory context.
        
        Args:
            ocr_text: Raw text from OCR
            user_profile: User demographics and preferences
            regulations: Retrieved regulatory documents
            
        Returns:
            Structured analysis with verdict, allergens, and recommendations
        """
        # TODO Phase 2: Send to LLM with structured prompt
        
        is_infant = user_profile.get("age_months", 24) < 12
        contains_sugar = "Sugar" in ocr_text
        
        # Simple rule-based logic for Phase 1
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
                "is_halal": None,  # Cannot determine without E-code database
                "is_vegan": False,  # Contains Milk
                "is_infant_safe": not (is_infant and contains_sugar)
            }
        }


class NutriScanPipeline:
    """
    Main orchestrator for the complete analysis workflow.
    """
    
    def __init__(self):
        self.ocr = OCRService()
        self.db = VectorDatabase()
        self.agent = LLMAgent()
    
    def process_scan(self, image_path: str, user_profile: Dict) -> Dict:
        """
        Execute complete analysis pipeline.
        
        Args:
            image_path: Path to uploaded food label image
            user_profile: User context (age, region, dietary restrictions)
            
        Returns:
            Complete analysis response matching api_contract.json schema
        """
        # Step 1: Extract text via OCR
        raw_text = self.ocr.extract_text(image_path)
        
        # Step 2: Identify search terms for regulatory lookup
        # TODO Phase 2: Use NER (Named Entity Recognition) for better extraction
        search_terms = ["Sugar", "Vanillin", "Infant Nutrition"]
        
        # Step 3: Retrieve relevant regulations (RAG)
        region = user_profile.get("region", "Global")
        regulations = self.db.search_regulations(search_terms, region)
        
        # Step 4: Generate health analysis
        analysis = self.agent.generate_analysis(raw_text, user_profile, regulations)
        
        # Step 5: Construct final response
        response = {
            "scan_id": str(uuid.uuid4()),
            "timestamp": datetime.now().isoformat(),
            "status": "success",
            "user_context_used": {
                "age_months": user_profile.get("age_months"),
                "dietary_restrictions": user_profile.get("dietary_restrictions", []),
                "region": region
            },
            "ocr_raw_text": raw_text.strip(),
            "parsed_ingredients": [
                {
                    "name": "Sugar",
                    "category": "sweetener",
                    "risk_level": "avoid" if analysis['verdict'] == 'poor' else "caution",
                    "description": "Added sweetener"
                },
                {
                    "name": "Wheat Flour",
                    "category": "core_ingredient",
                    "risk_level": "safe",
                    "description": "Primary grain ingredient"
                },
                {
                    "name": "Vanillin",
                    "category": "additive",
                    "risk_level": "caution",
                    "description": "Artificial vanilla flavoring"
                }
            ],
            "nutrition_facts": {
                "serving_size": "100g",
                "calories": 400,
                "sugar_g": 18,
                "sodium_mg": 120,
                "fat_g": 5
            },
            "allergen_alerts": analysis["allergens"],
            "dietary_compliance": {
                "is_halal": analysis["dietary_flags"]["is_halal"],
                "is_vegan": analysis["dietary_flags"]["is_vegan"],
                "is_infant_safe": analysis["dietary_flags"]["is_infant_safe"],
                "flags": ["Contains Milk", "Contains Gluten"]
            },
            "health_impact_summary": {
                "verdict": analysis["verdict"],
                "short_summary": analysis["summary"],
                "detailed_analysis": analysis["detail"]
            },
            "suggestions": [
                {
                    "type": "swap",
                    "product_name": "Organic Baby Cereal (No Added Sugar)",
                    "reason": "Better for infant development without added sugars"
                }
            ],
            "sources": [
                {
                    "authority": reg["source"],
                    "doc_id": reg["id"],
                    "url": reg.get("url", "")
                }
                for reg in regulations
            ]
        }
        
        return response
