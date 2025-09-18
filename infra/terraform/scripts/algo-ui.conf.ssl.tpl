# Redirect all HTTP to HTTPS
server {
    listen ${algo_ui_port};
    server_name ${algo_domain_name};
    
    location / {
        return 301 https://$host$request_uri;
    }
}

server {
    listen 443 ssl;
    server_name ${algo_domain_name};

    ssl_certificate /etc/letsencrypt/live/${algo_domain_name}/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/${algo_domain_name}/privkey.pem;

    # Serve Flutter Web
    root /var/www/algo-ui;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    # Proxy API calls to Flask + Waitress
    location /api/ {
        proxy_pass http://127.0.0.1:5000/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}