# Salesforce Combined Service

This service combines the Salesforce Prompt Service and Salesforce Metadata API into a single service running on one port.

## Overview

The Salesforce Combined Service provides a unified interface for:

1. Generating SOQL queries from natural language prompts
2. Retrieving Salesforce metadata for objects and fields

By combining these services, you can deploy a single application that handles both query generation and metadata retrieval, simplifying your infrastructure and deployment process.

## Prerequisites

- Python 3.6 or higher
- Salesforce metadata files (generated using generate_metadata.py)
- Salesforce account with API access enabled (for metadata retrieval)
- Salesforce Connected App with OAuth credentials (client ID and client secret)
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
   python src/services/generate_metadata.py --excel-file Salesforce_Complete_Metadata.xlsx --output-dir data/metadata
   ```

## Usage

### Starting the Service

```bash
python src/services/salesforce_combined_service.py --host <host> --port <port> --metadata-dir <metadata_dir>
```

### Arguments

- `--host`: Host to bind the service to (default: "0.0.0.0")
- `--port`: Port to bind the service to (default: 5000)
- `--metadata-dir`: Directory containing metadata files (default: "data/metadata")
- `--debug`: Run in debug mode (optional)

### Example

```bash
python src/services/salesforce_combined_service.py --host 0.0.0.0 --port 5000 --metadata-dir data/metadata
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
  "message": "Salesforce Combined Service is running",
  "metadata_loaded": true
}
```

### Prompt Service Endpoints

#### Generate Query

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

#### Batch Generate Queries

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

### Metadata API Endpoints

#### Get List of Objects

```
POST /api/objects
```

Request body:
```json
{
  "username": "user@example.com",
  "password": "mypassword",
  "security_token": "mytoken",
  "client_id": "myclientid",
  "client_secret": "myclientsecret"
}
```

Response:
```json
{
  "objects": ["Account", "Contact", "Opportunity", ...]
}
```

#### Get Metadata for Objects

```
POST /api/metadata
```

Request body:
```json
{
  "username": "user@example.com",
  "password": "mypassword",
  "security_token": "mytoken",
  "client_id": "myclientid",
  "client_secret": "myclientsecret",
  "objects": ["Account", "Contact"]  // Optional
}
```

Response: Excel file with Salesforce metadata

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

# Get list of objects
curl -X POST \
  http://localhost:5000/api/objects \
  -H 'Content-Type: application/json' \
  -d '{
    "username": "user@example.com",
    "password": "mypassword",
    "security_token": "mytoken",
    "client_id": "myclientid",
    "client_secret": "myclientsecret"
  }'

# Get metadata for specific objects
curl -X POST \
  http://localhost:5000/api/metadata \
  -H 'Content-Type: application/json' \
  -d '{
    "username": "user@example.com",
    "password": "mypassword",
    "security_token": "mytoken",
    "client_id": "myclientid",
    "client_secret": "myclientsecret",
    "objects": ["Account", "Contact"]
  }' \
  -o metadata.xlsx
```

## Testing

A test script is provided to verify that the service is working correctly:

```bash
python tests/test_combined_service.py --host localhost --port 5000
```

This script tests all the endpoints of the combined service, including:
- Health check
- Generate query
- Batch generate
- Get objects (skipped by default to avoid credential requirements)
- Get metadata (skipped by default to avoid credential requirements)

## Deployment

For deploying the Salesforce Combined Service to AWS EC2, follow the same steps as described in the [Deployment Guide](DEPLOYMENT_GUIDE.md), but use `salesforce_combined_service.py` instead of the individual service files.

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
4. **Authentication Errors**: Verify your Salesforce credentials and ensure your Connected App is properly configured.

### Debugging

For more detailed logging, run the service in debug mode:

```bash
python src/services/salesforce_combined_service.py --debug
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.