import 'dart:io';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:image_picker/image_picker.dart';
import 'package:nutriscan_mobile/providers/scan_state.dart';
import 'package:nutriscan_mobile/screens/results_screen.dart';
import 'package:path_provider/path_provider.dart';

/// Main scan screen with camera/gallery picker and demo mode
class ScanScreen extends ConsumerStatefulWidget {
  const ScanScreen({super.key});

  @override
  ConsumerState<ScanScreen> createState() => _ScanScreenState();
}

class _ScanScreenState extends ConsumerState<ScanScreen> {
  final ImagePicker _picker = ImagePicker();

  @override
  Widget build(BuildContext context) {
    final scanState = ref.watch(scanNotifierProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('NutriScan'),
        elevation: 0,
      ),
      body: Center(
        child: scanState.when(
          initial: () => _buildInitialView(),
          loading: () => _buildLoadingView(),
          success: (response) {
            // Navigate to results screen
            WidgetsBinding.instance.addPostFrameCallback((_) {
              Navigator.of(context).push(
                MaterialPageRoute(
                  builder: (context) => ResultsScreen(response: response),
                ),
              ).then((_) {
                // Reset state when coming back
                ref.read(scanNotifierProvider.notifier).reset();
              });
            });
            return _buildLoadingView(); // Show loading while navigating
          },
          error: (type, message, canRetry) => _buildErrorView(type, message, canRetry),
        ),
      ),
    );
  }

  Widget _buildInitialView() {
    return Padding(
      padding: const EdgeInsets.all(24),
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(
            Icons.camera_alt,
            size: 100,
            color: Theme.of(context).primaryColor.withOpacity(0.5),
          ),
          const SizedBox(height: 24),
          Text(
            'Scan a Food Label',
            style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                  fontWeight: FontWeight.bold,
                ),
          ),
          const SizedBox(height: 12),
          Text(
            'Take a photo of ingredients list to analyze',
            style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                  color: Colors.grey[600],
                ),
            textAlign: TextAlign.center,
          ),
          const SizedBox(height: 48),
          ElevatedButton.icon(
            onPressed: () => _pickImage(ImageSource.camera),
            icon: const Icon(Icons.camera_alt),
            label: const Text('Take Photo'),
            style: ElevatedButton.styleFrom(
              padding: const EdgeInsets.symmetric(horizontal: 32, vertical: 16),
              textStyle: const TextStyle(fontSize: 16),
            ),
          ),
          const SizedBox(height: 16),
          OutlinedButton.icon(
            onPressed: () => _pickImage(ImageSource.gallery),
            icon: const Icon(Icons.photo_library),
            label: const Text('Choose from Gallery'),
            style: OutlinedButton.styleFrom(
              padding: const EdgeInsets.symmetric(horizontal: 32, vertical: 16),
              textStyle: const TextStyle(fontSize: 16),
            ),
          ),
          const SizedBox(height: 32),
          Divider(),
          const SizedBox(height: 16),
          TextButton.icon(
            onPressed: _useSampleImage,
            icon: const Icon(Icons.image, size: 20),
            label: const Text('Use Sample Image'),
            style: TextButton.styleFrom(
              foregroundColor: Colors.green[700],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildLoadingView() {
    return Column(
      mainAxisAlignment: MainAxisAlignment.center,
      children: [
        const CircularProgressIndicator(),
        const SizedBox(height: 24),
        Text(
          'Analyzing label...',
          style: Theme.of(context).textTheme.titleMedium,
        ),
        const SizedBox(height: 8),
        Text(
          'This may take a few seconds',
          style: Theme.of(context).textTheme.bodySmall?.copyWith(
                color: Colors.grey[600],
              ),
        ),
      ],
    );
  }

  Widget _buildErrorView(String type, String message, bool canRetry) {
    IconData errorIcon;
    Color errorColor;

    switch (type) {
      case 'network':
        errorIcon = Icons.wifi_off;
        errorColor = Colors.orange;
        break;
      case 'validation':
        errorIcon = Icons.error_outline;
        errorColor = Colors.red;
        break;
      case 'server':
        errorIcon = Icons.cloud_off;
        errorColor = Colors.orange;
        break;
      default:
        errorIcon = Icons.error;
        errorColor = Colors.red;
    }

    return Padding(
      padding: const EdgeInsets.all(24),
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(
            errorIcon,
            size: 80,
            color: errorColor,
          ),
          const SizedBox(height: 24),
          Text(
            'Scan Failed',
            style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                  fontWeight: FontWeight.bold,
                ),
          ),
          const SizedBox(height: 12),
          Text(
            message,
            style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                  color: Colors.grey[700],
                ),
            textAlign: TextAlign.center,
          ),
          const SizedBox(height: 32),
          if (canRetry) ...[
            ElevatedButton.icon(
              onPressed: () {
                ref.read(scanNotifierProvider.notifier).retry();
              },
              icon: const Icon(Icons.refresh),
              label: const Text('Retry'),
              style: ElevatedButton.styleFrom(
                padding: const EdgeInsets.symmetric(horizontal: 32, vertical: 16),
              ),
            ),
            const SizedBox(height: 16),
          ],
          OutlinedButton.icon(
            onPressed: () {
              ref.read(scanNotifierProvider.notifier).reset();
            },
            icon: const Icon(Icons.arrow_back),
            label: const Text('Start Over'),
            style: OutlinedButton.styleFrom(
              padding: const EdgeInsets.symmetric(horizontal: 32, vertical: 16),
            ),
          ),
        ],
      ),
    );
  }

  Future<void> _pickImage(ImageSource source) async {
    try {
      final XFile? image = await _picker.pickImage(
        source: source,
        maxWidth: 1920,
        maxHeight: 1920,
        imageQuality: 85,
      );

      if (image != null) {
        _uploadImage(File(image.path));
      }
    } catch (e) {
      _showError('Failed to pick image: $e');
    }
  }

  Future<void> _useSampleImage() async {
    try {
      // Load sample image from assets
      final ByteData data = await rootBundle.load('assets/images/sample_label.jpg');
      
      // Write to temporary file
      final tempDir = await getTemporaryDirectory();
      final file = File('${tempDir.path}/sample_label.jpg');
      await file.writeAsBytes(data.buffer.asUint8List());

      _uploadImage(file);
    } catch (e) {
      _showError('Failed to load sample image: $e');
    }
  }

  void _uploadImage(File image) {
    // TODO: Allow user to configure profile
    // For now, using empty profile
    ref.read(scanNotifierProvider.notifier).uploadScan(
          image: image,
          profileJson: null,
        );
  }

  void _showError(String message) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(message),
        backgroundColor: Colors.red,
      ),
    );
  }
}
