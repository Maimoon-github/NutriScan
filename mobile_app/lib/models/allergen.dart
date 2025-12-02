import 'package:freezed_annotation/freezed_annotation.dart';

part 'allergen.freezed.dart';
part 'allergen.g.dart';

enum AllergenSeverity {
  @JsonValue('high')
  high,
  @JsonValue('medium')
  medium,
  @JsonValue('low')
  low,
}

@freezed
class Allergen with _$Allergen {
  const factory Allergen({
    required String substance,
    required AllergenSeverity severity,
    required String evidence,
  }) = _Allergen;

  factory Allergen.fromJson(Map<String, dynamic> json) =>
      _$AllergenFromJson(json);
}

extension AllergenSeverityExtension on AllergenSeverity {
  /// Returns the color code for UI display
  int get colorCode {
    switch (this) {
      case AllergenSeverity.high:
        return 0xFFF44336; // Bold Red
      case AllergenSeverity.medium:
        return 0xFFFF9800; // Orange
      case AllergenSeverity.low:
        return 0xFFFFC107; // Yellow
    }
  }

  String get displayName {
    switch (this) {
      case AllergenSeverity.high:
        return 'HIGH RISK';
      case AllergenSeverity.medium:
        return 'Medium Risk';
      case AllergenSeverity.low:
        return 'Low Risk';
    }
  }
}
