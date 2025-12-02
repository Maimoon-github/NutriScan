import 'package:freezed_annotation/freezed_annotation.dart';
import 'package:nutriscan_mobile/models/allergen.dart';
import 'package:nutriscan_mobile/models/better_swap.dart';
import 'package:nutriscan_mobile/models/citation.dart';
import 'package:nutriscan_mobile/models/health_impact_summary.dart';
import 'package:nutriscan_mobile/models/ingredient.dart';
import 'package:nutriscan_mobile/models/nutrition_facts.dart';
import 'package:nutriscan_mobile/models/regulatory_flag.dart';
import 'package:nutriscan_mobile/models/traffic_light.dart';
import 'package:nutriscan_mobile/models/user_context.dart';

part 'scan_response.freezed.dart';
part 'scan_response.g.dart';

enum ScanStatus {
  @JsonValue('success')
  success,
  @JsonValue('partial_ocr_failure')
  partialOcrFailure,
  @JsonValue('unreadable')
  unreadable,
}

@freezed
class ScanResponse with _$ScanResponse {
  const factory ScanResponse({
    @JsonKey(name: 'scan_id') required String scanId,
    required String timestamp,
    required ScanStatus status,
    @JsonKey(name: 'user_context_used') required UserContext userContextUsed,
    @JsonKey(name: 'ocr_raw_text') required String ocrRawText,
    @JsonKey(name: 'ocr_confidence') double? ocrConfidence,
    @JsonKey(name: 'parsed_ingredients') required List<Ingredient> parsedIngredients,
    @JsonKey(name: 'nutrition_facts') NutritionFacts? nutritionFacts,
    @JsonKey(name: 'allergen_alerts') required List<Allergen> allergenAlerts,
    @JsonKey(name: 'health_impact_summary') required HealthImpactSummary healthImpactSummary,
    @JsonKey(name: 'traffic_light') required TrafficLight trafficLight,
    required String why,
    @Default([]) List<Citation> citations,
    @JsonKey(name: 'better_swaps') @Default([]) List<BetterSwap> betterSwaps,
    @Default([]) List<Citation> sources,
    @JsonKey(name: 'latency_ms') int? latencyMs,
    @JsonKey(name: 'regulatory_flags') @Default([]) List<RegulatoryFlag> regulatoryFlags,
  }) = _ScanResponse;

  factory ScanResponse.fromJson(Map<String, dynamic> json) =>
      _$ScanResponseFromJson(json);
}

extension ScanStatusExtension on ScanStatus {
  bool get isSuccess => this == ScanStatus.success;
  bool get isPartialFailure => this == ScanStatus.partialOcrFailure;
  bool get isUnreadable => this == ScanStatus.unreadable;
  
  String get displayMessage {
    switch (this) {
      case ScanStatus.success:
        return 'Analysis completed successfully';
      case ScanStatus.partialOcrFailure:
        return '⚠️ Text extraction was incomplete. Please verify ingredients manually.';
      case ScanStatus.unreadable:
        return '❌ Unable to read label. Please retake the photo with better lighting.';
    }
  }
}
