# NutriScan Mobile - Configuration Guide

## Quick Start

### 1. Install Dependencies
```bash
cd mobile_app
flutter pub get
```

### 2. Generate Code
Before running the app, you MUST generate the freezed and json_serializable code:

```bash
flutter pub run build_runner build --delete-conflicting-outputs
```

This generates all the `.freezed.dart` and `.g.dart` files needed by the models.

### 3. Configure API Endpoint

Edit `lib/providers/scan_state.dart` and update the base URL:

```dart
final scanRepositoryProvider = Provider<ScanRepository>((ref) {
  return ScanRepository(
    baseUrl: 'http://YOUR_IP_ADDRESS:8000',  // Change this!
  );
});
```

**For Android Emulator:**
- Use `http://10.0.2.2:8000` to connect to localhost
- Or use your computer's LAN IP address

**For iOS Simulator:**
- Use `http://localhost:8000` or your computer's IP

**For Physical Devices:**
- Use your computer's LAN IP address (e.g., `http://192.168.1.100:8000`)
- Ensure backend and device are on the same network
- Make sure backend is running with `0.0.0.0` (not just `127.0.0.1`)

### 4. Add Sample Image (Optional)

For the demo mode to work:

1. Find or create a sample food label image
2. Save it as `assets/images/sample_label.jpg`
3. Image should show ingredients list clearly

### 5. Run the App

```bash
# Check connected devices
flutter devices

# Run on specific device
flutter run -d <device_id>

# Run in debug mode with hot reload
flutter run
```

## Backend Setup

Ensure your Django backend is running and accessible:

```bash
# In the project root (not mobile_app)
python manage.py runserver 0.0.0.0:8000
```

Test the endpoint:
```bash
curl http://YOUR_IP:8000/api/v1/scan/
```

## Troubleshooting

### "Unable to connect to server"
- Check backend is running: `curl http://YOUR_IP:8000/`
- Verify firewall isn't blocking port 8000
- For physical devices, ensure both are on same WiFi network

### "File not found" errors
- Run `flutter pub run build_runner build --delete-conflicting-outputs`
- This generates missing `.g.dart` and `.freezed.dart` files

### Sample image not loading
- Ensure file exists at `assets/images/sample_label.jpg`
- Run `flutter pub get` after adding the asset
- Check `pubspec.yaml` has the assets section uncommented

### Hot reload not working
- Try hot restart: Press 'R' in terminal or Shift+R
- Some changes require full restart (models, providers)

### Android emulator slow
- Use hardware acceleration (HAXM/WHPX)
- Increase RAM in AVD settings
- Consider using a physical device

## Development Workflow

1. **Making model changes:**
   ```bash
   # Edit models in lib/models/
   flutter pub run build_runner build --delete-conflicting-outputs
   ```

2. **Live coding with watch mode:**
   ```bash
   # Terminal 1: Watch for model changes
   flutter pub run build_runner watch

   # Terminal 2: Run app with hot reload
   flutter run
   ```

3. **Before committing:**
   ```bash
   flutter analyze
   flutter format lib/
   flutter test  # When tests are added
   ```

## Production Build

### Android
```bash
# Build APK
flutter build apk --release

# Output: build/app/outputs/flutter-apk/app-release.apk

# Build App Bundle (for Play Store)
flutter build appbundle --release
```

### iOS
```bash
# Build iOS app
flutter build ios --release

# Archive in Xcode for App Store submission
```

## Environment-Specific Configuration

For different environments (dev, staging, prod), you can modify `scan_state.dart`:

```dart
final scanRepositoryProvider = Provider<ScanRepository>((ref) {
  const baseUrl = String.fromEnvironment(
    'API_BASE_URL',
    defaultValue: 'http://localhost:8000',
  );
  
  return ScanRepository(baseUrl: baseUrl);
});
```

Then run with:
```bash
flutter run --dart-define=API_BASE_URL=https://api.nutriscan.com
```

## Next Steps

- Configure user profile settings screen
- Add local storage for scan history
- Implement offline mode
- Add internationalization (i18n)
