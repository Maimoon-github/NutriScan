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
        # Get analysis from session or database
        if analysis_id == 'last':
            analysis = request.session.get('last_analysis', {})
        else:
            # TODO: Implement database query for saved analyses
            analysis = {}
        
        context = {
            'nutrition_data': analysis.get('nutrition', {}),
            'compliance_status': analysis.get('compliance', {}),
            'image_url': analysis.get('image_url', '')
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
                    "error": "Invalid input",
                    "details": input_serializer.errors
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 2. Extract validated data
        image_file = input_serializer.validated_data['image']
        user_profile = input_serializer.validated_data.get('user_profile', {})
        
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
                        "error": "Internal processing error",
                        "details": response_serializer.errors
                    },
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        
        except Exception as e:
            # Catch any unexpected errors
            return Response(
                {
                    "error": "Processing failed",
                    "message": str(e)
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )