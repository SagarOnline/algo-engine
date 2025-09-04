server {
    listen ${algo_ui_port};
    server_name ${algo_ui_host};

    # Serve Flutter Web
    root /var/www/algo-ui;
    index index.html;

    location / {
        try_files $uri /index.html;
    }

    # Proxy API calls to Flask + Waitress
    location /api/ {
        proxy_pass http://127.0.0.1:5000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
