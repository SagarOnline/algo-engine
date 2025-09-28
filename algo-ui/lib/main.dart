import 'package:flutter/material.dart';
import 'package:google_sign_in/google_sign_in.dart'; // <-- added
import 'my_strategies.dart';

// GoogleSignIn instance
final GoogleSignIn _googleSignIn = GoogleSignIn(); // <-- added

void main() {
  runApp(const AlgoApp());
}

class AlgoApp extends StatelessWidget {
  const AlgoApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Sutram',
      theme: ThemeData.dark().copyWith(
        colorScheme: ColorScheme.dark(
          primary: Colors.deepPurple,
          secondary: Colors.amber,
        ),
        scaffoldBackgroundColor: Colors.black,
      ),
      home: const LoginPage(), // <-- changed from AlgoHome to LoginPage
      debugShowCheckedModeBanner: false,
    );
  }
}

// --- Added LoginPage for Google Sign-In ---
class LoginPage extends StatefulWidget {
  const LoginPage({super.key});

  @override
  State<LoginPage> createState() => _LoginPageState();
}

class _LoginPageState extends State<LoginPage> {
  bool _isSigningIn = false;
  String? _error;

  Future<void> _handleSignIn() async {
    setState(() {
      _isSigningIn = true;
      _error = null;
    });
    try {
      final account = await _googleSignIn.signIn();
      if (account != null) {
        // Successful sign in, navigate to AlgoHome
        if (!mounted) return;
        Navigator.pushReplacement(
          context,
          MaterialPageRoute(builder: (context) => const AlgoHome()),
        );
      } else {
        setState(() {
          _error = "Sign in aborted by user.";
        });
      }
    } catch (error) {
      setState(() {
        _error = "Sign in failed: $error";
      });
    } finally {
      setState(() {
        _isSigningIn = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.black,
      body: Center(
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: 32.0),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              const Icon(Icons.show_chart, color: Colors.deepPurple, size: 64),
              const SizedBox(height: 24),
              const Text(
                'Welcome to Sutram',
                style: TextStyle(fontSize: 28, fontWeight: FontWeight.bold),
              ),
              const SizedBox(height: 32),
              _isSigningIn
                  ? const CircularProgressIndicator()
                  : ElevatedButton.icon(
                      style: ElevatedButton.styleFrom(
                        backgroundColor: Colors.white,
                        foregroundColor: Colors.black,
                        minimumSize: const Size(double.infinity, 48),
                      ),
                      icon: Image.asset(
                        'assets/images/google_logo.png',
                        height: 24,
                        width: 24,
                      ),
                      label: const Text('Sign-in with Google'),
                      onPressed: _handleSignIn,
                    ),
              if (_error != null) ...[
                const SizedBox(height: 16),
                Text(
                  _error!,
                  style: const TextStyle(color: Colors.red),
                  textAlign: TextAlign.center,
                ),
              ],
            ],
          ),
        ),
      ),
    );
  }
}
// --- End LoginPage ---

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
            'Welcome to Sutram Home!',
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
                            'Sutram',
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
                      title: const Text('Sutram'),
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
                            'Sutram',
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
