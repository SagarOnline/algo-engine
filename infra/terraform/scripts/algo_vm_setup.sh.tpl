#!/bin/bash

# Script to upgrade Python to 3.11 on Oracle Linux 8

set -e

# Function to extract major.minor version of python3
get_python_version() {
    python3 --version 2>/dev/null | awk '{print $2}' | cut -d. -f1,2
}

open_firewall_port() {
    PORT=$1
    PROTOCOL=$${2:-tcp}  # Default protocol is tcp

    if [ -z "$PORT" ]; then
        echo "Usage: open_firewall_port <port> [protocol]"
        return 1
    fi

    # Check if port is already open
    if sudo firewall-cmd --list-ports | grep -q "$PORT/$PROTOCOL"; then
        echo "Port $PORT/$PROTOCOL is already open."
    else
        echo "Opening port $PORT/$PROTOCOL permanently..."
        sudo firewall-cmd --permanent --add-port=$PORT/$PROTOCOL
        sudo firewall-cmd --reload
        echo "Port $PORT/$PROTOCOL opened successfully."
    fi
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

copy_algo_api() {
    echo "📦 Copying application files..."
    APP_DIR="/opt/algo-api"
    sudo rm -rf "$APP_DIR"
    sudo mkdir -p "$APP_DIR"
    sudo cp -r algo-engine/algo-api/* "$APP_DIR/"
    sudo chown -R $(whoami):$(whoami) "$APP_DIR"
}

configure_algo_api() {
    echo "📦 Copying application files..."

    # config direcotory
    CONFIG_DIR="/etc/algo-api"
    sudo rm -rf "$CONFIG_DIR"
    sudo mkdir -p "$CONFIG_DIR"
    sudo chown -R $(whoami):$(whoami) "$CONFIG_DIR"

    # log directory
    LOG_DIR="/var/log/algo-api"
    sudo rm -rf "$LOG_DIR"
    sudo mkdir -p "$LOG_DIR"
    sudo chown -R $(whoami):$(whoami) "$LOG_DIR"
    sudo chmod 755 "$LOG_DIR"

    configure_algo_api_data
    configure_algo_api_strategies
    configure_algo_api_config_json
    configure_algo_api_env_file
    configure_algo_api_service_file
}

configure_algo_api_data() {
    echo "📦 Copying data files..."
    DATA_DIR="/etc/algo-api/data"
    sudo mkdir -p "$DATA_DIR"
    sudo cp -r algo-engine/data/* "$DATA_DIR"
    sudo chown -R $(whoami):$(whoami) "$DATA_DIR"
}

configure_algo_api_config_json() {
  CONFIG_DIR="/etc/algo-api"
  CONFIG_FILE="$CONFIG_DIR/config.json"

  # Write JSON content
  sudo tee "$CONFIG_FILE" > /dev/null << 'EOF'
{
  "backtest_engine": {
    "historical_data_backend": "PARQUET_FILES",
    "reports_dir": "/etc/algo-api/reports",
    "parquet_files_base_dir": "/etc/algo-api/data",
    "strategy_json_config_dir": "/etc/algo-api/strategies"
  }
}
EOF
  sudo chown  $(whoami):$(whoami) "$CONFIG_FILE"
  echo "✅ Config file created at $CONFIG_FILE"
}

configure_algo_api_env_file() {
  CONFIG_DIR="/etc/algo-api"
  ENV_FILE="$CONFIG_DIR/algo-api.env"

  # Write JSON content
  sudo tee "$ENV_FILE" > /dev/null << 'EOF'
CONFIG_JSON_PATH=/etc/algo-api/config.json
EOF
  sudo chown  $(whoami):$(whoami) "$ENV_FILE"
  echo "✅ Config file created at $ENV_FILE"
}

configure_algo_api_service_file() {
  SERVICE_FILE="/etc/systemd/system/algo-api.service"

  sudo cp  /tmp/algo-api.service $SERVICE_FILE
  sudo dos2unix $SERVICE_FILE
  sudo chown  root:root "$SERVICE_FILE"
  sudo chmod 644 "$SERVICE_FILE"
  echo "✅ Service file created at $SERVICE_FILE"
}

configure_algo_api_strategies() {
    echo "📦 Copying strategies files..."
    STRATEGIES_DIR="/etc/algo-api/strategies"
    sudo mkdir -p "$STRATEGIES_DIR"
    sudo cp -r algo-engine/strategies/* "$STRATEGIES_DIR"
    sudo chown -R $(whoami):$(whoami) "$STRATEGIES_DIR"
}

deploy_algo_api() {
    cd /opt/algo-api
    echo "🔧 Creating Python virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
    echo "📦 Installing dependencies..."
    python -m pip install --upgrade pip
    python -m pip install .
    echo "✅ algo_api deployment complete."
}

restart_algo_api_service() {
    echo "🔄 Restarting algo API service..."
    sudo systemctl daemon-reload
    sudo systemctl enable algo-api.service
    sudo systemctl restart algo-api.service
    echo "✅ Algo API service restarted."
}

clone_repo() {
    echo "🚀 Cloning repository: ${git_repository} (branch: ${branch})"
    cd /tmp
    rm -rf algo-engine
    git clone --branch "${branch}" "${git_repository}" algo-engine
}

# Function to deploy algo API
setup_algo_api() {
    upgrade_python_to_311
    echo "🚀 Deploying algo API from repository: ${git_repository} (branch: ${branch})"
    
    copy_algo_api
    configure_algo_api
    deploy_algo_api
    restart_algo_api_service
    open_firewall_port ${algo_api_port}
}


install_nginx() {
        # Check if nginx is installed
    if ! rpm -q nginx &> /dev/null; then
        echo "Nginx not found. Installing..."
        
        # Install nginx
        sudo dnf -y install nginx
        sudo systemctl enable nginx
        sudo systemctl start nginx
    else
        echo "Nginx is already installed."
    fi

    # Print nginx version
    nginx -v
}

copy_algo_ui() {
    echo "📦 Copying application files..."
    APP_DIR="/var/www/algo-ui"
    sudo rm -rf "$APP_DIR"
    sudo mkdir -p "$APP_DIR"
    sudo cp -r /tmp/algo-engine/algo-ui/build/web/* "$APP_DIR/"
    
    # Allow Nginx to serve content from this directory
    sudo semanage fcontext -a -t httpd_sys_content_t "$APP_DIR(/.*)?"
    sudo restorecon -Rv "$APP_DIR"

    # allow Nginx to connect to network on 127.0.0.1 to forward API requests
    sudo setsebool -P httpd_can_network_connect 1
    
}

configure_algo_ui() {
    CONF_FILE="/etc/nginx/conf.d/algo-ui.conf"

    sudo cp  /tmp/algo-ui.conf $CONF_FILE
    sudo dos2unix $CONF_FILE
    sudo nginx -t
    sudo systemctl restart nginx
    echo "✅ Nginx configuration reloaded."
}


# Function to deploy algo UI
setup_algo_ui() {
    install_nginx
    copy_algo_ui
    configure_algo_ui
    open_firewall_port ${algo_ui_port}
}

download_github_artifact() {
  repo=$1             # e.g. user/algo-engine
  release_version=$2  # e.g. v1.0.0
  asset_name=$3       # e.g. algo-ui

  if [ -z "$repo" ] || [ -z "$release_version" ] || [ -z "$asset_name" ]; then
    echo "Usage: download_github_artifact <repo> <release_version> <asset_name>"
    return 1
  fi

  echo "🔎 Fetching release: $release_version for repo: $repo"

  # Get release info for the given tag
  release_json=$(curl -sL \
    -H "Accept: application/vnd.github+json" \
    "https://api.github.com/repos/$repo/releases/tags/$release_version")

  # Extract asset download URL that matches asset_name
  asset_url=$(echo "$release_json" | jq -r ".assets[] | select(.name | contains(\"$asset_name\")) | .browser_download_url")
  echo $asset_url
  if [ -z "$asset_url" ] || [ "$asset_url" == "null" ]; then
    echo "❌ No asset found with name containing '$asset_name' in release $release_version"
    return 1
  fi

  echo "  Downloading asset: $asset_name.zip from release $release_version"

  # Download asset (requires GitHub token if repo is private)
  curl -L \
    -H "Accept: application/octet-stream" \
    -H "Authorization: Bearer ${GITHUB_TOKEN:-}" \
    "$asset_url" -o "$asset_name.zip"

  echo "✅ Saved as $asset_name.zip"
}

# --- Main Script ---

check_and_install_git
clone_repo
setup_algo_api
setup_algo_ui
