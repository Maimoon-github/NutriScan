"""
API Contract Validation Script
-------------------------------
Validates that the serializer and pipeline outputs match the api_contract.json schema.
Run this after any changes to ensure contract compliance.
"""

import json
from typing import Dict, List, Set


def load_contract_schema() -> Dict:
    """Load the JSON schema from api_contract.json."""
    with open('api_contract.json', 'r', encoding='utf-8') as f:
        return json.load(f)


def get_required_fields(schema: Dict) -> Set[str]:
    """Extract required fields from JSON schema."""
    return set(schema.get('required', []))


def get_all_properties(schema: Dict) -> Set[str]:
    """Extract all defined properties from JSON schema."""
    return set(schema.get('properties', {}).keys())


def validate_response_structure(response: Dict, schema: Dict) -> List[str]:
    """
    Validate a response dictionary against the contract schema.
    
    Returns:
        List of validation errors (empty if valid)
    """
    errors = []
    
    # Check required fields
    required_fields = get_required_fields(schema)
    response_keys = set(response.keys())
    
    missing_fields = required_fields - response_keys
    if missing_fields:
        errors.append(f"❌ Missing required fields: {', '.join(missing_fields)}")
    
    # Check for unexpected fields (warnings only)
    all_properties = get_all_properties(schema)
    unexpected_fields = response_keys - all_properties
    if unexpected_fields:
        errors.append(f"⚠️  Unexpected fields (not in schema): {', '.join(unexpected_fields)}")
    
    # Validate frontend-critical fields
    critical_fields = [
        'traffic_light', 'why', 'citations', 'better_swaps',
        'ocr_confidence', 'latency_ms', 'parsed_ingredients',
        'allergen_alerts'
    ]
    
    for field in critical_fields:
        if field not in response:
            errors.append(f"❌ Missing frontend-critical field: {field}")
    
    # Type checks for critical fields
    if 'traffic_light' in response:
        valid_colors = ['green', 'yellow', 'red']
        if response['traffic_light'] not in valid_colors:
            errors.append(f"❌ Invalid traffic_light value: {response['traffic_light']} (must be one of {valid_colors})")
    
    if 'status' in response:
        valid_statuses = ['success', 'partial_ocr_failure', 'unreadable']
        if response['status'] not in valid_statuses:
            errors.append(f"❌ Invalid status value: {response['status']} (must be one of {valid_statuses})")
    
    if 'ocr_confidence' in response:
        conf = response['ocr_confidence']
        if not isinstance(conf, (int, float)) or not (0 <= conf <= 1):
            errors.append(f"❌ Invalid ocr_confidence: {conf} (must be float between 0 and 1)")
    
    if 'parsed_ingredients' in response:
        if not isinstance(response['parsed_ingredients'], list):
            errors.append(f"❌ parsed_ingredients must be an array")
        else:
            for idx, ing in enumerate(response['parsed_ingredients']):
                if 'name' not in ing or 'risk_level' not in ing or 'category' not in ing:
                    errors.append(f"❌ Ingredient at index {idx} missing required fields (name, risk_level, category)")
    
    if 'allergen_alerts' in response:
        if not isinstance(response['allergen_alerts'], list):
            errors.append(f"❌ allergen_alerts must be an array")
    
    if 'better_swaps' in response:
        if not isinstance(response['better_swaps'], list):
            errors.append(f"❌ better_swaps must be an array")
    
    return errors


def validate_example_responses():
    """Validate all example responses from the contract."""
    print("=" * 70)
    print("API CONTRACT VALIDATION")
    print("=" * 70)
    
    schema = load_contract_schema()
    examples = schema.get('examples', [])
    
    if not examples:
        print("⚠️  No example responses found in api_contract.json")
        return
    
    print(f"\nValidating {len(examples)} example responses...\n")
    
    all_valid = True
    for example in examples:
        name = example.get('example_name', 'Unnamed Example')
        description = example.get('description', '')
        response_data = example.get('data', {})
        
        print(f"📋 {name}")
        print(f"   {description}")
        
        errors = validate_response_structure(response_data, schema)
        
        if not errors:
            print(f"   ✅ Valid - All required fields present\n")
        else:
            print(f"   ❌ Validation failed:")
            for error in errors:
                print(f"      {error}")
            print()
            all_valid = False
    
    print("=" * 70)
    if all_valid:
        print("✅ ALL EXAMPLES VALID - Contract is consistent!")
    else:
        print("❌ VALIDATION FAILED - Fix errors above")
    print("=" * 70)


def check_serializer_alignment():
    """Check if serializers.py defines all required fields."""
    print("\n" + "=" * 70)
    print("SERIALIZER ALIGNMENT CHECK")
    print("=" * 70)
    
    try:
        from analyzer.serializers import AnalysisResponseSerializer
        
        serializer_fields = AnalysisResponseSerializer().fields.keys()
        schema = load_contract_schema()
        schema_properties = get_all_properties(schema)
        
        print(f"\nSerializer fields: {len(serializer_fields)}")
        print(f"Schema properties: {len(schema_properties)}")
        
        missing_in_serializer = schema_properties - set(serializer_fields)
        extra_in_serializer = set(serializer_fields) - schema_properties
        
        if missing_in_serializer:
            print(f"\n⚠️  Fields in schema but NOT in serializer:")
            for field in missing_in_serializer:
                print(f"   - {field}")
        
        if extra_in_serializer:
            print(f"\n⚠️  Fields in serializer but NOT in schema:")
            for field in extra_in_serializer:
                print(f"   - {field}")
        
        if not missing_in_serializer and not extra_in_serializer:
            print("\n✅ Perfect alignment - Serializer matches schema exactly!")
        
        print("=" * 70)
        
    except ImportError as e:
        print(f"\n❌ Could not import serializer: {e}")
        print("Make sure Django is properly configured.")


if __name__ == "__main__":
    # Validate example responses
    validate_example_responses()
    
    # Check serializer alignment (requires Django setup)
    try:
        import django
        import os
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nutriscan.settings')
        django.setup()
        check_serializer_alignment()
    except Exception as e:
        print(f"\n⚠️  Skipping serializer check (Django not configured): {e}")
