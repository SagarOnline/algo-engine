import 'package:flutter/material.dart';

class BacktestSummaryWidget extends StatelessWidget {
  final Map<String, dynamic> summary;
  const BacktestSummaryWidget({Key? key, required this.summary})
    : super(key: key);

  @override
  Widget build(BuildContext context) {
    // Extract values safely
    final startDate = summary['start_date'] ?? '';
    final endDate = summary['end_date'] ?? '';
    final strategyName = summary['strategy_name'] ?? '';
    final totalTrades = summary['total_trades_count']?.toString() ?? '0';
    final winningTrades = summary['winning_trades_count']?.toString() ?? '0';
    final losingTrades = summary['losing_trades_count']?.toString() ?? '0';
    final winningStreak = summary['winning_streak']?.toString() ?? '0';
    final losingStreak = summary['losing_streak']?.toString() ?? '0';
    final maxGain = summary['max_gain']?.toString() ?? '0';
    final maxLoss = summary['max_loss']?.toString() ?? '0';
    final totalPnLPoints = summary['total_pnl_points']?.toString() ?? '0';
    final totalPnLPercentage = summary['total_pnl_percentage'];

    return Center(
      child: Card(
        color: Colors.grey[900],
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
        elevation: 8,
        child: Padding(
          padding: const EdgeInsets.all(24.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Row(
                    children: [
                      const Text(
                        'Backtest Results',
                        style: TextStyle(
                          fontWeight: FontWeight.bold,
                          fontSize: 18,
                          color: Colors.white,
                        ),
                      ),
                      const SizedBox(width: 8),
                      Text(
                        'for $strategyName',
                        style: const TextStyle(
                          color: Colors.white70,
                          fontSize: 15,
                          fontWeight: FontWeight.w500,
                        ),
                      ),
                    ],
                  ),
                  Text(
                    '($startDate to $endDate)',
                    style: const TextStyle(
                      color: Colors.white70,
                      fontSize: 15,
                      fontWeight: FontWeight.w500,
                    ),
                  ),
                ],
              ),

              const SizedBox(height: 12),
              Wrap(
                spacing: 32,
                runSpacing: 12,
                children: [
                  _summaryItem('Total Trades', totalTrades),
                  _summaryItem(
                    'Winning / Losing Trades',
                    '$winningTrades / $losingTrades',
                  ),
                  _summaryItem(
                    'Winning / Losing Streak',
                    '$winningStreak / $losingStreak',
                  ),
                  _summaryItem(
                    'Max Gain (pts)',
                    maxGain,
                    _getColorForValue(maxGain),
                  ),
                  _summaryItem(
                    'Max Loss (pts)',
                    maxLoss,
                    _getColorForValue(maxLoss),
                  ),
                  _summaryItem(
                    'Total PnL (pts)',
                    totalPnLPoints,
                    _getColorForValue(totalPnLPoints),
                  ),
                  _summaryItem(
                    'Total PnL (%)',
                    totalPnLPercentage?.toString() ?? '0',
                    _getColorForValue(totalPnLPercentage?.toString() ?? '0'),
                  ),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _summaryItem(String label, String value, [Color? valueColor]) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          label,
          style: const TextStyle(
            color: Colors.white70,
            fontWeight: FontWeight.bold,
            fontSize: 13,
          ),
        ),
        const SizedBox(height: 4),
        Text(
          value,
          style: TextStyle(color: valueColor ?? Colors.white, fontSize: 15),
        ),
      ],
    );
  }

  Color _getColorForValue(String value) {
    // Remove any formatting characters and parse the numeric value
    String cleanValue = value.replaceAll(RegExp(r'[^\d.-]'), '');
    double? numValue = double.tryParse(cleanValue);

    if (numValue == null) {
      return Colors.white; // Default color if parsing fails
    }

    if (numValue < 0) {
      return Colors.red;
    } else if (numValue > 0) {
      return Colors.green;
    } else {
      return Colors.white; // Neutral color for zero
    }
  }
}
