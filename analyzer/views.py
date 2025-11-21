from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from .serializers import ScanUploadSerializer, AnalysisResponseSerializer
import uuid
from datetime import datetime

class ScanAnalyzeView(APIView):
    # Parser classes allow us to handle file uploads (images)
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
        # 1. Validate Input (Image + User Data)
        input_serializer = ScanUploadSerializer(data=request.data)
        if input_serializer.is_valid():
            
            # --- LOGIC PLACEHOLDER ---
            # In Phase 2, we will call: pipeline.process_scan(image)
            # For now, we return MOCK data to test the contract.
            
            mock_response_data = {
                "scan_id": uuid.uuid4(),
                "timestamp": datetime.now(),
                "status": "success",
                "user_context_used": {
                    "age_months": 8,
                    "dietary_restrictions": [],
                    "region": "PK-Punjab"
                },
                "ocr_raw_text": "Wheat Flour, Sugar...",
                "parsed_ingredients": [
                    {"name": "Sugar", "category": "sweetener", "risk_level": "avoid", "description": "Added sugar."}
                ],
                "health_impact_summary": {
                    "verdict": "poor",
                    "short_summary": "High sugar content detected.",
                    "detailed_analysis": "Not suitable for infants."
                },
                "allergen_alerts": []
            }
            
            # 2. Validate Output (Ensure we meet the Contract)
            response_serializer = AnalysisResponseSerializer(data=mock_response_data)
            if response_serializer.is_valid():
                return Response(response_serializer.data, status=status.HTTP_200_OK)
            else:
                return Response(response_serializer.errors, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response(input_serializer.errors, status=status.HTTP_400_BAD_REQUEST)