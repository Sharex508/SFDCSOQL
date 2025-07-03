# Salesforce Metadata Service Deployment Guide

This guide provides instructions for deploying the Salesforce Metadata Service to AWS EC2.

## Overview

The Salesforce Metadata Service consists of two main components:

1. **salesforce_metadata_service.py** - A command-line tool for retrieving Salesforce metadata and exporting it to an Excel file
2. **salesforce_metadata_api.py** - A Flask web service that exposes an API for retrieving Salesforce metadata

This guide focuses on deploying the Flask web service to AWS EC2.

## Prerequisites

- An AWS account with permissions to create and manage EC2 instances
- Basic knowledge of AWS EC2 and security groups
- A Salesforce account with API access enabled
- A Salesforce Connected App with OAuth credentials (client ID and client secret)

## Step 1: Set Up an EC2 Instance

1. Log in to the AWS Management Console and navigate to the EC2 dashboard
2. Click "Launch Instance"
3. Choose an Amazon Machine Image (AMI) - Amazon Linux 2 or Ubuntu Server are recommended
4. Choose an instance type (t2.micro is sufficient for testing)
5. Configure instance details as needed
6. Add storage (default is usually sufficient)
7. Add tags (optional)
8. Configure security group:
   - Allow SSH (port 22) from your IP address
   - Allow HTTP (port 80) from anywhere
   - Allow HTTPS (port 443) from anywhere
   - Allow custom TCP (port 5000) from anywhere (or restrict to specific IPs)
9. Review and launch the instance
10. Create or select an existing key pair for SSH access

## Step 2: Connect to the EC2 Instance

```bash
ssh -i /path/to/your-key.pem ec2-user@your-instance-public-dns
```

Replace `/path/to/your-key.pem` with the path to your key pair file and `your-instance-public-dns` with your instance's public DNS name.

## Step 3: Install Required Software

### For Amazon Linux 2:

```bash
# Update the system
sudo yum update -y

# Install Python 3 and pip
sudo yum install python3 python3-pip -y

# Install git
sudo yum install git -y
```

### For Ubuntu Server:

```bash
# Update the system
sudo apt update && sudo apt upgrade -y

# Install Python 3 and pip
sudo apt install python3 python3-pip -y

# Install git
sudo apt install git -y
```

## Step 4: Clone the Repository

```bash
# Clone the repository
git clone https://github.com/yourusername/sfdcsoql.git
cd sfdcsoql

# Install dependencies
pip3 install -r requirements.txt
```

## Step 5: Test the Service Locally

```bash
# Test the command-line tool
python3 salesforce_metadata_service.py --help

# Test the API service
python3 salesforce_metadata_api.py --host 127.0.0.1 --port 5000 --debug
```

## Step 6: Set Up the Service to Run Continuously

### Option 1: Using systemd (recommended)

Create a systemd service file:

```bash
sudo nano /etc/systemd/system/salesforce-metadata-api.service
```

Add the following content:

```
[Unit]
Description=Salesforce Metadata API Service
After=network.target

[Service]
User=ec2-user
WorkingDirectory=/home/ec2-user/sfdcsoql
ExecStart=/usr/bin/python3 /home/ec2-user/sfdcsoql/salesforce_metadata_api.py --host 0.0.0.0 --port 5000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start the service:

```bash
sudo systemctl daemon-reload
sudo systemctl enable salesforce-metadata-api
sudo systemctl start salesforce-metadata-api
sudo systemctl status salesforce-metadata-api
```

### Option 2: Using screen

```bash
# Install screen
sudo yum install screen -y  # For Amazon Linux 2
# or
sudo apt install screen -y  # For Ubuntu

# Start a new screen session
screen -S salesforce-api

# Run the service
python3 salesforce_metadata_api.py --host 0.0.0.0 --port 5000

# Detach from the screen session by pressing Ctrl+A, then D
```

## Step 7: Set Up a Domain Name (Optional)

1. Register a domain name using Route 53 or another domain registrar
2. Create a DNS record pointing to your EC2 instance's public IP address

## Step 8: Set Up HTTPS with Let's Encrypt (Optional)

```bash
# Install certbot
sudo yum install certbot -y  # For Amazon Linux 2
# or
sudo apt install certbot python3-certbot-nginx -y  # For Ubuntu

# Get a certificate
sudo certbot --nginx -d yourdomain.com
```

## Step 9: Set Up Nginx as a Reverse Proxy (Optional)

### For Amazon Linux 2:

```bash
# Install nginx
sudo amazon-linux-extras install nginx1 -y
sudo systemctl start nginx
sudo systemctl enable nginx
```

### For Ubuntu:

```bash
# Install nginx
sudo apt install nginx -y
sudo systemctl start nginx
sudo systemctl enable nginx
```

Create an Nginx configuration file:

```bash
sudo nano /etc/nginx/conf.d/salesforce-metadata-api.conf
```

Add the following content:

```
server {
    listen 80;
    server_name yourdomain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Test and reload Nginx:

```bash
sudo nginx -t
sudo systemctl reload nginx
```

## Using the API

### Health Check

```bash
curl http://your-instance-public-dns:5000/health
```

### Get List of Objects

```bash
curl -X POST \
  http://your-instance-public-dns:5000/api/objects \
  -H 'Content-Type: application/json' \
  -d '{
    "username": "your-username",
    "password": "your-password",
    "security_token": "your-security-token",
    "client_id": "your-client-id",
    "client_secret": "your-client-secret"
}'
```

### Get Metadata for Specific Objects

```bash
curl -X POST \
  http://your-instance-public-dns:5000/api/metadata \
  -H 'Content-Type: application/json' \
  -d '{
    "username": "your-username",
    "password": "your-password",
    "security_token": "your-security-token",
    "client_id": "your-client-id",
    "client_secret": "your-client-secret",
    "objects": ["Account", "Contact"]
}' \
  -o Salesforce_Complete_Metadata.xlsx
```

## Security Considerations

1. **Credential Management**: Never hardcode credentials in your code. Consider using AWS Secrets Manager or environment variables.
2. **IP Restrictions**: Restrict access to your API by configuring the EC2 security group to allow connections only from trusted IP addresses.
3. **HTTPS**: Always use HTTPS in production to encrypt data in transit.
4. **API Authentication**: Consider adding an authentication mechanism to your API (e.g., API keys or JWT tokens).

## Monitoring and Maintenance

1. **Logs**: Check the service logs for errors:
   ```bash
   sudo journalctl -u salesforce-metadata-api
   ```

2. **Updates**: Regularly update the system and dependencies:
   ```bash
   sudo yum update -y  # For Amazon Linux 2
   # or
   sudo apt update && sudo apt upgrade -y  # For Ubuntu
   
   pip3 install --upgrade -r requirements.txt
   ```

3. **Backup**: Regularly backup your code and configuration files.

## Troubleshooting

1. **Service not starting**: Check the logs for errors:
   ```bash
   sudo journalctl -u salesforce-metadata-api
   ```

2. **Cannot connect to the API**: Check if the service is running and the security group is properly configured:
   ```bash
   sudo systemctl status salesforce-metadata-api
   ```

3. **Authentication errors**: Verify your Salesforce credentials and ensure your Connected App is properly configured.