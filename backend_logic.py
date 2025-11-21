import json
import datetime
from typing import List, Dict, Optional

# Mocking external libraries for the sake of this architectural demo
class OCRService:
    def extract_text(self, image_bytes) -> str:
        # In prod: Call Google Cloud Vision or AWS Textract
        # Simulating a scan of an infant cereal box
        return """
        INGREDIENTS: Wheat Flour, Sugar, Skimmed Milk Powder, 
        Vegetable Oil, Calcium Carbonate, Artificial Flavor (Vanillin), 
        Vitamin C, Iron.
        NUTRITION: Energy 400kcal, Sugar 18g, Fat 5g.
        """

class VectorDatabase:
    def search_regulations(self, keywords: List[str], region: str) -> List[Dict]:
        # In prod: Query Pinecone/Weaviate for regulations
        return [
            {
                "source": "WHO Guidelines on Complementary Feeding",
                "content": "Added sugars should not be introduced before 2 years of age.",
                "id": "WHO-2023-SUGAR"
            },
            {
                "source": "Punjab Pure Food Rules",
                "content": "Vanillin is permitted, but natural flavors are preferred for infants.",
                "id": "PFA-RULES-2018"
            }
        ]

class LLMAgent:
    def generate_analysis(self, ocr_text: str, user_profile: Dict, regulations: List[Dict]) -> Dict:
        # In prod: This is the prompt sent to GPT-4o or Gemini 1.5 Pro
        
        # Simulating the LLM's reasoning process:
        # 1. User is an infant (8 months).
        # 2. Product contains Sugar. WHO says NO. -> Verdict: POOR.
        # 3. Product contains Wheat/Milk. -> Allergen Alert.
        
        is_infant = user_profile.get("age_months", 24) < 12
        
        health_verdict = "poor" if is_infant and "Sugar" in ocr_text else "good"
        
        return {
            "verdict": health_verdict,
            "summary": "Not recommended for your 8-month-old due to added sugar.",
            "detail": "This product lists Sugar as the second ingredient. WHO guidelines recommend zero added sugar for infants under 2 years to prevent metabolic issues and taste preferences for sweets.",
            "allergens": [
                {"substance": "Wheat", "severity": "high", "evidence": "Ingredient: Wheat Flour"},
                {"substance": "Milk", "severity": "high", "evidence": "Ingredient: Skimmed Milk Powder"}
            ]
        }

class NutriScanPipeline:
    def __init__(self):
        self.ocr = OCRService()
        self.db = VectorDatabase()
        self.agent = LLMAgent()

    def process_scan(self, image_bytes, user_profile: Dict) -> Dict:
        # 1. Extract Text
        raw_text = self.ocr.extract_text(image_bytes)
        
        # 2. Agentic Planning (Identify key terms to research)
        # Simplified: Just taking text tokens
        search_terms = ["Sugar", "Vanillin", "Infant Nutrition"]
        
        # 3. Retrieval (RAG)
        regulations = self.db.search_regulations(search_terms, user_profile.get("region", "Global"))
        
        # 4. Generation
        analysis = self.agent.generate_analysis(raw_text, user_profile, regulations)
        
        # 5. Construct Final JSON
        response = {
            "scan_id": "scan_12345_abcde",
            "timestamp": datetime.datetime.now().isoformat(),
            "status": "success",
            "ocr_raw_text": raw_text.strip(),
            "parsed_ingredients": [
                {"name": "Sugar", "category": "sweetener", "risk_level": "avoid" if analysis['verdict'] == 'poor' else "caution"},
                {"name": "Wheat Flour", "category": "core_ingredient", "risk_level": "safe"}
            ],
            "health_impact_summary": {
                "verdict": analysis["verdict"],
                "short_summary": analysis["summary"],
                "detailed_analysis": analysis["detail"]
            },
            "allergen_alerts": analysis["allergens"],
            "sources": [
                {"authority": reg["source"], "doc_id": reg["id"]} for reg in regulations
            ]
        }
        return response

# --- Execution Example ---
if __name__ == "__main__":
    # Simulation of a user request
    pipeline = NutriScanPipeline()
    
    mock_image = b"fake_image_data"
    user_profile = {
        "age_months": 8,
        "weight_kg": 8.5,
        "region": "PK-Punjab",
        "allergies": []
    }
    
    result = pipeline.process_scan(mock_image, user_profile)
    print(json.dumps(result, indent=2))