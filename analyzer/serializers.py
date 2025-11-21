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

class HealthImpactSerializer(serializers.Serializer):
    verdict = serializers.ChoiceField(choices=["excellent", "good", "fair", "poor", "hazardous"])
    short_summary = serializers.CharField(max_length=150)
    detailed_analysis = serializers.CharField()

class AllergenAlertSerializer(serializers.Serializer):
    substance = serializers.CharField()
    severity = serializers.ChoiceField(choices=["high", "medium", "low"])
    evidence = serializers.CharField()

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
    health_impact_summary = HealthImpactSerializer()
    allergen_alerts = AllergenAlertSerializer(many=True)
    # Note: Simplified for brevity, but 'nutrition_facts' and 'sources' would be added here similarly.

# --- Request Serializer ---

class ScanUploadSerializer(serializers.Serializer):
    """
    Defines what the Mobile App sends to us.
    """
    image = serializers.ImageField()
    user_profile = serializers.JSONField(required=False)