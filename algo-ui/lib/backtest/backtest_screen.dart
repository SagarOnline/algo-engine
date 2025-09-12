import 'package:algo_ui/backtest/backtest_summary_widget.dart';
import 'package:algo_ui/backtest/trades_table_widget.dart';
import 'package:flutter/material.dart';
import 'dart:convert';
import 'package:http/http.dart' as http;
import '../app_config.dart';

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

  Map<String, dynamic>? _backtestResult;
  bool _isBacktestLoading = false;
  String? _backtestError;

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

  Future<void> runBacktest() async {
    setState(() {
      _isBacktestLoading = true;
      _backtestError = null;
    });
    final baseUrl = AppConfig.getAlgoApiBaseUrl();
    final url = '$baseUrl/backtest';
    final body = json.encode({
      'strategy_name': widget.strategyName,
      'start_date': _fromDateController.text,
      'end_date': _toDateController.text,
    });
    try {
      final response = await http.post(
        Uri.parse(url),
        headers: {'Content-Type': 'application/json'},
        body: body,
      );
      if (response.statusCode == 200) {
        setState(() {
          _backtestResult = json.decode(response.body);
        });
      } else {
        setState(() {
          _backtestError = 'Failed to run backtest: \\${response.statusCode}';
        });
      }
    } catch (e) {
      setState(() {
        _backtestError = 'Error: $e';
      });
    } finally {
      setState(() {
        _isBacktestLoading = false;
      });
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
          body: SingleChildScrollView(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.center,
              children: [
                StrategyBacktestWidget(
                  strategyDisplayName: strategyDisplayName,
                  underlyingInstrument: underlyingInstrument,
                  positionInstruments: positionInstruments,
                  fromDateController: _fromDateController,
                  toDateController: _toDateController,
                  onRunBacktest: runBacktest,
                  isBacktestLoading: _isBacktestLoading,
                  backtestError: _backtestError,
                ),
                if (_backtestResult != null) ...[
                  if (_backtestResult!['summary'] != null)
                    Padding(
                      padding: const EdgeInsets.only(top: 24),
                      child: BacktestSummaryWidget(
                        summary:
                            _backtestResult!['summary'] as Map<String, dynamic>,
                      ),
                    ),
                  Padding(
                    padding: const EdgeInsets.only(top: 24),
                    child: TradesTableWidget(
                      trades: _backtestResult!['tradable']['trades'] as List,
                    ),
                  ),
                ],
              ],
            ),
          ),
        );
      },
    );
  }
}

class StrategyBacktestWidget extends StatelessWidget {
  final String strategyDisplayName;
  final String underlyingInstrument;
  final String positionInstruments;
  final TextEditingController fromDateController;
  final TextEditingController toDateController;
  final VoidCallback onRunBacktest;
  final bool isBacktestLoading;
  final String? backtestError;

  const StrategyBacktestWidget({
    Key? key,
    required this.strategyDisplayName,
    required this.underlyingInstrument,
    required this.positionInstruments,
    required this.fromDateController,
    required this.toDateController,
    required this.onRunBacktest,
    required this.isBacktestLoading,
    this.backtestError,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Center(
      child: Card(
        color: Colors.grey[900],
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
        elevation: 8,
        child: Padding(
          padding: const EdgeInsets.all(24.0),
          child: Column(
            mainAxisSize: MainAxisSize.max,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Strategy Name
              const Text(
                'Strategy Name',
                style: TextStyle(fontWeight: FontWeight.bold),
              ),
              const SizedBox(height: 6),
              Container(
                width: double.infinity,
                padding: const EdgeInsets.symmetric(
                  vertical: 8,
                  horizontal: 12,
                ),
                decoration: BoxDecoration(
                  color: Colors.grey[850],
                  borderRadius: BorderRadius.circular(8),
                  border: Border.all(color: Colors.grey[700]!),
                ),
                child: Text(
                  strategyDisplayName,
                  style: const TextStyle(color: Colors.white),
                ),
              ),
              const SizedBox(height: 18),
              // Underlying Instrument
              const Text(
                'Underlying Instrument',
                style: TextStyle(fontWeight: FontWeight.bold),
              ),
              const SizedBox(height: 6),
              Container(
                width: double.infinity,
                padding: const EdgeInsets.symmetric(
                  vertical: 8,
                  horizontal: 12,
                ),
                decoration: BoxDecoration(
                  color: Colors.grey[850],
                  borderRadius: BorderRadius.circular(8),
                  border: Border.all(color: Colors.grey[700]!),
                ),
                child: Text(
                  underlyingInstrument,
                  style: const TextStyle(color: Colors.white),
                ),
              ),
              const SizedBox(height: 18),
              // Position Instruments
              const Text(
                'Position Instruments',
                style: TextStyle(fontWeight: FontWeight.bold),
              ),
              const SizedBox(height: 6),
              Container(
                width: double.infinity,
                padding: const EdgeInsets.symmetric(
                  vertical: 8,
                  horizontal: 12,
                ),
                decoration: BoxDecoration(
                  color: Colors.grey[850],
                  borderRadius: BorderRadius.circular(8),
                  border: Border.all(color: Colors.grey[700]!),
                ),
                child: Text(
                  positionInstruments,
                  style: const TextStyle(color: Colors.white),
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
                          controller: fromDateController,
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
                              fromDateController.text = picked
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
                          controller: toDateController,
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
                              toDateController.text = picked
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
                    onPressed: isBacktestLoading ? null : onRunBacktest,
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
              if (isBacktestLoading)
                const Padding(
                  padding: EdgeInsets.only(top: 16),
                  child: Center(child: CircularProgressIndicator()),
                ),
              if (backtestError != null)
                Padding(
                  padding: const EdgeInsets.only(top: 16),
                  child: Text(
                    backtestError!,
                    style: const TextStyle(color: Colors.red),
                  ),
                ),
            ],
          ),
        ),
      ),
    );
  }
}
