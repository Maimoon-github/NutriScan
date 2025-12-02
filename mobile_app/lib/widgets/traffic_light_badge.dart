import 'package:flutter/material.dart';
import 'package:nutriscan_mobile/models/traffic_light.dart' as model;

/// Widget displaying traffic light status badge
class TrafficLightBadge extends StatelessWidget {
  final model.TrafficLight trafficLight;
  final double size;

  const TrafficLightBadge({
    super.key,
    required this.trafficLight,
    this.size = 80.0,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      width: size,
      height: size,
      decoration: BoxDecoration(
        color: Color(trafficLight.colorCode),
        shape: BoxShape.circle,
        boxShadow: [
          BoxShadow(
            color: Color(trafficLight.colorCode).withOpacity(0.4),
            blurRadius: 12,
            spreadRadius: 2,
          ),
        ],
      ),
      child: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(
              _getIcon(),
              color: Colors.white,
              size: size * 0.4,
            ),
            SizedBox(height: 4),
            Text(
              trafficLight.displayName,
              style: TextStyle(
                color: Colors.white,
                fontSize: size * 0.15,
                fontWeight: FontWeight.bold,
              ),
            ),
          ],
        ),
      ),
    );
  }

  IconData _getIcon() {
    switch (trafficLight) {
      case model.TrafficLight.green:
        return Icons.check_circle;
      case model.TrafficLight.yellow:
        return Icons.warning;
      case model.TrafficLight.red:
        return Icons.cancel;
    }
  }
}
