import 'package:freezed_annotation/freezed_annotation.dart';

part 'health_impact_summary.freezed.dart';
part 'health_impact_summary.g.dart';

enum Verdict {
  @JsonValue('excellent')
  excellent,
  @JsonValue('good')
  good,
  @JsonValue('fair')
  fair,
  @JsonValue('poor')
  poor,
  @JsonValue('hazardous')
  hazardous,
}

@freezed
class HealthImpactSummary with _$HealthImpactSummary {
  const factory HealthImpactSummary({
    required Verdict verdict,
    @JsonKey(name: 'short_summary') required String shortSummary,
    @JsonKey(name: 'detailed_analysis') required String detailedAnalysis,
  }) = _HealthImpactSummary;

  factory HealthImpactSummary.fromJson(Map<String, dynamic> json) =>
      _$HealthImpactSummaryFromJson(json);
}
