# NutriScan API Contract v1.0.0 - LOCKED ✅

**Last Updated:** November 22, 2025  
**Status:** 🔒 **FROZEN** - Breaking changes require version bump  
**Endpoint:** `POST /api/v1/scan/`

---

## Overview

This document defines the **locked API contract** between the NutriScan backend and frontend applications. The contract is now frozen for frontend development. Any breaking changes will require a version increment and coordination with all consuming clients.

**Key Goals:**
- Provide consistent, predictable responses
- Enable rich UI rendering (Traffic Light, Ingredient Lists, Citations, Better Swaps)
- Support personalized analysis (age, region, dietary restrictions)
- Maintain backward compatibility

---

## Request Format

### Endpoint
```
POST /api/v1/scan/
Content-Type: multipart/form-data
```

### Request Parameters

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `image` | File | ✅ Yes | Food label image (JPEG/PNG, max 10MB) |
| `user_profile` | JSON String | ❌ No | User context for personalized analysis |

### `user_profile` Structure (JSON)

```json
{
  "age_months": 8,                           // Integer or null
  "dietary_restrictions": ["vegan", "halal"], // Array of strings
  "region": "PK-Punjab"                       // String (e.g., "PK-Punjab", "PK-Sindh")
}
```

**Example Request (cURL):**
```bash
curl -X POST http://localhost:8000/api/v1/scan/ \
  -F "image=@label.jpg" \
  -F 'user_profile={"age_months": 8, "dietary_restrictions": ["vegan"], "region": "PK-Punjab"}'
```

---

## Response Format

### Success Response (200 OK)

The response follows the schema defined in `api_contract.json`. All responses include these top-level fields:

| Field | Type | Always Present | Description |
|-------|------|----------------|-------------|
| `scan_id` | UUID string | ✅ Yes | Unique scan identifier |
| `timestamp` | ISO 8601 string | ✅ Yes | Processing timestamp |
| `status` | Enum string | ✅ Yes | `"success"`, `"partial_ocr_failure"`, or `"unreadable"` |
| `user_context_used` | Object | ✅ Yes | Echo of input user profile |
| `ocr_raw_text` | String | ✅ Yes | Raw OCR extracted text |
| `ocr_confidence` | Float (0-1) | ✅ Yes | OCR confidence score |
| `parsed_ingredients` | Array | ✅ Yes | Structured ingredient list |
| `nutrition_facts` | Object or null | ✅ Yes | Nutrition info (null if absent) |
| `allergen_alerts` | Array | ✅ Yes | Allergen warnings (empty if none) |
| `dietary_compliance` | Object or null | ✅ Yes | Dietary flags (null if not analyzed) |
| `health_impact_summary` | Object | ✅ Yes | Overall health verdict |
| `traffic_light` | Enum string | ✅ Yes | `"green"`, `"yellow"`, or `"red"` |
| `why` | String | ✅ Yes | Plain-language explanation |
| `citations` | Array | ✅ Yes | Regulatory sources with excerpts |
| `better_swaps` | Array | ✅ Yes | Product alternatives (empty if none) |
| `suggestions` | Array | ✅ Yes | All suggestions (swaps + tips) |
| `sources` | Array | ✅ Yes | RAG sources (duplicates citations) |
| `latency_ms` | Integer | ✅ Yes | Processing time in milliseconds |
| `regulatory_flags` | Array | ✅ Yes | Violations/warnings (empty if none) |

---

## Frontend-Critical Fields

### 1. Traffic Light (`traffic_light`)
**Type:** `"green" | "yellow" | "red"`  
**Purpose:** Primary UI indicator for safety at-a-glance  
**Mapping:**
- `"green"` → Verdict: `excellent`, `good`
- `"yellow"` → Verdict: `fair`
- `"red"` → Verdict: `poor`, `hazardous`

**UI Usage:**
```jsx
const colors = {
  green: '#10B981',  // Tailwind green-500
  yellow: '#F59E0B', // Tailwind yellow-500
  red: '#EF4444'     // Tailwind red-500
};
```

---

### 2. Why Explanation (`why`)
**Type:** `string`  
**Purpose:** Single-sentence explanation combining summary + key risks  
**Example:**
```
"High sugar content (28g/100g) and saturated fats. Contains gluten allergen. 
Unsuitable for infants due to sugar and potential choking hazards."
```

**UI Usage:** Display prominently below traffic light badge.

---

