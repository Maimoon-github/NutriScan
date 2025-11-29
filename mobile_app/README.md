# NutriScan Mobile App

A Flutter mobile application for scanning and analyzing food labels to provide health insights based on ingredients, allergens, and regulatory compliance.

## Features

### ✅ Phase 2 Implementation

- **Data Layer with Freezed Models**: Type-safe, immutable data models matching the backend API contract
- **API Integration with Dio**: Robust networking layer with comprehensive error handling
- **State Management with Riverpod**: Clean state management with retry logic for failed requests
- **Component-Based UI**:
  - `TrafficLightBadge`: Visual health status indicator
  - `WhyCard`: Expandable explanation with regulatory citations
  - `IngredientList`: Color-coded ingredient chips by risk level
  - `SwapCarousel`: Horizontal scrollable list of better alternatives
  - `AllergenAlerts`: Prominent allergen warnings
- **Results Screen**: Comprehensive analysis display with status warnings
- **Demo Mode**: Test functionality with bundled sample images

## Project Structure

```
lib/
├── main.dart                 # App entry point
├── models/                   # Freezed data models
│   ├── scan_response.dart    # Main API response
│   ├── traffic_light.dart    # Traffic light enum
│   ├── ingredient.dart       # Ingredient model
│   ├── allergen.dart         # Allergen model
│   ├── citation.dart         # Citation/source model
│   ├── better_swap.dart      # Product swap model
│   └── ...
├── repositories/             # Data layer
│   └── scan_repository.dart  # API client with Dio
├── providers/                # State management
│   └── scan_state.dart       # Riverpod state notifier
├── widgets/                  # Reusable UI components
│   ├── traffic_light_badge.dart
│   ├── why_card.dart
│   ├── ingredient_list.dart
│   ├── swap_carousel.dart
│   └── allergen_alerts.dart
└── screens/                  # Main screens
    ├── scan_screen.dart      # Camera/gallery picker
    └── results_screen.dart   # Analysis results
```

## Setup Instructions

### Prerequisites

- Flutter SDK 3.0.0 or higher
- Dart 3.0.0 or higher
- Android Studio / Xcode for mobile development

### Installation

1. **Install dependencies**:
   ```bash
   cd mobile_app
   flutter pub get
   ```

2. **Generate code** (Freezed & JSON serialization):
   ```bash
   flutter pub run build_runner build --delete-conflicting-outputs
   ```

3. **Add sample image** (for demo mode):
   - Place a sample food label image at `assets/images/sample_label.jpg`

4. **Configure API endpoint**:
   - Edit `lib/providers/scan_state.dart` and update the `baseUrl` in `scanRepositoryProvider`:
     ```dart
     baseUrl: 'http://YOUR_SERVER_IP:8000',
     ```

### Running the App

```bash
# Run on connected device/emulator
flutter run

# Run in debug mode with hot reload
flutter run --debug

# Build release APK (Android)
flutter build apk --release

# Build iOS app
flutter build ios --release
```

## API Integration

### Endpoint
- **POST** `/api/v1/scan/`

### Request Format
- `image`: MultipartFile (JPEG/PNG)
- `user_profile`: Optional JSON string with user context

### Error Handling

The app handles three types of errors:

1. **Network Errors** (retryable):
   - Connection timeout
   - No internet connection
   - Server unreachable

2. **Validation Errors** (non-retryable):
   - HTTP 400 - Missing or invalid image
   - Malformed user profile

3. **Server Errors** (retryable):
   - HTTP 500 - Backend processing failure

## State Management

### Scan States

- `initial`: App ready for new scan
- `loading`: Processing scan request
- `success(ScanResponse)`: Analysis complete
- `error(type, message, canRetry)`: Scan failed

### Retry Logic

- Network errors and 500s: Retry enabled
- 400 validation errors: Retry disabled (user must fix input)

## UI Components

### Traffic Light Badge
- **Green**: Safe/healthy product
- **Yellow**: Moderate caution
- **Red**: Avoid or high risk

### Ingredient Chips
- Color-coded by risk level
- Tap to view detailed information
- Shows original label text

### Better Swaps Carousel
- Horizontal scrollable cards
- Shows alternative products with reasons
- Includes price hints when available

### Why Card
- Expandable accordion
- Shows analysis explanation
- Lists regulatory citations with links

## Testing

### Manual Testing Checklist

- [ ] Camera capture works
- [ ] Gallery image selection works
- [ ] Sample image demo loads
- [ ] Loading state displays during scan
- [ ] Success state navigates to results
- [ ] Error states show retry button (for retryable errors)
- [ ] Traffic light badge displays correct color
- [ ] Ingredients list shows all parsed items
- [ ] Allergen alerts appear for allergenic ingredients
- [ ] Better swaps carousel scrolls horizontally
- [ ] Why card expands/collapses
- [ ] OCR raw text is viewable

## Known Limitations

- Sample image must be manually added to `assets/images/`
- API endpoint is hardcoded (needs configuration screen)
- User profile is not yet configurable
- No offline support
- No scan history persistence

## Next Steps (Phase 3+)

- [ ] User profile configuration screen
- [ ] Scan history with local storage
- [ ] Offline mode with cached results
- [ ] Multi-language support
- [ ] Barcode scanning integration
- [ ] Social sharing features
- [ ] Product database search

## Dependencies

### Core
- `flutter_riverpod` - State management
- `dio` - HTTP client
- `freezed` - Immutable models
- `json_serializable` - JSON parsing

### UI
- `image_picker` - Camera/gallery access
- `path_provider` - File system access

### Development
- `build_runner` - Code generation
- `flutter_lints` - Linting rules

## License

Copyright © 2025 NutriScan. All rights reserved.
