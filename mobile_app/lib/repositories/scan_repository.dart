import 'dart:io';
import 'package:dio/dio.dart';
import 'package:nutriscan_mobile/models/scan_response.dart';

/// Custom exception for API errors
class ApiException implements Exception {
  final String message;
  final String type;
  final int? statusCode;

  ApiException({
    required this.message,
    required this.type,
    this.statusCode,
  });

  @override
  String toString() => message;

  /// Whether this error is retryable
  bool get isRetryable {
    // Network errors and 500s are retryable
    if (type == 'network' || statusCode == 500) {
      return true;
    }
    // 400 validation errors are not retryable
    return false;
  }
}

class ScanRepository {
  final Dio _dio;
  final String baseUrl;

  ScanRepository({
    required this.baseUrl,
    Dio? dio,
  }) : _dio = dio ?? Dio() {
    _configureDio();
  }

  void _configureDio() {
    _dio.options.baseUrl = baseUrl;
    _dio.options.connectTimeout = const Duration(seconds: 30);
    _dio.options.receiveTimeout = const Duration(seconds: 30);
    _dio.options.headers = {
      'Accept': 'application/json',
    };
  }

  /// Upload image for scanning
  /// 
  /// Throws [ApiException] with appropriate error type:
  /// - 'network': Connection issues (retryable)
  /// - 'validation': Bad request - 400 (not retryable)
  /// - 'server': Server error - 500 (retryable)
  /// - 'unknown': Other errors
  Future<ScanResponse> uploadScan({
    required File image,
    String? profileJson,
  }) async {
    try {
      // Prepare multipart form data
      final formData = FormData.fromMap({
        'image': await MultipartFile.fromFile(
          image.path,
          filename: 'scan_image.jpg',
        ),
        if (profileJson != null && profileJson.isNotEmpty)
          'user_profile': profileJson,
      });

      // Make the API call
      final response = await _dio.post(
        '/api/v1/scan/',
        data: formData,
      );

      // Parse successful response
      if (response.statusCode == 200 || response.statusCode == 201) {
        return ScanResponse.fromJson(response.data as Map<String, dynamic>);
      }

      // Unexpected success status code
      throw ApiException(
        message: 'Unexpected response status: ${response.statusCode}',
        type: 'unknown',
        statusCode: response.statusCode,
      );
    } on DioException catch (e) {
      throw _handleDioException(e);
    } catch (e) {
      throw ApiException(
        message: 'Unexpected error: $e',
        type: 'unknown',
      );
    }
  }

  /// Handle Dio exceptions and convert to ApiException
  ApiException _handleDioException(DioException e) {
    switch (e.type) {
      case DioExceptionType.connectionTimeout:
      case DioExceptionType.sendTimeout:
      case DioExceptionType.receiveTimeout:
        return ApiException(
          message: 'Connection timeout. Please check your internet connection.',
          type: 'network',
        );

      case DioExceptionType.connectionError:
        return ApiException(
          message: 'Unable to connect to server. Please check your internet connection.',
          type: 'network',
        );

      case DioExceptionType.badResponse:
        final statusCode = e.response?.statusCode;
        final responseData = e.response?.data;

        if (statusCode == 400) {
          // Parse backend validation error
          String errorMessage = 'Invalid request';
          
          if (responseData is Map<String, dynamic>) {
            if (responseData.containsKey('error')) {
              errorMessage = responseData['error'].toString();
            } else if (responseData.containsKey('message')) {
              errorMessage = responseData['message'].toString();
            } else if (responseData.containsKey('detail')) {
              errorMessage = responseData['detail'].toString();
            }
          }

          return ApiException(
            message: errorMessage,
            type: 'validation',
            statusCode: 400,
          );
        }

        if (statusCode != null && statusCode >= 500) {
          // Server error
          String errorMessage = 'Server error. Please try again later.';
          
          if (responseData is Map<String, dynamic> &&
              responseData.containsKey('error')) {
            errorMessage = responseData['error'].toString();
          }

          return ApiException(
            message: errorMessage,
            type: 'server',
            statusCode: statusCode,
          );
        }

        return ApiException(
          message: 'Request failed with status: $statusCode',
          type: 'unknown',
          statusCode: statusCode,
        );

      case DioExceptionType.cancel:
        return ApiException(
          message: 'Request was cancelled',
          type: 'unknown',
        );

      case DioExceptionType.badCertificate:
        return ApiException(
          message: 'Security error: Invalid certificate',
          type: 'network',
        );

      case DioExceptionType.unknown:
      default:
        return ApiException(
          message: 'An unexpected error occurred: ${e.message}',
          type: 'unknown',
        );
    }
  }
}
