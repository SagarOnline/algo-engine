#!/bin/bash
# Example setup script for core_vm

# Script to upgrade Python to 3.11 on Oracle Linux 8

set -e

# Function to extract major.minor version of python3
get_python_version() {
    python3 --version 2>/dev/null | awk '{print $2}' | cut -d. -f1,2
}

# Function to upgrade Python to 3.11
upgrade_python_to_311() {
    CURRENT_VERSION=$(get_python_version)
    echo "🔍 Current Python3 version: ${CURRENT_VERSION:-not installed}"

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


# Function to deploy core API
deploy_core_api() {
    echo "🚀 Deploying core API from repository: ${git_repository} (branch: ${branch})"
    cd /tmp
    rm -rf algo-engine
    git clone --branch "${branch}" "${git_repository}" algo-engine
    cd algo-engine/components/algo_core
    echo "🔧 Creating Python virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
    echo "📦 Installing dependencies..."
    python -m pip install --upgrade pip
    python -m pip install .
    echo "✅ core_api deployment complete."
}

# --- Main Script ---
upgrade_python_to_311
deploy_core_api
