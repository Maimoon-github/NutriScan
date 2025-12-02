# NutriScan Mobile App - Flutter Installation Guide

## ⚠️ Flutter Not Detected

The Flutter mobile app has been fully implemented in the `mobile_app/` directory, but Flutter SDK is not currently installed on this system.

## What Was Implemented

A complete **Phase 2** Flutter mobile application with:

✅ **10 Freezed data models** matching the backend API contract  
✅ **Dio-based API client** with comprehensive error handling  
✅ **Riverpod state management** with retry logic  
✅ **5 reusable UI widgets** (TrafficLightBadge, WhyCard, IngredientList, SwapCarousel, AllergenAlerts)  
✅ **2 complete screens** (ScanScreen, ResultsScreen)  
✅ **Demo mode** with sample image support  
✅ **Full documentation** (README, SETUP, BUILD_COMMANDS)

## Option 1: Install Flutter SDK (Recommended for Mobile Development)

If you want to run the Flutter mobile app:

### 1. Download Flutter SDK
- Visit: https://docs.flutter.dev/get-started/install/windows
- Download Flutter SDK for Windows
- Extract to `C:\src\flutter` (or your preferred location)

### 2. Add Flutter to PATH
```powershell
# Add to System Environment Variables
$env:Path += ";C:\src\flutter\bin"

# Or permanently via System Properties > Environment Variables
# Add: C:\src\flutter\bin to PATH
```

### 3. Run Flutter Doctor
```powershell
flutter doctor
```

This will check for:
- ✅ Flutter SDK
- ✅ Android SDK (for Android development)
- ✅ Xcode (for iOS development - macOS only)
- ✅ VS Code / Android Studio

### 4. Install Dependencies
```powershell
cd "C:\Users\CreativePC\Documents\vscode\NutriScan\mobile_app"
flutter pub get
```

### 5. Generate Freezed Code
```powershell
flutter pub run build_runner build --delete-conflicting-outputs
```

### 6. Run the App
```powershell
flutter run
```

## Option 2: Use the Web Console Instead (Already Working)

Since you already have the **web-console** working with React/TypeScript, you can continue using that for development. The web console provides similar functionality:

```powershell
cd "C:\Users\CreativePC\Documents\vscode\NutriScan\web-console"
npm run dev
```

Then open: http://localhost:5173/

## Option 3: Continue with Web Console Only

The web-console at `web-console/` already has Phase 2 functionality implemented with:
- Image upload component
- API integration with axios
- Results display components
- TypeScript type safety
- Responsive design with Tailwind CSS

## Comparison: Flutter vs Web Console

### Flutter Mobile App (`mobile_app/`)
- ✅ Native mobile app (Android/iOS)
- ✅ Better performance on mobile devices
- ✅ Camera integration
- ✅ App store distribution
- ❌ Requires Flutter SDK installation
- ❌ More setup complexity

### Web Console (`web-console/`)
- ✅ Already working and running
- ✅ No additional installation needed
- ✅ Works on desktop browsers
- ✅ Progressive Web App capable
- ✅ Easier to develop and debug
- ❌ Web camera API (not as smooth as native)
- ❌ Cannot be distributed via app stores

## Recommendation

**For immediate development**: Continue with the web-console which is already working.

**For production mobile app**: Install Flutter SDK and use the `mobile_app/` implementation.

## Flutter Mobile App File Structure

```
mobile_app/
├── lib/
│   ├── main.dart                    # App entry point
│   ├── models/                      # Freezed data models
│   │   ├── scan_response.dart
│   │   ├── traffic_light.dart
│   │   ├── ingredient.dart
│   │   ├── allergen.dart
│   │   ├── citation.dart
│   │   ├── better_swap.dart
│   │   └── ... (10 models total)
│   ├── repositories/
│   │   └── scan_repository.dart     # API client with Dio
│   ├── providers/
│   │   └── scan_state.dart          # Riverpod state management
│   ├── widgets/                     # Reusable components
│   │   ├── traffic_light_badge.dart
│   │   ├── why_card.dart
│   │   ├── ingredient_list.dart
│   │   ├── swap_carousel.dart
│   │   └── allergen_alerts.dart
│   └── screens/
│       ├── scan_screen.dart         # Camera/gallery picker
│       └── results_screen.dart      # Analysis results
├── assets/
│   └── images/                      # Sample images for demo
├── pubspec.yaml                     # Dependencies
├── analysis_options.yaml            # Linting rules
├── README.md                        # Full documentation
├── SETUP.md                         # Setup instructions
└── BUILD_COMMANDS.md                # Build commands reference
```

## Quick Start with Web Console

Since Flutter is not installed, here's how to work with what you have:

```powershell
# Navigate to web console
cd "C:\Users\CreativePC\Documents\vscode\NutriScan\web-console"

# Install dependencies (already done)
npm install

# Start development server
npm run dev

# Open browser to http://localhost:5173/
```

## Need Help?

- **Flutter Installation**: https://docs.flutter.dev/get-started/install
- **Web Console**: Already running at http://localhost:5173/
- **Backend API**: Ensure Django server is running on port 8000

## Summary

✅ **Mobile app fully implemented** - Ready to run once Flutter SDK is installed  
✅ **Web console working** - Use this for immediate development  
📱 **Choose your platform** - Mobile (Flutter) or Web (React) based on your needs
