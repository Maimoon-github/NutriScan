import 'package:freezed_annotation/freezed_annotation.dart';

part 'nutrition_facts.freezed.dart';
part 'nutrition_facts.g.dart';

@freezed
class NutritionFacts with _$NutritionFacts {
  const factory NutritionFacts({
    @JsonKey(name: 'serving_size') String? servingSize,
    double? calories,
    @JsonKey(name: 'sugar_g') double? sugarG,
    @JsonKey(name: 'sodium_mg') double? sodiumMg,
    @JsonKey(name: 'fat_g') double? fatG,
  }) = _NutritionFacts;

  factory NutritionFacts.fromJson(Map<String, dynamic> json) =>
      _$NutritionFactsFromJson(json);
}
