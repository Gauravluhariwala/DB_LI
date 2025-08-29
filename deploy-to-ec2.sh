#!/bin/bash

# Simple EC2 Deployment Script for Botasaurus API
set -e

# Configuration - Replace with your values
EC2_IP="YOUR_ELASTIC_IP_HERE"
EC2_USER="ubuntu"
KEY_FILE="path/to/your-key.pem"

echo "🚀 Deploying Botasaurus API to EC2..."

# Copy files to EC2
echo "📦 Uploading files to EC2..."
scp -i "$KEY_FILE" -o StrictHostKeyChecking=no \
    server.js package.json \
    "$EC2_USER@$EC2_IP:/home/ubuntu/"

# Install dependencies and start server
echo "🔧 Installing dependencies and starting server..."
ssh -i "$KEY_FILE" -o StrictHostKeyChecking=no "$EC2_USER@$EC2_IP" << 'ENDSSH'
    # Install Node.js if not present
    if ! command -v node &> /dev/null; then
        curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
        sudo apt-get install -y nodejs
    fi
    
    # Install dependencies
    npm install
    
    # Stop any existing process
    pkill -f "node server.js" || true
    
    # Start server in background
    nohup npm start > api.log 2>&1 &
    
    echo "✅ API server started on port 3000"
    echo "🌐 Access your API at: http://$EC2_IP/health"
ENDSSH

echo "🎉 Deployment complete!"
echo "📋 Next steps:"
echo "   1. Configure Apache to proxy to port 3000"
echo "   2. Test API: curl http://$EC2_IP/health"
echo "   3. Test scraping: curl -X POST http://$EC2_IP/scrape -H 'Content-Type: application/json' -d '{\"queries\":[\"restaurants in NYC\"]}'"