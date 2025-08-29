# EC2 Deployment Guide for Botasaurus API

## Quick Start

### 1. Set up EC2 Instance (Following your guide)
```bash
# Create EC2 instance: Ubuntu 24.04, t3.medium
# Reserve and associate Elastic IP
# Enable HTTP/HTTPS in security groups
```

### 2. Install Base Requirements on EC2
```bash
# SSH into your EC2 instance
curl -sL https://raw.githubusercontent.com/omkarcloud/botasaurus/master/vm-scripts/install-bota-desktop.sh | bash

# Install Botasaurus desktop app
python3 -m bota install-desktop-app --debian-installer-url YOUR_DEBIAN_INSTALLER_URL --custom-args "--auth-token YOUR_AUTH_TOKEN"
```

### 3. Deploy Your API
```bash
# On your local machine:
# 1. Update deploy-to-ec2.sh with your EC2 IP and key file path
# 2. Run deployment
./deploy-to-ec2.sh
```

### 4. Configure Apache Proxy (on EC2)
```bash
# Create Apache virtual host
sudo tee /etc/apache2/sites-available/botasaurus-api.conf << EOF
<VirtualHost *:80>
    ProxyPreserveHost On
    ProxyRequests Off
    ProxyPass /api/ http://localhost:3000/
    ProxyPassReverse /api/ http://localhost:3000/
    
    # Health check directly accessible
    ProxyPass /health http://localhost:3000/health
    ProxyPassReverse /health http://localhost:3000/health
</VirtualHost>
EOF

# Enable site and restart Apache
sudo a2ensite botasaurus-api.conf
sudo systemctl reload apache2
```

## API Endpoints

- `GET /health` - Health check
- `POST /scrape` - Main scraping endpoint

### Example Request
```bash
curl -X POST http://YOUR_ELASTIC_IP/scrape \
  -H "Content-Type: application/json" \
  -d '{
    "queries": ["restaurants in New York"],
    "max_results": 50,
    "enable_reviews_extraction": true
  }'
```

### Example Response
```json
{
  "success": true,
  "result_count": 50,
  "data": [
    {
      "name": "Restaurant Name",
      "address": "123 Main St",
      "phone": "+1-234-567-8900",
      "rating": 4.5,
      "reviews": 250
    }
  ]
}
```

## Files Structure
```
.
├── server.js              # Express API server
├── package.json           # Dependencies
├── deploy-to-ec2.sh      # Deployment script
└── README-EC2-Deployment.md
```

That's it! Simple deployment without over-engineering.