import 'package:flutter/material.dart';
import 'package:nutriscan_mobile/models/allergen.dart';

/// Widget displaying allergen alerts
class AllergenAlerts extends StatelessWidget {
  final List<Allergen> allergens;

  const AllergenAlerts({
    super.key,
    required this.allergens,
  });

  @override
  Widget build(BuildContext context) {
    if (allergens.isEmpty) {
      return const SizedBox.shrink();
    }

    return Card(
      margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      color: Colors.red[50],
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(
                  Icons.warning_amber_rounded,
                  color: Colors.red[700],
                  size: 24,
                ),
                const SizedBox(width: 8),
                Text(
                  'Allergen Alerts',
                  style: Theme.of(context).textTheme.titleMedium?.copyWith(
                        fontWeight: FontWeight.bold,
                        color: Colors.red[700],
                      ),
                ),
              ],
            ),
            const SizedBox(height: 12),
            ...allergens.map((allergen) => _buildAllergenItem(context, allergen)),
          ],
        ),
      ),
    );
  }

  Widget _buildAllergenItem(BuildContext context, Allergen allergen) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 8),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
            decoration: BoxDecoration(
              color: Color(allergen.severity.colorCode),
              borderRadius: BorderRadius.circular(4),
            ),
            child: Text(
              allergen.severity.displayName,
              style: const TextStyle(
                color: Colors.white,
                fontSize: 11,
                fontWeight: FontWeight.bold,
              ),
            ),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  allergen.substance,
                  style: const TextStyle(
                    fontWeight: FontWeight.bold,
                    fontSize: 14,
                  ),
                ),
                const SizedBox(height: 2),
                Text(
                  'Evidence: "${allergen.evidence}"',
                  style: TextStyle(
                    fontSize: 12,
                    color: Colors.grey[700],
                    fontStyle: FontStyle.italic,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
