# Build & Run Commands

# Generate freezed and json_serializable code
flutter pub run build_runner build --delete-conflicting-outputs

# Watch mode for continuous code generation during development
# flutter pub run build_runner watch --delete-conflicting-outputs

# Clean build files
flutter clean

# Get dependencies
flutter pub get

# Run app in debug mode
flutter run

# Run app in release mode
flutter run --release

# Build APK (Android)
flutter build apk --release

# Build App Bundle (Android)
flutter build appbundle --release

# Build iOS
flutter build ios --release

# Run tests
flutter test

# Analyze code
flutter analyze

# Format code
flutter format lib/
