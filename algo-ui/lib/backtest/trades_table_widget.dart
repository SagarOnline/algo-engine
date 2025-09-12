import 'package:flutter/material.dart';

class TradesTableWidget extends StatelessWidget {
  final List trades;
  const TradesTableWidget({Key? key, required this.trades}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Center(
      child: Card(
        color: Colors.grey[900],
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
        elevation: 8,
        child: Padding(
          padding: const EdgeInsets.all(24.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Text(
                'Trades',
                style: TextStyle(
                  fontWeight: FontWeight.bold,
                  fontSize: 18,
                  color: Colors.white,
                ),
              ),
              const SizedBox(height: 12),
              SingleChildScrollView(
                scrollDirection: Axis.horizontal,
                child: DataTable(
                  headingRowColor: MaterialStateProperty.resolveWith<Color?>(
                    (_) => Colors.deepPurple[700],
                  ),
                  dataRowColor: MaterialStateProperty.resolveWith<Color?>(
                    (states) => Colors.grey[850],
                  ),
                  columns: const [
                    DataColumn(
                      label: Text(
                        'Entry Price',
                        style: TextStyle(
                          color: Colors.white,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ),
                    DataColumn(
                      label: Text(
                        'Entry Time',
                        style: TextStyle(
                          color: Colors.white,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ),
                    DataColumn(
                      label: Text(
                        'Exit Price',
                        style: TextStyle(
                          color: Colors.white,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ),
                    DataColumn(
                      label: Text(
                        'Exit Time',
                        style: TextStyle(
                          color: Colors.white,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ),
                    DataColumn(
                      label: Text(
                        'Profit',
                        style: TextStyle(
                          color: Colors.white,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ),
                    DataColumn(
                      label: Text(
                        'Profit %',
                        style: TextStyle(
                          color: Colors.white,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ),
                    DataColumn(
                      label: Text(
                        'Quantity',
                        style: TextStyle(
                          color: Colors.white,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ),
                  ],
                  rows: List<DataRow>.generate(trades.length, (index) {
                    final trade = trades[index];
                    return DataRow(
                      cells: [
                        DataCell(
                          Text(
                            trade['entry_price'].toString(),
                            style: const TextStyle(color: Colors.white),
                          ),
                        ),
                        DataCell(
                          Text(
                            trade['entry_time'].toString(),
                            style: const TextStyle(color: Colors.white70),
                          ),
                        ),
                        DataCell(
                          Text(
                            trade['exit_price'].toString(),
                            style: const TextStyle(color: Colors.white),
                          ),
                        ),
                        DataCell(
                          Text(
                            trade['exit_time'].toString(),
                            style: const TextStyle(color: Colors.white70),
                          ),
                        ),
                        DataCell(
                          Text(
                            trade['profit'].toStringAsFixed(2),
                            style: TextStyle(
                              color: trade['profit'] >= 0
                                  ? Colors.green
                                  : Colors.red,
                            ),
                          ),
                        ),
                        DataCell(
                          Text(
                            (trade['profit_percentage'] * 100).toStringAsFixed(
                                  2,
                                ) +
                                '%',
                            style: TextStyle(
                              color: trade['profit_percentage'] >= 0
                                  ? Colors.green
                                  : Colors.red,
                            ),
                          ),
                        ),
                        DataCell(
                          Text(
                            trade['quantity'].toString(),
                            style: const TextStyle(color: Colors.white),
                          ),
                        ),
                      ],
                    );
                  }),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
