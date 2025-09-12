import 'package:flutter/material.dart';
import 'package:data_table_2/data_table_2.dart';

class DashboardTable extends StatelessWidget {
  final List<String> columnNames;
  final List<List<Widget>> rowCells;

  const DashboardTable({
    Key? key,
    required this.columnNames,
    required this.rowCells,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Container(
      padding: const EdgeInsets.all(1),
      decoration: BoxDecoration(
        border: Border.all(color: Colors.black, width: 1),
        borderRadius: BorderRadius.circular(8),
      ),
      child: Card(
        color: theme.cardColor,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
        elevation: 8,
        child: DataTable2(
          headingRowColor: MaterialStateProperty.resolveWith<Color?>(
            (states) => theme.colorScheme.primary,
          ),
          columnSpacing: 24,
          horizontalMargin: 16,
          columns: columnNames
              .map(
                (name) => DataColumn(
                  label: Text(name, style: theme.textTheme.titleMedium),
                ),
              )
              .toList(),
          rows: List<DataRow>.generate(rowCells.length, (index) {
            final rowColor = index % 2 == 0
                ? theme.colorScheme.surface
                : theme.colorScheme.onSurface.withOpacity(0.08);
            return DataRow(
              color: MaterialStateProperty.resolveWith<Color?>(
                (states) => rowColor,
              ),
              cells: rowCells[index].map((cell) => DataCell(cell)).toList(),
            );
          }),
        ),
      ),
    );
  }
}
