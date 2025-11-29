// API Contract Types - Generated from api_contract.json
export interface ScanRequest {
  image: File;
  profile?: UserProfile;
}

export interface UserProfile {
  age_months?: number | null;
  region?: string;
  dietary_restrictions?: string[];
}

export interface ScanResponse {
  scan_id: string;
  timestamp: string;
  status: 'success' | 'partial' | 'failed';
  user_context_used: boolean;
  traffic_light: TrafficLight;
  ocr_raw_text: string | null;
  ocr_confidence: number | null;
  parsed_ingredients: Ingredient[];
  allergen_alerts: AllergenAlert[];
  health_impact_summary: HealthImpactSummary;
  why: WhyExplanation;
  citations: Citation[];
  better_swaps: BetterSwap[];
  latency_ms: number;
}

export interface TrafficLight {
  // Contract uses direct traffic_light color string
  // UI derives label/confidence if needed from other fields
  // Keeping minimal per contract
  // If your contract includes structured object, adjust here.
  status: 'green' | 'yellow' | 'red';
  label: string;
  confidence: number;
}

export interface Ingredient {
  name: string;
  category: string;
  risk_level: 'safe' | 'moderate' | 'high';
}

export interface AllergenAlert {
  allergen: string;
  severity: 'low' | 'medium' | 'high';
  source: string;
}

export interface HealthImpactSummary {
  verdict: string;
  short_summary: string;
  detailed_analysis: string;
  is_halal?: boolean | null;
  is_vegan?: boolean | null;
  is_infant_safe?: boolean | null;
}

export interface WhyExplanation {
  summary: string;
  details: string[];
  regulatory_basis: string;
}

export interface Citation {
  source: string;
  title: string;
  relevance: string;
}

export interface BetterSwap {
  product_name: string;
  reason: string;
  health_score: number;
}
