import 'package:flutter/material.dart';
import 'dart:convert';
import 'package:http/http.dart' as http;
import 'app_config.dart';
import 'package:algo_ui/backtest/backtest_screen.dart';
import 'dashboard_table.dart';

class MyStrategiesPage extends StatefulWidget {
  const MyStrategiesPage({Key? key}) : super(key: key);

  @override
  State<MyStrategiesPage> createState() => _MyStrategiesPageState();
}

class _MyStrategiesPageState extends State<MyStrategiesPage> {
  late Future<List<Map<String, dynamic>>> _strategiesFuture;

  @override
  void initState() {
    super.initState();
    _strategiesFuture = fetchStrategies();
  }

  Future<List<Map<String, dynamic>>> fetchStrategies() async {
    final baseUrl = AppConfig.getAlgoApiBaseUrl();
    final url = '$baseUrl/strategy';
    final response = await http.get(Uri.parse(url));
    if (response.statusCode == 200) {
      final List<dynamic> data = json.decode(response.body);
      return data.cast<Map<String, dynamic>>();
    } else {
      throw Exception('Failed to load strategies');
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('My Strategies')),
      body: FutureBuilder<List<Map<String, dynamic>>>(
        future: _strategiesFuture,
        builder: (context, snapshot) {
          if (snapshot.connectionState == ConnectionState.waiting) {
            return const Center(child: CircularProgressIndicator());
          } else if (snapshot.hasError) {
            return Center(child: Text('Error: \\${snapshot.error}'));
          } else if (!snapshot.hasData || snapshot.data!.isEmpty) {
            return const Center(child: Text('No strategies found'));
          }
          final strategies = snapshot.data!;
          // Use DashboardTable instead of DataTable
          return Card(
            color: Colors.grey[900],
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(16),
            ),
            elevation: 8,
            child: Padding(
              padding: const EdgeInsets.all(24.0),
              child: DashboardTable(
                columnNames: [
                  'Strategy Name',
                  'Description',
                  'Instrument',
                  'Actions',
                ],
                rowCells: List.generate(strategies.length, (index) {
                  final strategy = strategies[index];
                  final instrument = strategy['instrument'] ?? {};
                  return [
                    Text(
                      strategy['display_name'] ?? strategy['name'] ?? '',
                      style: const TextStyle(color: Colors.white),
                    ),
                    Container(
                      width: 180,
                      child: Text(
                        strategy['description'] ?? '',
                        style: const TextStyle(color: Colors.white70),
                        overflow: TextOverflow.ellipsis,
                        maxLines: 1,
                      ),
                    ),
                    Text(
                      instrument['display_name'] ?? '',
                      style: const TextStyle(color: Colors.amber),
                    ),
                    Padding(
                      padding: const EdgeInsets.symmetric(vertical: 4.0),
                      child: ElevatedButton(
                        style: ElevatedButton.styleFrom(
                          backgroundColor: Colors.blue,
                          shape: RoundedRectangleBorder(
                            borderRadius: BorderRadius.circular(8),
                          ),
                          padding: const EdgeInsets.symmetric(
                            horizontal: 20,
                            vertical: 8,
                          ),
                        ),
                        onPressed: () {
                          final strategyName =
                              strategy['name'] ??
                              strategy['display_name'] ??
                              '';
                          Navigator.of(context).push(
                            MaterialPageRoute(
                              builder: (context) =>
                                  BacktestScreen(strategyName: strategyName),
                            ),
                          );
                        },
                        child: const Text(
                          'Backtest',
                          style: TextStyle(color: Colors.white),
                        ),
                      ),
                    ),
                  ];
                }),
              ),
            ),
          );
        },
      ),
    );
  }
}