### 3. Parsed Ingredients (`parsed_ingredients`)
**Type:** `Array<Ingredient>`  
**Structure:**
```typescript
interface Ingredient {
  name: string;              // "Sugar", "Wheat Flour"
  original_text?: string;    // Original from label
  category: IngredientCategory;
  risk_level: RiskLevel;
  description?: string;      // Plain-language explanation
}

type IngredientCategory = 
  | "core_ingredient" 
  | "additive" 
  | "preservative" 
  | "sweetener" 
  | "colorant" 
  | "unknown";

type RiskLevel = "safe" | "caution" | "avoid" | "unknown";
```

**UI Usage:**
- Group by `category` in expandable accordions
- Color-code by `risk_level`: safe=green, caution=yellow, avoid=red, unknown=gray
- Show `description` on tap/hover

---

### 4. Allergen Alerts (`allergen_alerts`)
**Type:** `Array<AllergenAlert>`  
**Structure:**
```typescript
interface AllergenAlert {
  substance: string;        // "Milk", "Peanuts", "Wheat"
  severity: "high" | "medium" | "low";
  evidence: string;         // Quote from label
}
```

**UI Usage:**
- Display as prominent chips/badges
- Color by severity: high=red, medium=orange, low=yellow
- Show evidence in detail panel

---

### 5. Citations (`citations`)
**Type:** `Array<Citation>`  
**Structure:**
```typescript
interface Citation {
  authority: string;   // "Punjab Food Authority"
  doc_id?: string;     // "PFA-2022-BeverageStandards"
  url?: string;        // Link to source
  excerpt?: string;    // Relevant quote (max 200 chars)
}
```

**UI Usage:**
- Display in expandable "Why?" section
- Make `url` clickable
- Show `excerpt` as supporting evidence

---

### 6. Better Swaps (`better_swaps`)
**Type:** `Array<Swap>`  
**Structure:**
```typescript
interface Swap {
  product_name: string;   // "Organic Rice Crackers"
  reason: string;         // "Lower sugar, no allergens"
  price_hint?: string;    // "Similar price" or "+20% cost"
}
```

**UI Usage:**
- Show as card list with CTA buttons ("Find Similar")
- Highlight price comparison if available
- Empty array = no suggestions

---

### 7. OCR Confidence (`ocr_confidence`)
**Type:** `number` (0.0 - 1.0)  
**Purpose:** Quality indicator for OCR extraction  
**Thresholds:**
- `≥ 0.8` → High confidence (green)
- `0.5 - 0.79` → Medium confidence (yellow), status = `partial_ocr_failure`
- `< 0.5` → Low confidence (red), status = `unreadable`

**UI Usage:**
```jsx
{ocr_confidence < 0.6 && (
  <Alert type="warning">
    Image quality is low. Results may be incomplete. Please retake photo.
  </Alert>
)}
```

---

### 8. Latency (`latency_ms`)
**Type:** `integer` (milliseconds)  
**Purpose:** Performance monitoring  
**Target:** < 4000ms (4 seconds)

**UI Usage:**
- Show spinner/progress during upload
- Log to analytics for performance tracking
- Display in dev/QA builds: `Processed in 2.8s`

---

## Response Status States

### Status: `"success"`
- OCR confidence ≥ 0.6
- Ingredients parsed successfully
- Full analysis completed
- **UI:** Show full results with green success indicator

### Status: `"partial_ocr_failure"`
- OCR confidence 0.5 - 0.59
- Text extracted but incomplete/uncertain
- Analysis performed with caveats
- **UI:** Show yellow warning banner:
  > ⚠️ **OCR Quality Warning**: Text extraction was incomplete. Please verify ingredients manually.

### Status: `"unreadable"`
- OCR confidence < 0.5 OR complete OCR failure
- No ingredients parsed
- Verdict = `"hazardous"` (cannot verify safety)
- **UI:** Show red error state with retry CTA

---

## Sample Responses

### ✅ Example 1: Successful Scan (Green)

```json
{
  "scan_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "timestamp": "2025-11-22T14:30:00Z",
  "status": "success",
  "ocr_confidence": 0.92,
  "traffic_light": "green",
  "why": "All ingredients are natural and safe. Low sugar, no harmful additives.",
  "health_impact_summary": {
    "verdict": "excellent",
    "short_summary": "Clean, plant-based product with minimal processing.",
    "detailed_analysis": "Contains only 4 simple ingredients..."
  },
  "parsed_ingredients": [
    {
      "name": "Water",
      "category": "core_ingredient",
      "risk_level": "safe",
      "description": "Primary ingredient, essential for hydration."
    }
  ],
  "allergen_alerts": [],
  "better_swaps": [],
  "latency_ms": 2847
}
```

### ⚠️ Example 2: Partial OCR Failure (Yellow)

