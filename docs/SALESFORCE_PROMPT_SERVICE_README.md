# Salesforce Prompt Service

This service allows you to receive natural language prompts from Salesforce and generate SOQL queries using the SOQLQueryGenerator.

## Overview

The Salesforce Prompt Service is a Flask web service that exposes an API to receive natural language prompts and generate SOQL queries. It uses the SOQLQueryGenerator from the nlp_model.py file to process the prompts and generate the queries.

## Prerequisites

- Python 3.6 or higher
- Salesforce metadata files (generated using generate_metadata.py)
- Required Python packages (see `requirements.txt`)

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/sfdcsoql.git
   cd sfdcsoql
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Generate metadata files (if not already done):
   ```bash
   python generate_metadata.py --excel-file Salesforce_Complete_Metadata.xlsx --output-dir data/metadata
   ```

## Usage

### Starting the Service

```bash
python salesforce_prompt_service.py --host <host> --port <port> --metadata-dir <metadata_dir>
```

### Arguments

- `--host`: Host to bind the service to (default: "0.0.0.0")
- `--port`: Port to bind the service to (default: 5000)
- `--metadata-dir`: Directory containing metadata files (default: "data/metadata")
- `--debug`: Run in debug mode (optional)

### Example

```bash
python salesforce_prompt_service.py --host 0.0.0.0 --port 5000 --metadata-dir data/metadata
```

## API Endpoints

### Health Check

```
GET /health
```

Response:
```json
{
  "status": "healthy",
  "message": "Salesforce Prompt Service is running",
  "metadata_loaded": true
}
```

### Generate Query

```
POST /api/generate-query
```

Request body:
```json
{
  "prompt": "Get all Accounts with Name and Industry"
}
```

Response:
```json
{
  "prompt": "Get all Accounts with Name and Industry",
  "query": "SELECT Name, Industry FROM Account"
}
```

### Batch Generate Queries

```
POST /api/batch-generate
```

Request body:
```json
{
  "prompts": [
    "Get all Accounts with Name and Industry",
    "Find Contacts in California"
  ]
}
```

Response:
```json
{
  "results": [
    {
      "prompt": "Get all Accounts with Name and Industry",
      "query": "SELECT Name, Industry FROM Account"
    },
    {
      "prompt": "Find Contacts in California",
      "query": "SELECT Id, FirstName, LastName FROM Contact WHERE MailingState = 'CA'"
    }
  ],
  "errors": [],
  "total": 2,
  "successful": 2,
  "failed": 0
}
```

## Example API Usage with curl

```bash
# Health check
curl http://localhost:5000/health

# Generate a query
curl -X POST \
  http://localhost:5000/api/generate-query \
  -H 'Content-Type: application/json' \
  -d '{
    "prompt": "Get all Accounts with Name and Industry"
  }'

# Batch generate queries
curl -X POST \
  http://localhost:5000/api/batch-generate \
  -H 'Content-Type: application/json' \
  -d '{
    "prompts": [
      "Get all Accounts with Name and Industry",
      "Find Contacts in California"
    ]
  }'
```

## Deployment to AWS EC2

For deploying the Salesforce Prompt Service to AWS EC2, follow these steps:

1. Set up an EC2 instance with Amazon Linux 2 or Ubuntu Server.
2. Install Python 3 and required dependencies.
3. Clone the repository and install the Python packages.
4. Generate metadata files or copy them from another source.
5. Set up the service to run continuously using systemd or screen.
6. Configure security groups to allow traffic on the desired port.

For detailed deployment instructions, see the [Deployment Guide](DEPLOYMENT_GUIDE.md).

### Quick EC2 Setup

```bash
# Update the system
sudo yum update -y  # For Amazon Linux 2
# or
sudo apt update && sudo apt upgrade -y  # For Ubuntu

# Install Python 3 and pip
sudo yum install python3 python3-pip -y  # For Amazon Linux 2
# or
sudo apt install python3 python3-pip -y  # For Ubuntu

# Install git
sudo yum install git -y  # For Amazon Linux 2
# or
sudo apt install git -y  # For Ubuntu

# Clone the repository
git clone https://github.com/yourusername/sfdcsoql.git
cd sfdcsoql

# Install dependencies
pip3 install -r requirements.txt

# Start the service
python3 salesforce_prompt_service.py --host 0.0.0.0 --port 5000 --metadata-dir data/metadata
```

### Setting Up as a Systemd Service

Create a systemd service file:

```bash
sudo nano /etc/systemd/system/salesforce-prompt-service.service
```

Add the following content:

```
[Unit]
Description=Salesforce Prompt Service
After=network.target

[Service]
User=ec2-user
WorkingDirectory=/home/ec2-user/sfdcsoql
ExecStart=/usr/bin/python3 /home/ec2-user/sfdcsoql/salesforce_prompt_service.py --host 0.0.0.0 --port 5000 --metadata-dir data/metadata
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start the service:

```bash
sudo systemctl daemon-reload
sudo systemctl enable salesforce-prompt-service
sudo systemctl start salesforce-prompt-service
sudo systemctl status salesforce-prompt-service
```

## Security Considerations

- Never hardcode credentials in your code
- Use HTTPS in production to encrypt data in transit
- Consider adding authentication to the API
- Restrict access to the API by IP address

## Troubleshooting

### Common Issues

1. **Metadata Not Loaded**: Ensure the metadata directory exists and contains valid metadata files.
2. **Service Not Starting**: Check the logs for errors and ensure the required dependencies are installed.
3. **Cannot Connect to the API**: Check if the service is running and the security group is properly configured.

### Debugging

For more detailed logging, run the service in debug mode:

```bash
python salesforce_prompt_service.py --debug
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.