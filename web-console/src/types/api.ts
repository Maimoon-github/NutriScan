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
  status: 'success' | 'partial_ocr_failure' | 'unreadable';
  traffic_light: 'green' | 'yellow' | 'red';
  summary: string;
  why: string; // Markdown-supported text
  citations: Citation[];
  parsed_ingredients: Ingredient[];
  allergen_alerts: AllergenAlert[];
  better_swaps: BetterSwap[];
  regulatory_flags: RegulatoryFlag[];
  ocr_confidence: number | null;
  latency_ms: number;
}

// traffic_light is a direct color string in the response

export interface Ingredient {
  name: string;
  category: string;
  risk_level: 'safe' | 'caution' | 'avoid' | 'unknown';
}

export interface AllergenAlert {
  name: string;
  severity: 'low' | 'medium' | 'high';
  source: string;
}

// Removed HealthImpactSummary to align with contract fields

// why is a Markdown string per contract

export interface Citation {
  title: string;
  source: string;
  url: string;
  excerpt: string;
}

export interface BetterSwap {
  name: string;
  brand?: string;
  notes?: string;
  price_hint?: string;
}

export interface RegulatoryFlag {
  label: string;
  jurisdiction: string;
  severity: 'low' | 'medium' | 'high';
}
