import 'dart:io';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:freezed_annotation/freezed_annotation.dart';
import 'package:nutriscan_mobile/models/scan_response.dart';
import 'package:nutriscan_mobile/repositories/scan_repository.dart';

part 'scan_state.freezed.dart';

@freezed
class ScanState with _$ScanState {
  const factory ScanState.initial() = _Initial;
  
  const factory ScanState.loading() = _Loading;
  
  const factory ScanState.success(ScanResponse response) = _Success;
  
  const factory ScanState.error({
    required String type,
    required String message,
    required bool canRetry,
  }) = _Error;
}

/// Provider for the scan repository
final scanRepositoryProvider = Provider<ScanRepository>((ref) {
  return ScanRepository(
    baseUrl: 'http://127.0.0.1:8000', // TODO: Make this configurable
  );
});

/// Notifier for managing scan state
class ScanNotifier extends StateNotifier<ScanState> {
  final ScanRepository _repository;
  
  // Store last scan params for retry
  File? _lastImage;
  String? _lastProfileJson;

  ScanNotifier(this._repository) : super(const ScanState.initial());

  /// Upload scan with the given parameters
  Future<void> uploadScan({
    required File image,
    String? profileJson,
  }) async {
    // Store for retry
    _lastImage = image;
    _lastProfileJson = profileJson;

    // Set loading state
    state = const ScanState.loading();

    try {
      final response = await _repository.uploadScan(
        image: image,
        profileJson: profileJson,
      );

      state = ScanState.success(response);
    } on ApiException catch (e) {
      state = ScanState.error(
        type: e.type,
        message: e.message,
        canRetry: e.isRetryable,
      );
    } catch (e) {
      state = ScanState.error(
        type: 'unknown',
        message: 'An unexpected error occurred: $e',
        canRetry: true,
      );
    }
  }

  /// Retry the last scan
  /// 
  /// Returns false if there's nothing to retry or retry is not allowed
  Future<bool> retry() async {
    final currentState = state;
    
    // Only allow retry from error state
    if (currentState is! _Error) {
      return false;
    }

    // Check if retry is allowed
    if (!currentState.canRetry) {
      return false;
    }

    // Check if we have params to retry
    if (_lastImage == null) {
      return false;
    }

    await uploadScan(
      image: _lastImage!,
      profileJson: _lastProfileJson,
    );

    return true;
  }

  /// Reset to initial state
  void reset() {
    state = const ScanState.initial();
    _lastImage = null;
    _lastProfileJson = null;
  }
}

/// Provider for the scan notifier
final scanNotifierProvider =
    StateNotifierProvider<ScanNotifier, ScanState>((ref) {
  final repository = ref.watch(scanRepositoryProvider);
  return ScanNotifier(repository);
});
