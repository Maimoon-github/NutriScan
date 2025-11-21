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
    Mirrors api_contrack.json.
    Used to validate the data BEFORE sending it to the mobile app.
    """
    scan_id = serializers.UUIDField()
    timestamp = serializers.DateTimeField()
    status = serializers.ChoiceField(choices=["success", "partial_ocr_failure", "unreadable"])
    user_context_used = UserContextSerializer()
    ocr_raw_text = serializers.CharField()
    parsed_ingredients = IngredientSerializer(many=True)
    nutrition_facts = NutritionFactsSerializer(required=False)
    allergen_alerts = AllergenAlertSerializer(many=True)
    dietary_compliance = DietaryComplianceSerializer(required=False)
    health_impact_summary = HealthImpactSerializer()
    suggestions = SuggestionSerializer(many=True, required=False)
    sources = SourceSerializer(many=True, required=False)

# --- Request Serializer ---

class ScanUploadSerializer(serializers.Serializer):
    """
    Defines what the Mobile App sends to us.
    """
    image = serializers.ImageField()
    user_profile = serializers.JSONField(required=False)