```json
{
  "status": "partial_ocr_failure",
  "ocr_confidence": 0.54,
  "traffic_light": "red",
  "why": "Very high sugar content (28g/100g). Contains gluten allergen.",
  "allergen_alerts": [
    {
      "substance": "Wheat (Gluten)",
      "severity": "high",
      "evidence": "Contains Wheat Flour"
    }
  ],
  "better_swaps": [
    {
      "product_name": "Organic Rice Crackers",
      "reason": "Lower sugar (5g/100g), no allergens",
      "price_hint": "Similar price"
    }
  ],
  "latency_ms": 3421
}
```

### ❌ Example 3: Unreadable Scan (Red)

```json
{
  "status": "unreadable",
  "ocr_confidence": 0.12,
  "traffic_light": "red",
  "why": "Cannot verify product safety. No ingredient information extracted.",
  "health_impact_summary": {
    "verdict": "hazardous",
    "short_summary": "Unable to analyze product due to poor image quality.",
    "detailed_analysis": "**Analysis Failed**: The label could not be read..."
  },
  "parsed_ingredients": [],
  "suggestions": [
    {
      "type": "usage_tip",
      "reason": "Retake photo in good lighting with ingredients list in focus."
    }
  ],
  "latency_ms": 1523
}
```

---

## Error Responses

### 400 Bad Request - Invalid Input
```json
{
  "error": "Invalid input",
  "details": {
    "image": ["This field is required."],
    "user_profile": ["Invalid JSON format."]
  }
}
```

### 500 Internal Server Error - Processing Failure
```json
{
  "error": "Processing failed",
  "message": "OCR service unavailable"
}
```

**Note:** Even on 500 errors, the backend attempts to return a valid contract-compliant response with `status: "unreadable"` when possible.

---

## Frontend Integration Checklist

### Phase 1: Core UI (MVP)
- [ ] Parse and display `traffic_light` badge
- [ ] Show `why` explanation below badge
- [ ] Render `parsed_ingredients` list with color coding
- [ ] Display `allergen_alerts` as chips
- [ ] Show `ocr_confidence` warning for low quality scans
- [ ] Handle all three `status` states (success, partial, unreadable)

### Phase 2: Rich Features
- [ ] Expandable `health_impact_summary.detailed_analysis`
- [ ] Citation links from `citations` array
- [ ] Better swaps carousel from `better_swaps`
- [ ] Nutrition facts table from `nutrition_facts`
- [ ] Dietary compliance badges (`is_halal`, `is_vegan`, `is_infant_safe`)

### Phase 3: Polish
- [ ] Loading skeleton during upload
- [ ] Retry CTA for unreadable scans
- [ ] Analytics tracking with `latency_ms`
- [ ] i18n for English/Urdu
- [ ] Accessibility (color contrast, screen reader labels)

---

## Backward Compatibility Promise

**Version 1.0.0 Guarantees:**
1. All fields marked as "Always Present" will never be removed
2. Field types will not change (string → number, etc.)
3. New optional fields may be added without version bump
4. Enum values may expand (but existing values won't change)
5. Breaking changes will increment major version (v2.0.0)

**Safe Additions (Won't Break Frontend):**
- New optional fields in response root
- New values in `suggestions.type` enum
- New categories in `ingredient.category`
- Additional metadata in `nutrition_facts`

**Breaking Changes (Require v2.0.0):**
- Renaming existing fields
- Removing required fields
- Changing data types
- Removing enum values
- Restructuring nested objects

---

## Testing Recommendations

### 1. Unit Tests (Frontend)
- Test parsing of all 3 sample responses
- Verify fallback rendering for null/empty arrays
- Check color mapping for traffic light states

### 2. Integration Tests
- Upload sample images and validate response structure
- Test low-quality image handling (OCR confidence < 0.6)
- Verify timeout handling (>4s latency)

### 3. Manual QA Scenarios
- ✅ Scan healthy product → Green light
- ⚠️ Scan junk food → Red light with swaps
- ❌ Scan blurry label → Unreadable with retry CTA
- 👶 Scan with infant profile (age_months < 12) → Strict verdict

---

## Support & Questions

**Backend Team Contact:** [Your Contact Info]  
**Contract Version:** v1.0.0  
**Last Validated:** November 22, 2025  

For questions or clarifications, reference this document and the `api_contract.json` schema file.

---

## Change Log

### v1.0.0 (2025-11-22) - Initial Lock 🔒
- Finalized schema with all frontend-required fields
- Added `traffic_light`, `why`, `citations`, `better_swaps`, `ocr_confidence`, `latency_ms`
- Created 3 sample responses (success, partial, unreadable)
- Updated serializers and pipeline to match contract
- Renamed file from `api_contrack.json` to `api_contract.json`
- **Status:** FROZEN - No breaking changes without version bump
