import 'package:freezed_annotation/freezed_annotation.dart';

part 'regulatory_flag.freezed.dart';
part 'regulatory_flag.g.dart';

enum FlagSeverity {
  @JsonValue('violation')
  violation,
  @JsonValue('warning')
  warning,
  @JsonValue('info')
  info,
}

@freezed
class RegulatoryFlag with _$RegulatoryFlag {
  const factory RegulatoryFlag({
    required String regulation,
    required FlagSeverity severity,
    required String description,
  }) = _RegulatoryFlag;

  factory RegulatoryFlag.fromJson(Map<String, dynamic> json) =>
      _$RegulatoryFlagFromJson(json);
}
