import 'dart:io';

class AppConfig {
  static String getAlgoApiBaseUrl() {
    // Try to read from environment variable

    const envVar = String.fromEnvironment(
      'ALGO_API_BASE_URL',
      defaultValue: '',
    );
    if (envVar.isNotEmpty) {
      return envVar;
    }
    // Fallback
    return '/api';
  }
}
