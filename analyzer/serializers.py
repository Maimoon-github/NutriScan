from rest_framework import serializers

# --- Nested Serializers for the Response Structure ---

class UserContextSerializer(serializers.Serializer):
    age_months = serializers.IntegerField(allow_null=True)
    dietary_restrictions = serializers.ListField(child=serializers.CharField())
    region = serializers.CharField()

class IngredientSerializer(serializers.Serializer):
    name = serializers.CharField()
    original_text = serializers.CharField(required=False)
    category = serializers.ChoiceField(
        choices=["core_ingredient", "additive", "preservative", "sweetener", "colorant", "unknown"]
    )
    risk_level = serializers.ChoiceField(choices=["safe", "caution", "avoid", "unknown"])
    description = serializers.CharField(required=False)

class NutritionFactsSerializer(serializers.Serializer):
    """Nutrition information per serving"""
    serving_size = serializers.CharField(required=False)
    calories = serializers.FloatField(required=False, allow_null=True)
    sugar_g = serializers.FloatField(required=False, allow_null=True)
    sodium_mg = serializers.FloatField(required=False, allow_null=True)
    fat_g = serializers.FloatField(required=False, allow_null=True)

class DietaryComplianceSerializer(serializers.Serializer):
    """Religious and dietary restriction compliance"""
    is_halal = serializers.BooleanField(required=False, allow_null=True)
    is_vegan = serializers.BooleanField(required=False, allow_null=True)
    is_infant_safe = serializers.BooleanField(required=False, allow_null=True)
    flags = serializers.ListField(
        child=serializers.CharField(),
        required=False
    )

class HealthImpactSerializer(serializers.Serializer):
    verdict = serializers.ChoiceField(choices=["excellent", "good", "fair", "poor", "hazardous"])
    short_summary = serializers.CharField(max_length=150)
    detailed_analysis = serializers.CharField()

class AllergenAlertSerializer(serializers.Serializer):
    substance = serializers.CharField()
    severity = serializers.ChoiceField(choices=["high", "medium", "low"])
    evidence = serializers.CharField()

class SuggestionSerializer(serializers.Serializer):
    """Alternative product suggestions"""
    type = serializers.ChoiceField(choices=["swap", "usage_tip"])
    product_name = serializers.CharField(required=False)
    reason = serializers.CharField()

class SourceSerializer(serializers.Serializer):
    """Citation for regulatory sources"""
    authority = serializers.CharField()
    doc_id = serializers.CharField(required=False)
    url = serializers.URLField(required=False)

# --- Main Response Serializer ---

class AnalysisResponseSerializer(serializers.Serializer):
    """
    Mirrors api_contract.json v1.0.0 (LOCKED CONTRACT).
    Used to validate the data BEFORE sending it to the mobile app.
    All frontend-required fields are included.
    """
    # Core identification
    scan_id = serializers.UUIDField()
    timestamp = serializers.DateTimeField()
    status = serializers.ChoiceField(choices=["success", "partial_ocr_failure", "unreadable"])
    
    # User context echo
    user_context_used = UserContextSerializer()
    
    # OCR results
    ocr_raw_text = serializers.CharField()
    ocr_confidence = serializers.FloatField(min_value=0, max_value=1)
    
    # Parsed data
    parsed_ingredients = IngredientSerializer(many=True)
    nutrition_facts = NutritionFactsSerializer(required=False, allow_null=True)
    allergen_alerts = AllergenAlertSerializer(many=True)
    dietary_compliance = DietaryComplianceSerializer(required=False, allow_null=True)
    
    # Health assessment
    health_impact_summary = HealthImpactSerializer()
    
    # Frontend convenience fields (computed from health_impact_summary.verdict)
    traffic_light = serializers.ChoiceField(
        choices=["green", "yellow", "red"],
        help_text="UI traffic light: green (excellent/good), yellow (fair), red (poor/hazardous)"
    )
    why = serializers.CharField(
        help_text="Plain-language explanation combining summary and key risk factors"
    )
    
    # Citations and sources
    citations = SourceSerializer(many=True, required=False)
    sources = SourceSerializer(many=True, required=False)
    
    # Suggestions and swaps
    better_swaps = SuggestionSerializer(many=True, required=False)
    suggestions = SuggestionSerializer(many=True, required=False)
    
    # Performance and compliance
    latency_ms = serializers.IntegerField(help_text="Processing time in milliseconds")
    regulatory_flags = serializers.ListField(
        child=serializers.DictField(),
        required=False,
        help_text="Regulatory violations or warnings"
    )

# --- Request Serializer ---

class ScanUploadSerializer(serializers.Serializer):
    """
    Defines what the Mobile App sends to us.
    """
    image = serializers.ImageField()
    # Accept either 'profile' (contract) or legacy 'user_profile'
    profile = serializers.JSONField(required=False)
    user_profile = serializers.JSONField(required=False)