// This is a basic Flutter widget test.
//
// To perform an interaction with a widget in your test, use the WidgetTester
// utility in the flutter_test package. For example, you can send tap and scroll
// gestures. You can also use WidgetTester to find child widgets in the widget
// tree, read text, and verify that the values of widget properties are correct.

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

import 'package:algo_ui/main.dart';

void main() {
  testWidgets('App title and home page text are shown', (
    WidgetTester tester,
  ) async {
    await tester.pumpWidget(const AlgoApp());
    expect(find.text('Sutram'), findsWidgets); // AppBar and NavigationRail
    expect(find.text('Welcome to Sutram Home!'), findsOneWidget);
  });

  testWidgets('NavigationRail toggles and navigates (desktop)', (
    WidgetTester tester,
  ) async {
    tester.binding.window.physicalSizeTestValue = const Size(1200, 800);
    tester.binding.window.devicePixelRatioTestValue = 1.0;
    await tester.pumpWidget(const AlgoApp());
    // Should show NavigationRail
    expect(find.byType(NavigationRail), findsOneWidget);
    // Toggle NavigationRail
    await tester.tap(find.byIcon(Icons.chevron_left));
    await tester.pump();
    expect(find.byIcon(Icons.chevron_right), findsOneWidget);
    // Navigate to My Strategies
    await tester.tap(find.text('My Strategies'));
    await tester.pump();
    expect(find.text('My Strategies'), findsWidgets);
    expect(find.text('Welcome to Sutram Home!'), findsNothing);
    // Reset window size
    addTearDown(tester.binding.window.clearPhysicalSizeTestValue);
    addTearDown(tester.binding.window.clearDevicePixelRatioTestValue);
  });
}
