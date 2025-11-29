import 'package:flutter/material.dart';
import 'package:nutriscan_mobile/models/scan_response.dart';
import 'package:nutriscan_mobile/widgets/allergen_alerts.dart';
import 'package:nutriscan_mobile/widgets/ingredient_list.dart';
import 'package:nutriscan_mobile/widgets/swap_carousel.dart';
import 'package:nutriscan_mobile/widgets/traffic_light_badge.dart';
import 'package:nutriscan_mobile/widgets/why_card.dart';

/// Screen displaying scan analysis results
class ResultsScreen extends StatelessWidget {
  final ScanResponse response;

  const ResultsScreen({
    super.key,
    required this.response,
  });

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Scan Results'),
        elevation: 0,
      ),
      body: SingleChildScrollView(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            // Status Warning Banner (if partial error or unreadable)
            if (response.status != ScanStatus.success)
              _buildWarningBanner(context),

            // Traffic Light Badge & Summary
            _buildHeader(context),

            // Allergen Alerts (if any)
            AllergenAlerts(allergens: response.allergenAlerts),

            // Why Card with Citations
            WhyCard(
              why: response.why,
              citations: response.citations,
            ),

            // Ingredients List
            IngredientList(ingredients: response.parsedIngredients),

            // Better Swaps Carousel
            SwapCarousel(swaps: response.betterSwaps),

            // Nutrition Facts (if available)
            if (response.nutritionFacts != null)
              _buildNutritionFacts(context),

            // OCR Raw Text (for debugging/user correction)
            if (response.ocrRawText.isNotEmpty)
              _buildOcrSection(context),

            const SizedBox(height: 24),
          ],
        ),
      ),
    );
  }

  Widget _buildWarningBanner(BuildContext context) {
    Color bannerColor;
    IconData icon;

    if (response.status == ScanStatus.unreadable) {
      bannerColor = Colors.red;
      icon = Icons.error;
    } else {
      bannerColor = Colors.orange;
      icon = Icons.warning;
    }

    return Container(
      color: bannerColor.withOpacity(0.1),
      padding: const EdgeInsets.all(16),
      child: Row(
        children: [
          Icon(icon, color: bannerColor, size: 28),
          const SizedBox(width: 12),
          Expanded(
            child: Text(
              response.status.displayMessage,
              style: TextStyle(
                color: bannerColor.withOpacity(0.9),
                fontWeight: FontWeight.w600,
                fontSize: 14,
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildHeader(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(24),
      child: Column(
        children: [
          // Traffic Light Badge
          TrafficLightBadge(
            trafficLight: response.trafficLight,
            size: 100,
          ),
          const SizedBox(height: 16),

          // Verdict Text
          Text(
            _getVerdictText(),
            style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                  fontWeight: FontWeight.bold,
                ),
            textAlign: TextAlign.center,
          ),
          const SizedBox(height: 8),

          // Short Summary
          Text(
            response.healthImpactSummary.shortSummary,
            style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                  color: Colors.grey[700],
                ),
            textAlign: TextAlign.center,
          ),

          // Scan Metadata
          const SizedBox(height: 16),
          Wrap(
            spacing: 16,
            runSpacing: 8,
            alignment: WrapAlignment.center,
            children: [
              if (response.ocrConfidence != null)
                _buildMetaChip(
                  Icons.document_scanner,
                  'OCR: ${(response.ocrConfidence! * 100).toStringAsFixed(0)}%',
                ),
              if (response.latencyMs != null)
                _buildMetaChip(
                  Icons.speed,
                  '${(response.latencyMs! / 1000).toStringAsFixed(1)}s',
                ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildMetaChip(IconData icon, String label) {
    return Chip(
      avatar: Icon(icon, size: 16),
      label: Text(label, style: const TextStyle(fontSize: 12)),
      padding: const EdgeInsets.symmetric(horizontal: 4),
    );
  }

  String _getVerdictText() {
    switch (response.healthImpactSummary.verdict) {
      case Verdict.excellent:
        return 'Excellent Choice!';
      case Verdict.good:
        return 'Good Choice';
      case Verdict.fair:
        return 'Fair - Consume Moderately';
      case Verdict.poor:
        return 'Poor Choice';
      case Verdict.hazardous:
        return 'Not Recommended';
    }
  }

  Widget _buildNutritionFacts(BuildContext context) {
    final nutrition = response.nutritionFacts!;

    return Card(
      margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Nutrition Facts',
              style: Theme.of(context).textTheme.titleMedium?.copyWith(
                    fontWeight: FontWeight.bold,
                  ),
            ),
            if (nutrition.servingSize != null) ...[
              const SizedBox(height: 8),
              Text(
                'Serving Size: ${nutrition.servingSize}',
                style: TextStyle(
                  fontSize: 13,
                  color: Colors.grey[600],
                  fontWeight: FontWeight.w500,
                ),
              ),
            ],
            const SizedBox(height: 12),
            if (nutrition.calories != null)
              _buildNutritionRow('Calories', nutrition.calories!.toString(), ''),
            if (nutrition.sugarG != null)
              _buildNutritionRow('Sugar', nutrition.sugarG!.toString(), 'g'),
            if (nutrition.sodiumMg != null)
              _buildNutritionRow('Sodium', nutrition.sodiumMg!.toString(), 'mg'),
            if (nutrition.fatG != null)
              _buildNutritionRow('Fat', nutrition.fatG!.toString(), 'g'),
          ],
        ),
      ),
    );
  }

  Widget _buildNutritionRow(String label, String value, String unit) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(
            label,
            style: const TextStyle(fontSize: 14),
          ),
          Text(
            '$value$unit',
            style: const TextStyle(
              fontSize: 14,
              fontWeight: FontWeight.bold,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildOcrSection(BuildContext context) {
    return Card(
      margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      child: ExpansionTile(
        leading: const Icon(Icons.text_fields),
        title: const Text('OCR Raw Text'),
        subtitle: const Text('View extracted text from label'),
        children: [
          Padding(
            padding: const EdgeInsets.all(16),
            child: Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: Colors.grey[100],
                borderRadius: BorderRadius.circular(8),
              ),
              child: Text(
                response.ocrRawText,
                style: const TextStyle(
                  fontSize: 12,
                  fontFamily: 'monospace',
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }
}
