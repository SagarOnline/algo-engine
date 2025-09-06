[Unit]
Description=Algo API Python Web App (Waitress)
After=network.target

[Service]
User=opc
Group=opc
WorkingDirectory=/opt/algo-api
EnvironmentFile=/etc/algo-api/algo-api.env
ExecStart=/opt/algo-api/venv/bin/waitress-serve \
    --host=0.0.0.0 \
    --port=${algo_api_port} \
    src.algo.app:app

# Redirect stdout/stderr to a log file
StandardOutput=append:/var/log/algo-api/algo-api.log
StandardError=append:/var/log/algo-api/algo-api.log

# Restart on failure
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
