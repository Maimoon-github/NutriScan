import 'package:freezed_annotation/freezed_annotation.dart';

part 'citation.freezed.dart';
part 'citation.g.dart';

@freezed
class Citation with _$Citation {
  const factory Citation({
    required String authority,
    @JsonKey(name: 'doc_id') String? docId,
    String? url,
    String? excerpt,
  }) = _Citation;

  factory Citation.fromJson(Map<String, dynamic> json) =>
      _$CitationFromJson(json);
}
