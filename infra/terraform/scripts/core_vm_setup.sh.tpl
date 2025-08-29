#!/bin/bash
# Example setup script for core_vm

# Script to upgrade Python to 3.11 on Oracle Linux 8

set -e

# Function to extract major.minor version of python3
get_python_version() {
    python3 --version 2>/dev/null | awk '{print $2}' | cut -d. -f1,2
}

check_and_install_git() {
    if ! command -v git &>/dev/null; then
        echo "Git not found. Installing..."
        sudo dnf install git -y
        if [ $? -eq 0 ]; then
            echo "Git installed successfully."
        else
            echo "Failed to install Git."
            exit 1
        fi
    else
        echo "Git is already installed."
    fi
}

# Function to upgrade Python to 3.11
upgrade_python_to_311() {
    CURRENT_VERSION=$(get_python_version)
    echo "🔍 Current Python3 version: $${CURRENT_VERSION:-not installed}"

    if [[ "$CURRENT_VERSION" == "3.11" ]]; then
        echo "✅ Python 3.11 is already installed and set as default."
        return 0
    fi

    echo "🚀 Upgrading to Python 3.11..."

    # Install Python 3.11
    sudo dnf install -y python3.11

    # Set python3 alternative to point to python3.11
    if [ -x "/usr/bin/python3.11" ]; then
        sudo alternatives --install /usr/bin/python3 python3 /usr/bin/python3.11 2
        sudo alternatives --set python3 /usr/bin/python3.11
    else
        echo "❌ python3.11 binary not found after installation."
        exit 1
    fi

    NEW_VERSION=$(get_python_version)
    echo "🎉 Upgrade complete. Current Python3 version: $NEW_VERSION"
}

copy_app() {
    echo "📦 Copying application files..."
    sudo rm -rf /opt/algo-core
    sudo mkdir -p /opt/algo-core
    sudo cp -r algo-engine/components/algo_core/* /opt/algo-core/
    sudo chown -R $(whoami):$(whoami) /opt/algo-core
}

config_app() {
    echo "📦 Copying application files..."
    sudo rm -rf /etc/algo-core
    sudo mkdir -p /etc/algo-core
    sudo chown -R $(whoami):$(whoami) /opt/algo-core
    copy_data
    copy_strategies
    copy_config_json
    copy_env_file
    copy_service_file
}

copy_data() {
    echo "📦 Copying data files..."
    DATA_DIR="/etc/algo-core/data"
    sudo mkdir -p "$DATA_DIR"
    sudo cp -r algo-engine/data/* "$DATA_DIR"
    sudo chown -R $(whoami):$(whoami) "$DATA_DIR"
}

copy_config_json() {
  CONFIG_DIR="/etc/algo-core"
  CONFIG_FILE="$CONFIG_DIR/config.json"

  # Write JSON content
  sudo tee "$CONFIG_FILE" > /dev/null << 'EOF'
{
  "backtest_engine": {
    "historical_data_backend": "PARQUET_FILES",
    "reports_dir": "/etc/algo-core/reports",
    "parquet_files_base_dir": "/etc/algo-core/data",
    "strategy_json_config_dir": "/etc/algo-core/strategies"
  }
}
EOF
  sudo chown  $(whoami):$(whoami) "$CONFIG_FILE"
  echo "✅ Config file created at $CONFIG_FILE"
}

copy_env_file() {
  CONFIG_DIR="/etc/algo-core"
  ENV_FILE="$CONFIG_DIR/algo-core.env"

  # Write JSON content
  sudo tee "$ENV_FILE" > /dev/null << 'EOF'
CONFIG_JSON_PATH=/etc/algo-core/config.json
EOF
  sudo chown  $(whoami):$(whoami) "$ENV_FILE"
  echo "✅ Config file created at $ENV_FILE"
}

copy_service_file() {
  SERVICE_FILE="/etc/systemd/system/algo-core.service"

  sudo cp  algo-engine/infra/terraform/scripts/algo-core.service $SERVICE_FILE
  sudo chown  root:root "$SERVICE_FILE"
  sudo chmod 644 "$SERVICE_FILE"
  echo "✅ Service file created at $SERVICE_FILE"
}

copy_strategies() {
    echo "📦 Copying strategies files..."
    STRATEGIES_DIR="/etc/algo-core/strategies"
    sudo mkdir -p "$STRATEGIES_DIR"
    sudo cp -r algo-engine/strategies/* "$STRATEGIES_DIR"
    sudo chown -R $(whoami):$(whoami) "$STRATEGIES_DIR"
}

deploy_app() {
    cd /opt/algo-core
    echo "🔧 Creating Python virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
    echo "📦 Installing dependencies..."
    python -m pip install --upgrade pip
    python -m pip install .
    echo "✅ core_api deployment complete."
}

start_app() {
    cd /opt/algo-core
    echo "🚀 Starting core API service..."
    # Assuming a systemd service file named algo-core.service is set up
    env CONFIG_JSON_PATH=/etc/algo-core/config.json \
    waitress-serve --host=0.0.0.0 --port=5000 src.algo_core.app:app
}

# Function to deploy core API
setup_core_api() {
    echo "🚀 Deploying core API from repository: ${git_repository} (branch: ${branch})"
    cd /tmp
    rm -rf algo-engine
    git clone --branch "${branch}" "${git_repository}" algo-engine

    copy_app
    config_app
    deploy_app
   
}

# --- Main Script ---
upgrade_python_to_311
check_and_install_git
setup_core_api
