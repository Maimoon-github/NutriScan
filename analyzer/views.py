from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from .serializers import ScanUploadSerializer, AnalysisResponseSerializer
from .services.pipeline import NutriScanPipeline
import uuid
from datetime import datetime

class ScanAnalyzeView(APIView):
    """
    POST /api/v1/scan/
    
    Mobile app endpoint for food label analysis.
    Accepts an image and optional user profile, returns health analysis.
    """
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
        """
        Process food label scan request.
        
        Request:
            - image: Image file of food label
            - user_profile: JSON with age_months, region, dietary_restrictions
            
        Response:
            - Complete analysis matching api_contract.json schema
        """
        # 1. Validate Input (Image + User Data)
        input_serializer = ScanUploadSerializer(data=request.data)
        
        if not input_serializer.is_valid():
            return Response(
                {
                    "error": "validation_error",
                    "details": input_serializer.errors
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 2. Extract validated data
        image_file = input_serializer.validated_data['image']
        # Prefer 'profile' field; fallback to 'user_profile'
        user_profile = input_serializer.validated_data.get('profile') or input_serializer.validated_data.get('user_profile') or {}

        # Server-side file size enforcement (10MB)
        try:
            size_bytes = getattr(image_file, 'size', None)
            if size_bytes is not None and size_bytes > 10 * 1024 * 1024:
                return Response(
                    {
                        "error": "validation_error",
                        "details": {"image": ["File size must be ≤ 10MB"]}
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
        except Exception:
            pass
        
        # 3. Process through pipeline
        try:
            pipeline = NutriScanPipeline()
            
            # Save image temporarily (Phase 2: might upload to S3)
            image_path = image_file.temporary_file_path() if hasattr(image_file, 'temporary_file_path') else None
            
            # Run analysis
            analysis_result = pipeline.process_scan(
                image_path=image_path or str(image_file),
                user_profile=user_profile
            )
            
            # 4. Validate Output (Ensure we meet the Contract)
            response_serializer = AnalysisResponseSerializer(data=analysis_result)
            
            if response_serializer.is_valid():
                return Response(response_serializer.data, status=status.HTTP_200_OK)
            else:
                # Internal error - our pipeline returned invalid data
                return Response(
                    {
                        "error": "pipeline_error",
                        "message": "Pipeline returned invalid data",
                        "details": response_serializer.errors
                    },
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        
        except Exception as e:
            # Catch any unexpected errors
            return Response(
                {
                    "error": "pipeline_error",
                    "message": str(e)
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )