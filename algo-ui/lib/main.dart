import 'package:flutter/material.dart';
import 'app_config.dart';
import 'my_strategies.dart';

void main() {
  runApp(const AlgoApp());
}

class AlgoApp extends StatelessWidget {
  const AlgoApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Sattva',
      theme: ThemeData.dark().copyWith(
        colorScheme: ColorScheme.dark(
          primary: Colors.deepPurple,
          secondary: Colors.amber,
        ),
        scaffoldBackgroundColor: Colors.black,
      ),
      home: const AlgoHome(),
      debugShowCheckedModeBanner: false,
    );
  }
}

class AlgoHome extends StatefulWidget {
  const AlgoHome({super.key});

  @override
  State<AlgoHome> createState() => _AlgoHomeState();
}

class _AlgoHomeState extends State<AlgoHome> {
  int _selectedIndex = 0;
  bool _isRailExtended = true;

  Widget _getContent(int index) {
    switch (index) {
      case 0:
        return const Center(
          child: Text(
            'Welcome to Sattva Home!',
            style: TextStyle(fontSize: 24),
          ),
        );
      case 1:
        return const MyStrategiesPage();
      default:
        return const Center(child: Text('Unknown Page'));
    }
  }

  @override
  Widget build(BuildContext context) {
    final isDesktop = MediaQuery.of(context).size.width > 800;
    return Scaffold(
      body: Row(
        children: [
          AnimatedContainer(
            duration: const Duration(milliseconds: 300),
            curve: Curves.easeInOut,
            child: isDesktop
                ? NavigationRail(
                    extended: _isRailExtended,
                    backgroundColor: Colors.grey[900],
                    leading: Column(
                      children: [
                        const SizedBox(height: 16),
                        Padding(
                          padding: const EdgeInsets.all(8.0),
                          child: CircleAvatar(
                            radius: 24,
                            backgroundColor: Colors.deepPurple,
                            child: const Icon(
                              Icons.show_chart,
                              color: Colors.white,
                              size: 28,
                            ),
                          ),
                        ),
                        const SizedBox(height: 8),
                        if (_isRailExtended)
                          const Text(
                            'Sattva',
                            style: TextStyle(
                              fontSize: 20,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                        IconButton(
                          icon: Icon(
                            _isRailExtended
                                ? Icons.chevron_left
                                : Icons.chevron_right,
                            size: 18,
                          ),
                          onPressed: () => setState(
                            () => _isRailExtended = !_isRailExtended,
                          ),
                        ),
                      ],
                    ),
                    destinations: [
                      NavigationRailDestination(
                        icon: const Icon(Icons.home, size: 24),
                        label: const Text('Home'),
                      ),
                      NavigationRailDestination(
                        icon: const Icon(Icons.lightbulb_outline, size: 24),
                        label: const Text('My Strategies'),
                      ),
                    ],
                    selectedIndex: _selectedIndex,
                    onDestinationSelected: (idx) =>
                        setState(() => _selectedIndex = idx),
                  )
                : const SizedBox.shrink(),
          ),
          Expanded(
            child: isDesktop
                ? _getContent(_selectedIndex)
                : Scaffold(
                    appBar: AppBar(
                      title: const Text('Sattva'),
                      backgroundColor: Colors.grey[900],
                    ),
                    drawer: Drawer(
                      child: Column(
                        children: [
                          const SizedBox(height: 32),
                          CircleAvatar(
                            radius: 24,
                            backgroundColor: Colors.deepPurple,
                            child: const Icon(
                              Icons.show_chart,
                              color: Colors.white,
                              size: 28,
                            ),
                          ),
                          const SizedBox(height: 8),
                          const Text(
                            'Sattva',
                            style: TextStyle(
                              fontSize: 20,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                          const Divider(),
                          ListTile(
                            leading: const Icon(Icons.home, size: 24),
                            title: const Text('Home'),
                            selected: _selectedIndex == 0,
                            onTap: () {
                              setState(() => _selectedIndex = 0);
                              Navigator.pop(context);
                            },
                          ),
                          ListTile(
                            leading: const Icon(
                              Icons.lightbulb_outline,
                              size: 24,
                            ),
                            title: const Text('My Strategies'),
                            selected: _selectedIndex == 1,
                            onTap: () {
                              setState(() => _selectedIndex = 1);
                              Navigator.pop(context);
                            },
                          ),
                        ],
                      ),
                    ),
                    body: _getContent(_selectedIndex),
                  ),
          ),
        ],
      ),
    );
  }
}
