import 'package:flutter/material.dart';
import 'package:nutriscan_mobile/models/ingredient.dart';

/// List of ingredient chips color-coded by risk level
class IngredientList extends StatelessWidget {
  final List<Ingredient> ingredients;

  const IngredientList({
    super.key,
    required this.ingredients,
  });

  @override
  Widget build(BuildContext context) {
    if (ingredients.isEmpty) {
      return Card(
        margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Center(
            child: Text(
              'No ingredients detected',
              style: TextStyle(color: Colors.grey[600]),
            ),
          ),
        ),
      );
    }

    return Card(
      margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Ingredients',
              style: Theme.of(context).textTheme.titleMedium?.copyWith(
                    fontWeight: FontWeight.bold,
                  ),
            ),
            const SizedBox(height: 12),
            Wrap(
              spacing: 8,
              runSpacing: 8,
              children: ingredients.map((ingredient) {
                return _buildIngredientChip(context, ingredient);
              }).toList(),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildIngredientChip(BuildContext context, Ingredient ingredient) {
    final riskColor = Color(ingredient.riskLevel.colorCode);
    
    return InkWell(
      onTap: () {
        _showIngredientDetails(context, ingredient);
      },
      child: Chip(
        label: Text(
          ingredient.name,
          style: TextStyle(
            color: _getTextColor(ingredient.riskLevel),
            fontWeight: FontWeight.w500,
          ),
        ),
        backgroundColor: riskColor.withOpacity(0.15),
        side: BorderSide(
          color: riskColor,
          width: 1.5,
        ),
        avatar: Icon(
          _getRiskIcon(ingredient.riskLevel),
          size: 16,
          color: riskColor,
        ),
      ),
    );
  }

  Color _getTextColor(RiskLevel riskLevel) {
    switch (riskLevel) {
      case RiskLevel.safe:
        return Color(0xFF2E7D32); // Dark green
      case RiskLevel.caution:
        return Color(0xFFF57C00); // Dark amber
      case RiskLevel.avoid:
        return Color(0xFFC62828); // Dark red
      case RiskLevel.unknown:
        return Color(0xFF616161); // Dark grey
    }
  }

  IconData _getRiskIcon(RiskLevel riskLevel) {
    switch (riskLevel) {
      case RiskLevel.safe:
        return Icons.check_circle;
      case RiskLevel.caution:
        return Icons.warning;
      case RiskLevel.avoid:
        return Icons.dangerous;
      case RiskLevel.unknown:
        return Icons.help;
    }
  }

  void _showIngredientDetails(BuildContext context, Ingredient ingredient) {
    showModalBottomSheet(
      context: context,
      builder: (context) {
        return Container(
          padding: const EdgeInsets.all(24),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  Icon(
                    _getRiskIcon(ingredient.riskLevel),
                    color: Color(ingredient.riskLevel.colorCode),
                    size: 24,
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: Text(
                      ingredient.name,
                      style: Theme.of(context).textTheme.titleLarge?.copyWith(
                            fontWeight: FontWeight.bold,
                          ),
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 8),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                decoration: BoxDecoration(
                  color: Color(ingredient.riskLevel.colorCode).withOpacity(0.15),
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(
                    color: Color(ingredient.riskLevel.colorCode),
                    width: 1,
                  ),
                ),
                child: Text(
                  ingredient.riskLevel.displayName,
                  style: TextStyle(
                    color: _getTextColor(ingredient.riskLevel),
                    fontWeight: FontWeight.bold,
                    fontSize: 12,
                  ),
                ),
              ),
              if (ingredient.originalText != null) ...[
                const SizedBox(height: 12),
                Text(
                  'Label text: ${ingredient.originalText}',
                  style: TextStyle(
                    fontSize: 13,
                    color: Colors.grey[600],
                    fontStyle: FontStyle.italic,
                  ),
                ),
              ],
              if (ingredient.description != null) ...[
                const SizedBox(height: 16),
                Text(
                  ingredient.description!,
                  style: Theme.of(context).textTheme.bodyMedium,
                ),
              ],
            ],
          ),
        );
      },
    );
  }
}
