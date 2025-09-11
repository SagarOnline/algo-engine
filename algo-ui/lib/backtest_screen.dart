import 'package:flutter/material.dart';
import 'dart:convert';
import 'package:http/http.dart' as http;
import 'app_config.dart';

class BacktestScreen extends StatefulWidget {
  final String strategyName;
  const BacktestScreen({Key? key, required this.strategyName})
    : super(key: key);

  @override
  State<BacktestScreen> createState() => _BacktestScreenState();
}

class _BacktestScreenState extends State<BacktestScreen> {
  late Future<Map<String, dynamic>> _strategyDetailsFuture;
  final _fromDateController = TextEditingController();
  final _toDateController = TextEditingController();

  @override
  void initState() {
    super.initState();
    _strategyDetailsFuture = fetchStrategyDetails(widget.strategyName);
  }

  Future<Map<String, dynamic>> fetchStrategyDetails(String name) async {
    final baseUrl = AppConfig.getAlgoApiBaseUrl();
    final url = '$baseUrl/strategy/$name';
    final response = await http.get(Uri.parse(url));
    if (response.statusCode == 200) {
      return json.decode(response.body);
    } else {
      throw Exception('Failed to load strategy details');
    }
  }

  @override
  Widget build(BuildContext context) {
    return FutureBuilder<Map<String, dynamic>>(
      future: _strategyDetailsFuture,
      builder: (context, snapshot) {
        if (snapshot.connectionState == ConnectionState.waiting) {
          return Scaffold(
            appBar: AppBar(title: Text('Backtest')),
            body: Center(child: CircularProgressIndicator()),
          );
        } else if (snapshot.hasError) {
          return Scaffold(
            appBar: AppBar(title: Text('Backtest')),
            body: Center(child: Text('Error: \\${snapshot.error}')),
          );
        } else if (!snapshot.hasData) {
          return Scaffold(
            appBar: AppBar(title: Text('Backtest')),
            body: Center(child: Text('No details found')),
          );
        }
        final details = snapshot.data!;
        final strategyDisplayName =
            details['display_name'] ?? details['name'] ?? '';
        final underlyingInstrument =
            details['instrument']?['display_name'] ?? '';
        final positionInstruments =
            (details['positions'] as List?)
                ?.map((p) => p['instrument']?['display_name'] ?? '')
                .join(', ') ??
            '';
        return Scaffold(
          appBar: AppBar(title: Text('Backtest: $strategyDisplayName')),
          body: Center(
            child: Card(
              color: Colors.grey[900],
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(16),
              ),
              elevation: 8,
              child: Padding(
                padding: const EdgeInsets.all(24.0),
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    // Strategy Name
                    const Text(
                      'Strategy Name',
                      style: TextStyle(fontWeight: FontWeight.bold),
                    ),
                    const SizedBox(height: 6),
                    TextField(
                      controller: TextEditingController(
                        text: strategyDisplayName,
                      ),
                      readOnly: true,
                      decoration: const InputDecoration(
                        border: OutlineInputBorder(),
                      ),
                    ),
                    const SizedBox(height: 18),
                    // Underlying Instrument
                    const Text(
                      'Underlying Instrument',
                      style: TextStyle(fontWeight: FontWeight.bold),
                    ),
                    const SizedBox(height: 6),
                    TextField(
                      controller: TextEditingController(
                        text: underlyingInstrument,
                      ),
                      readOnly: true,
                      decoration: const InputDecoration(
                        border: OutlineInputBorder(),
                      ),
                    ),
                    const SizedBox(height: 18),
                    // Position Instruments
                    const Text(
                      'Position Instruments',
                      style: TextStyle(fontWeight: FontWeight.bold),
                    ),
                    const SizedBox(height: 6),
                    TextField(
                      controller: TextEditingController(
                        text: positionInstruments,
                      ),
                      readOnly: true,
                      decoration: const InputDecoration(
                        border: OutlineInputBorder(),
                      ),
                    ),
                    const SizedBox(height: 24),
                    // Date Pickers
                    Row(
                      children: [
                        Expanded(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              const Text(
                                'From Date',
                                style: TextStyle(fontWeight: FontWeight.bold),
                              ),
                              const SizedBox(height: 6),
                              TextField(
                                controller: _fromDateController,
                                decoration: const InputDecoration(
                                  hintText: 'YYYY-MM-DD',
                                  border: OutlineInputBorder(),
                                ),
                                readOnly: true,
                                onTap: () async {
                                  DateTime? picked = await showDatePicker(
                                    context: context,
                                    initialDate: DateTime.now(),
                                    firstDate: DateTime(2000),
                                    lastDate: DateTime(2100),
                                  );
                                  if (picked != null) {
                                    _fromDateController.text = picked
                                        .toIso8601String()
                                        .substring(0, 10);
                                  }
                                },
                              ),
                            ],
                          ),
                        ),
                        const SizedBox(width: 16),
                        Expanded(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              const Text(
                                'To Date',
                                style: TextStyle(fontWeight: FontWeight.bold),
                              ),
                              const SizedBox(height: 6),
                              TextField(
                                controller: _toDateController,
                                decoration: const InputDecoration(
                                  hintText: 'YYYY-MM-DD',
                                  border: OutlineInputBorder(),
                                ),
                                readOnly: true,
                                onTap: () async {
                                  DateTime? picked = await showDatePicker(
                                    context: context,
                                    initialDate: DateTime.now(),
                                    firstDate: DateTime(2000),
                                    lastDate: DateTime(2100),
                                  );
                                  if (picked != null) {
                                    _toDateController.text = picked
                                        .toIso8601String()
                                        .substring(0, 10);
                                  }
                                },
                              ),
                            ],
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 24),
                    // Run Backtest Button
                    Row(
                      mainAxisAlignment: MainAxisAlignment.end,
                      children: [
                        ElevatedButton.icon(
                          onPressed: () {
                            // TODO: Implement backtest action
                          },
                          icon: Icon(Icons.rocket_launch, color: Colors.white),
                          label: const Text(
                            'Run Backtest',
                            style: TextStyle(
                              color: Colors.white,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                          style: ElevatedButton.styleFrom(
                            backgroundColor: Colors.grey[900],
                            foregroundColor: Colors.white,
                            elevation: 2,
                            padding: const EdgeInsets.symmetric(
                              horizontal: 24,
                              vertical: 14,
                            ),
                            shape: RoundedRectangleBorder(
                              borderRadius: BorderRadius.circular(8),
                            ),
                          ),
                        ),
                      ],
                    ),
                  ],
                ),
              ),
            ),
          ),
        );
      },
    );
  }
}
