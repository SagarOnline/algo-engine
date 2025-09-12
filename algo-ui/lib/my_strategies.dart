import 'package:flutter/material.dart';
import 'dart:convert';
import 'package:http/http.dart' as http;
import 'app_config.dart';
import 'backtest_screen.dart';

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
          return Container(
            color: Colors.grey[900],
            padding: const EdgeInsets.all(16),
            child: Card(
              color: Colors.black,
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(16),
              ),
              elevation: 8,
              child: DataTable(
                headingRowColor: MaterialStateProperty.resolveWith<Color?>(
                  (states) => Colors.deepPurple[700],
                ),
                dataRowColor: MaterialStateProperty.resolveWith<Color?>((
                  states,
                ) {
                  // Use index from DataRow, not states
                  // We'll use the index from the strategies list
                  // This requires us to build the rows with index
                  return null; // We'll set color in DataRow below
                }),
                columnSpacing: 24,
                horizontalMargin: 16,
                columns: const [
                  DataColumn(
                    label: Text(
                      'Strategy Name',
                      style: TextStyle(
                        color: Colors.white,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ),
                  DataColumn(
                    label: Text(
                      'Description',
                      style: TextStyle(
                        color: Colors.white,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ),
                  DataColumn(
                    label: Text(
                      'Instrument',
                      style: TextStyle(
                        color: Colors.white,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ),
                  DataColumn(
                    label: Text(
                      'Actions',
                      style: TextStyle(
                        color: Colors.white,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ),
                ],
                rows: List<DataRow>.generate(strategies.length, (index) {
                  final strategy = strategies[index];
                  final instrument = strategy['instrument'] ?? {};
                  final rowColor = index % 2 == 0
                      ? Colors.grey[850]
                      : Colors.grey[800];
                  return DataRow(
                    color: MaterialStateProperty.resolveWith<Color?>(
                      (_) => rowColor,
                    ),
                    cells: [
                      DataCell(
                        Text(
                          strategy['display_name'] ?? strategy['name'] ?? '',
                          style: const TextStyle(color: Colors.white),
                        ),
                      ),
                      DataCell(
                        Container(
                          width: 180,
                          child: Text(
                            strategy['description'] ?? '',
                            style: const TextStyle(color: Colors.white70),
                            overflow: TextOverflow.ellipsis,
                            maxLines: 1,
                          ),
                        ),
                      ),
                      DataCell(
                        Text(
                          instrument['display_name'] ?? '',
                          style: const TextStyle(color: Colors.amber),
                        ),
                      ),
                      DataCell(
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
                                  builder: (context) => BacktestScreen(
                                    strategyName: strategyName,
                                  ),
                                ),
                              );
                            },
                            child: const Text(
                              'Backtest',
                              style: TextStyle(color: Colors.white),
                            ),
                          ),
                        ),
                      ),
                    ],
                  );
                }),
              ),
            ),
          );
        },
      ),
    );
  }
}
