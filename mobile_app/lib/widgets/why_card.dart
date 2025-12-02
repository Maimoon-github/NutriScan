import 'package:flutter/material.dart';
import 'package:nutriscan_mobile/models/citation.dart';

/// Expandable card showing the "why" explanation
class WhyCard extends StatefulWidget {
  final String why;
  final List<Citation> citations;

  const WhyCard({
    super.key,
    required this.why,
    required this.citations,
  });

  @override
  State<WhyCard> createState() => _WhyCardState();
}

class _WhyCardState extends State<WhyCard> {
  bool _isExpanded = false;

  @override
  Widget build(BuildContext context) {
    return Card(
      elevation: 2,
      margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          InkWell(
            onTap: () {
              setState(() {
                _isExpanded = !_isExpanded;
              });
            },
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Row(
                children: [
                  Icon(
                    Icons.info_outline,
                    color: Theme.of(context).primaryColor,
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: Text(
                      'Why this rating?',
                      style: Theme.of(context).textTheme.titleMedium?.copyWith(
                            fontWeight: FontWeight.bold,
                          ),
                    ),
                  ),
                  Icon(
                    _isExpanded ? Icons.expand_less : Icons.expand_more,
                    color: Colors.grey[600],
                  ),
                ],
              ),
            ),
          ),
          if (_isExpanded) ...[
            Divider(height: 1),
            Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    widget.why,
                    style: Theme.of(context).textTheme.bodyMedium,
                  ),
                  if (widget.citations.isNotEmpty) ...[
                    const SizedBox(height: 16),
                    Text(
                      'Sources',
                      style: Theme.of(context).textTheme.titleSmall?.copyWith(
                            fontWeight: FontWeight.bold,
                          ),
                    ),
                    const SizedBox(height: 8),
                    ...widget.citations.map((citation) => _buildCitation(citation)),
                  ],
                ],
              ),
            ),
          ],
        ],
      ),
    );
  }

  Widget _buildCitation(Citation citation) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 8),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Icon(
            Icons.article_outlined,
            size: 16,
            color: Colors.grey[600],
          ),
          const SizedBox(width: 8),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  citation.authority,
                  style: TextStyle(
                    fontWeight: FontWeight.w600,
                    fontSize: 13,
                  ),
                ),
                if (citation.docId != null) ...[
                  const SizedBox(height: 2),
                  Text(
                    citation.docId!,
                    style: TextStyle(
                      fontSize: 12,
                      color: Colors.grey[600],
                    ),
                  ),
                ],
                if (citation.excerpt != null) ...[
                  const SizedBox(height: 4),
                  Text(
                    '"${citation.excerpt}"',
                    style: TextStyle(
                      fontSize: 12,
                      fontStyle: FontStyle.italic,
                      color: Colors.grey[700],
                    ),
                  ),
                ],
                if (citation.url != null) ...[
                  const SizedBox(height: 4),
                  InkWell(
                    onTap: () {
                      // TODO: Launch URL
                      ScaffoldMessenger.of(context).showSnackBar(
                        SnackBar(content: Text('URL: ${citation.url}')),
                      );
                    },
                    child: Text(
                      'View source →',
                      style: TextStyle(
                        fontSize: 12,
                        color: Theme.of(context).primaryColor,
                        decoration: TextDecoration.underline,
                      ),
                    ),
                  ),
                ],
              ],
            ),
          ),
        ],
      ),
    );
  }
}
