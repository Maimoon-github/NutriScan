from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.views.generic import ListView, DetailView
from django.contrib.messages import success, error
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from .serializers import ScanUploadSerializer, AnalysisResponseSerializer
from .services.pipeline import NutriScanPipeline
import uuid
from datetime import datetime


# ============================================================================
# FRONTEND VIEWS (for web UI)
# ============================================================================

class HomeView(View):
    """Home page view for the simple frontend"""
    
    def get(self, request):
        return render(request, 'analyzer/home.html')


class UploadView(View):
    """Upload nutrition label image view"""
    
    def get(self, request):
        return render(request, 'analyzer/upload.html')
    
    def post(self, request):
        # Handle file upload
        if 'image' not in request.FILES:
            error(request, 'Please select an image to upload')
            return redirect('analyzer:upload')
        
        try:
            image_file = request.FILES['image']
            description = request.POST.get('description', '')
            
            # Process through pipeline
            pipeline = NutriScanPipeline()
            analysis_result = pipeline.process_scan(
                image_path=image_file.temporary_file_path() if hasattr(image_file, 'temporary_file_path') else str(image_file),
                user_profile={}
            )
            
            # Store result in session and redirect to results
            request.session['last_analysis'] = analysis_result
            success(request, 'Image analyzed successfully!')
            return redirect('analyzer:results', analysis_id='last')
            
        except Exception as e:
            error(request, f'Error processing image: {str(e)}')
            return redirect('analyzer:upload')


class ResultsView(View):
    """Display analysis results"""
    
    def get(self, request, analysis_id):
        import json
        
        # Get analysis from session or database
        if analysis_id == 'last':
            analysis = request.session.get('last_analysis', {})
        else:
            # TODO: Implement database query for saved analyses
            analysis = {}
        
        # Prepare context with all response fields from the API
        context = {
            # Full response for debugging
            'full_response_json': json.dumps(analysis),
            
            # Core identification
            'scan_id': analysis.get('scan_id', ''),
            'timestamp': analysis.get('timestamp', ''),
            'status': analysis.get('status', 'unknown'),
            'latency_ms': analysis.get('latency_ms', 0),
            
            # Health assessment
            'traffic_light': analysis.get('traffic_light', 'yellow'),
            'why': analysis.get('why', ''),
            'health_impact_summary': analysis.get('health_impact_summary', {}),
            
            # OCR results
            'ocr_raw_text': analysis.get('ocr_raw_text', ''),
            'ocr_confidence': analysis.get('ocr_confidence', 0),
            
            # Parsed data
            'parsed_ingredients': analysis.get('parsed_ingredients', []),
            'nutrition_facts': analysis.get('nutrition_facts', {}),
            'allergen_alerts': analysis.get('allergen_alerts', []),
            'dietary_compliance': analysis.get('dietary_compliance', {}),
            
            # Citations and sources
            'citations': analysis.get('citations', []),
            'sources': analysis.get('sources', []),
            
            # Suggestions and swaps
            'better_swaps': analysis.get('better_swaps', []),
            'suggestions': analysis.get('suggestions', []),
            
            # Regulatory info
            'regulatory_flags': analysis.get('regulatory_flags', []),
            
            # User context
            'user_context_used': analysis.get('user_context_used', {}),
        }
        
        return render(request, 'analyzer/results.html', context)


class HistoryView(ListView):
    """Display user's analysis history"""
    
    template_name = 'analyzer/history.html'
    context_object_name = 'analyses'
    paginate_by = 20
    
    def get_queryset(self):
        # TODO: Implement database query for user's analyses
        return []
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


# ============================================================================
# API VIEWS (REST API for mobile/external clients)
# ============================================================================

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
            
            # Get image path - handle both temporary files and in-memory uploads
            if hasattr(image_file, 'temporary_file_path'):
                # File is large enough to be stored on disk
                image_path = image_file.temporary_file_path()
            else:
                # File is in memory - save it temporarily
                import tempfile
                import os
                
                # Create temp file with proper extension
                file_extension = os.path.splitext(image_file.name)[1] or '.jpg'
                temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=file_extension)
                
                # Write uploaded file to temp location
                for chunk in image_file.chunks():
                    temp_file.write(chunk)
                temp_file.close()
                
                image_path = temp_file.name
            
            # Run analysis
            analysis_result = pipeline.process_scan(
                image_path=image_path,
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
