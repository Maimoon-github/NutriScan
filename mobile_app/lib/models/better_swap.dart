import 'package:freezed_annotation/freezed_annotation.dart';

part 'better_swap.freezed.dart';
part 'better_swap.g.dart';

@freezed
class BetterSwap with _$BetterSwap {
  const factory BetterSwap({
    @JsonKey(name: 'product_name') required String productName,
    required String reason,
    @JsonKey(name: 'price_hint') String? priceHint,
  }) = _BetterSwap;

  factory BetterSwap.fromJson(Map<String, dynamic> json) =>
      _$BetterSwapFromJson(json);
}
