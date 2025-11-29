import 'package:freezed_annotation/freezed_annotation.dart';

part 'user_context.freezed.dart';
part 'user_context.g.dart';

@freezed
class UserContext with _$UserContext {
  const factory UserContext({
    @JsonKey(name: 'age_months') int? ageMonths,
    @JsonKey(name: 'dietary_restrictions') @Default([]) List<String> dietaryRestrictions,
    String? region,
  }) = _UserContext;

  factory UserContext.fromJson(Map<String, dynamic> json) =>
      _$UserContextFromJson(json);
}
