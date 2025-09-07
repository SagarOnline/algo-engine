# Algo UI

The **Algo UI** is the front-end interface for the Algo Engine platform.  
It provides a modern, cross-platform dashboard for visualizing strategy performance, managing trades, and interacting with the core engine.

---

## 📌 Overview

- **Strategy Dashboard**  
  Visualize backtest results, live trading status, and key metrics from the Algo Engine.

- **Trade Management**  
  Place, monitor, and manage trades directly from the UI.

- **Multi-Platform Support**  
  Runs on web, desktop (Windows, macOS, Linux), and mobile (Android, iOS) using Flutter.

---

## ⚙️ Features

- Real-time display of strategy performance and trade status.
- Navigation for switching between Home, My Strategies, and other modules.
- Responsive design for desktop and mobile layouts.
- Integration with the Algo Engine API for live data and actions.
- Modular architecture for easy extension and customization.

---

## 🚀 Getting Started

### Prerequisites

- [Flutter SDK](https://docs.flutter.dev/get-started/install) (version 3.35.2+ recommended)
- Dart SDK (comes with Flutter) 3.9.0+
- Access to the Algo Engine API (for live data)

### Installation

1. **Clone the repository:**

   ```bash
   git clone https://github.com/SagarOnline/algo-engine.git
   cd algo-engine/algo-ui
   ```

2. **Install dependencies:**

   ```bash
   flutter pub get
   ```

---

### Running the UI Locally

#### Web

```bash
flutter run -d chrome
```

#### Desktop (Windows, macOS, Linux)

```bash
flutter run -d windows   # For Windows
flutter run -d macos     # For macOS
flutter run -d linux     # For Linux
```

#### Mobile (Android, iOS)

```bash
flutter run -d android
flutter run -d ios
```

---

### Development Tips

- To hot reload during development, press `r` in the terminal or use your IDE’s hot reload feature.
- To run tests:

  ```bash
  flutter test
  ```

- To build for production:

  ```bash
  flutter build web      # For web
  flutter build windows  # For Windows
  flutter build macos    # For macOS
  flutter build linux    # For Linux
  flutter build apk      # For Android
  flutter build ios      # For iOS
  ```

---

## 🛠️ Customization

- Update API endpoints in the code to match your Algo Engine server.
- Modify UI components in `lib/` to add new features or change layouts.

---

## 📚 Resources

- [Flutter Documentation](https://docs.flutter.dev/)
- [Algo Engine API](../algo-api/README.md)

---
