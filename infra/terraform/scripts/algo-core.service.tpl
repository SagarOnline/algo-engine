[Unit]
Description=Algo Core Python Web App (Waitress)
After=network.target

[Service]
User=opc
Group=opc
WorkingDirectory=/opt/algo-core
EnvironmentFile=/etc/algo-core/algo-core.env
ExecStart=/opt/algo-core/venv/bin/waitress-serve \
    --host=0.0.0.0 \
    --port=${core_api_port} \
    src.algo_core.app:app

# Redirect stdout/stderr to a log file
StandardOutput=append:/var/log/algo-core/algo-core.log
StandardError=append:/var/log/algo-core/algo-core.log

# Restart on failure
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
