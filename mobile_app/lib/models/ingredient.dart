import 'package:freezed_annotation/freezed_annotation.dart';

part 'ingredient.freezed.dart';
part 'ingredient.g.dart';

enum IngredientCategory {
  @JsonValue('core_ingredient')
  coreIngredient,
  @JsonValue('additive')
  additive,
  @JsonValue('preservative')
  preservative,
  @JsonValue('sweetener')
  sweetener,
  @JsonValue('colorant')
  colorant,
  @JsonValue('unknown')
  unknown,
}

enum RiskLevel {
  @JsonValue('safe')
  safe,
  @JsonValue('caution')
  caution,
  @JsonValue('avoid')
  avoid,
  @JsonValue('unknown')
  unknown,
}

@freezed
class Ingredient with _$Ingredient {
  const factory Ingredient({
    required String name,
    @JsonKey(name: 'original_text') String? originalText,
    required IngredientCategory category,
    @JsonKey(name: 'risk_level') required RiskLevel riskLevel,
    String? description,
  }) = _Ingredient;

  factory Ingredient.fromJson(Map<String, dynamic> json) =>
      _$IngredientFromJson(json);
}

extension RiskLevelExtension on RiskLevel {
  /// Returns the color code for UI chips
  int get colorCode {
    switch (this) {
      case RiskLevel.safe:
        return 0xFF4CAF50; // Green
      case RiskLevel.caution:
        return 0xFFFFC107; // Amber
      case RiskLevel.avoid:
        return 0xFFF44336; // Red
      case RiskLevel.unknown:
        return 0xFF9E9E9E; // Grey
    }
  }

  String get displayName {
    switch (this) {
      case RiskLevel.safe:
        return 'Safe';
      case RiskLevel.caution:
        return 'Caution';
      case RiskLevel.avoid:
        return 'Avoid';
      case RiskLevel.unknown:
        return 'Unknown';
    }
  }
}
