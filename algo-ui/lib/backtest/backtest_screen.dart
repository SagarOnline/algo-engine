import 'package:algo_ui/backtest/backtest_summary_widget.dart';
import 'package:algo_ui/backtest/strategy_backtest_widget.dart';
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
                    child: PositionsTableWidget(
                      positions:
                          _backtestResult!['tradable']['positions'] as List,
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
