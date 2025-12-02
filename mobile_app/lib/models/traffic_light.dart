import 'package:freezed_annotation/freezed_annotation.dart';

part 'traffic_light.freezed.dart';
part 'traffic_light.g.dart';

enum TrafficLight {
  @JsonValue('green')
  green,
  @JsonValue('yellow')
  yellow,
  @JsonValue('red')
  red,
}

extension TrafficLightExtension on TrafficLight {
  String get displayName {
    switch (this) {
      case TrafficLight.green:
        return 'Safe';
      case TrafficLight.yellow:
        return 'Caution';
      case TrafficLight.red:
        return 'Avoid';
    }
  }

  /// Returns the color code for UI display
  int get colorCode {
    switch (this) {
      case TrafficLight.green:
        return 0xFF4CAF50; // Green
      case TrafficLight.yellow:
        return 0xFFFFC107; // Amber
      case TrafficLight.red:
        return 0xFFF44336; // Red
    }
  }
}
