# NutriScan


Product Specification: NutriScan AI (Project SafeBite)

Version: 1.0

Status: Draft

Target Market: Pakistan (Initial - Infant Food Focus), Global (Scale)

Core Technology: Vision OCR, RAG, Agentic AI

1. Executive Summary

NutriScan AI is a mobile application that empowers parents and health-conscious individuals to decode complex food labels instantly. Unlike competitors that rely on barcode databases (which are often incomplete in developing markets like Pakistan), NutriScan uses visual AI to read the ingredient list and nutrition table directly. It uses Agentic RAG (Retrieval Augmented Generation) to cross-reference scanned text against local food safety laws (e.g., Punjab Food Authority) and global standards (WHO/FDA) to provide personalized health insights, specifically prioritizing infant safety.

2. User Personas

Primary: The Vigilant Parent (Ayesha)

Profile: 28 years old, lives in Lahore. Mother of a 9-month-old.

Pain Point: Confused by technical names on imported and local cereals. Worried about hidden sugars and "nature-identical" flavors banned for infants.

Goal: "Is this safe for my baby right now?"

Secondary: The Metabolic Manager (Bilal)

Profile: 45 years old, Pre-diabetic.

Pain Point: Small font sizes on labels; misleading "No Added Sugar" claims that hide Maltodextrin.

Goal: Quickly calculate the Glycemic Load of a snack.

3. Functional Requirements

3.1. The Scan Flow (No Barcode Dependency)

Camera Interface: Real-time viewfinder with "Text Stabilization" overlay.

Smart Capture: Auto-shutter when text is in focus and legible.

Layout Analysis: AI distinguishes between "Marketing Fluff" (front of pack) and "Structural Data" (Ingredients List / Nutrition Table).

Multi-Language Support: * Phase 1: English & Urdu (Nastaliq & Naskh scripts).

Phase 2: Arabic, French, Spanish.

3.2. The Analysis Engine (Agentic RAG)

Ingredient Parsing: Splits comma-separated lists, handles OCR errors (e.g., reading "Slat" as "Salt"), and resolves synonyms (e.g., "E300" $\to$ "Vitamin C").

Infant Guardrails: If user_profile.is_infant == true, the agent triggers a stricter rule set (zero tolerance for honey, added salt, specific preservatives).

Dietary Flags: * Halal/Haram Check: Cross-references E-codes against Halal certification databases.

Allergens: Highlights bolded text and infers hidden allergens (e.g., "Casein" $\to$ "Milk").

3.3. The Output Interface

The "Traffic Light": Green (Safe), Yellow (Caution), Red (Avoid).

"Why" Explainer: Clicking a Red flag opens a citation (e.g., "Contains Sodium Benzoate: Not recommended for infants under 2 years per WHO guidelines").

Better Swaps: "This porridge has 15g sugar. Try [Brand B] which has 0g sugar."

4. Technical Architecture

4.1. High-Level Stack

Mobile App: Flutter (for rapid Android/iOS deployment).

Edge AI: Google ML Kit (Text Recognition v2) for instantaneous text bounding box detection.

Cloud Backend: Python (FastAPI).

LLM/Agent: Gemini 1.5 Flash (cost-effective, high context window) or GPT-4o-mini.

Vector DB: Pinecone or Weaviate (stores Food Regulations & Clinical Guidelines).

4.2. Data Pipeline

Ingestion: Image uploaded $\to$ Cloud OCR (Amazon Textract or Google Vision API for superior Urdu support).

Normalization: Raw text cleaned via fuzzy matching against an Ingredient_Ontology.

Retrieval (RAG): * Query: "Health impact of [Ingredient List] for [Age Group] in [Region]".

Context Fetched: Local verified regulatory docs, toxicity reports.

Synthesis: Agentic LLM constructs the JSON response with citations.

5. Data Sources & Compliance

5.1. Authoritative Sources (Pakistan Context)

PSQCA (Pakistan Standards and Quality Control Authority): Standards for packaged goods.

PFA (Punjab Food Authority): Banned additive lists.

Import Regulations: Lists of allowed/banned E-numbers for imported goods.

5.2. Global Standards

Codex Alimentarius (FAO/WHO): The baseline for international food safety.

Open Food Facts: For supplemental product metadata.

5.3. Compliance & Liability

Disclaimers: "Information is for educational purposes only. Consult a pediatrician."

Infant Data Privacy: Strict adherence to COPPA/GDPR. Infant profiles are stored locally on-device where possible; only anonymous age/weight data is sent to the cloud.

6. KPIs & Success Metrics

OCR Extraction Fidelity:

Target: 95% accuracy on ingredient names (ignoring punctuation).

Critical: 100% detection of bolded allergen warnings.

Safety Critical Recall:

Target: 0% False Negatives for major allergens (Peanuts, Milk, Gluten) in high-confidence scans.

Latency:

Target: < 4 seconds from "Capture" to "First Paint" of results.

Regulatory Alignment:

Metric: % of health claims backed by a specific database citation ID.

7. Implementation Roadmap

Phase 1: Alpha (Internal & Friends/Family) - Month 1-2

Manual collection of 500 Pakistani product images (Cereals, Formulas, Biscuits).

Basic OCR + Hardcoded Rules Engine (Python scripts).

UI: Simple text dump + "Safe/Unsafe" toggle.

Phase 2: Beta (Pakistan Launch) - Month 3-4

Integrate Gemini/LLM for RAG explanations.

Urdu OCR optimization.

App Store release restricted to Pakistan region.

Phase 3: Global Scale - Month 6+

Expand RAG database to FDA (USA) and EFSA (Europe) regulations.

"Community Verify": Users can correct OCR errors to earn "Health Points".