# Salesforce Metadata Service

This service allows you to retrieve Salesforce metadata and generate metadata files for use with the SOQL query generator.

## Overview

The Salesforce Metadata Service consists of two main components:

1. **Command-line tool** (`salesforce_metadata_service.py`) - Retrieves Salesforce metadata and exports it to an Excel file
2. **Web API** (`salesforce_metadata_api.py`) - Exposes an API for retrieving Salesforce metadata

Both components connect to Salesforce using the simple-salesforce library, retrieve metadata for specified objects (or all objects), and export it to an Excel file that can be used with the `generate_metadata.py` script to generate metadata files.

## Prerequisites

- Python 3.6 or higher
- Salesforce account with API access enabled
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

## Command-line Tool Usage

The command-line tool allows you to retrieve Salesforce metadata and export it to an Excel file.

```bash
python salesforce_metadata_service.py --username <username> --password <password> --security-token <token> --client-id <client_id> --client-secret <client_secret> --output-file <output_file>
```

### Arguments

- `--username`, `-u`: Salesforce username (required)
- `--password`, `-p`: Salesforce password (required)
- `--security-token`, `-t`: Salesforce security token (required)
- `--client-id`, `-i`: Salesforce connected app client ID (required)
- `--client-secret`, `-s`: Salesforce connected app client secret (required)
- `--output-file`, `-o`: Path to the output Excel file (default: "Salesforce_Complete_Metadata.xlsx")
- `--objects`: Specific Salesforce objects to retrieve (optional, if not provided all objects will be retrieved)

### Example

```bash
python salesforce_metadata_service.py \
  --username user@example.com \
  --password mypassword \
  --security-token mytoken \
  --client-id myclientid \
  --client-secret myclientsecret \
  --output-file metadata.xlsx \
  --objects Account Contact Opportunity
```

## Web API Usage

The web API allows you to retrieve Salesforce metadata through HTTP requests.

### Starting the API Server

```bash
python salesforce_metadata_api.py --host <host> --port <port>
```

### Arguments

- `--host`: Host to bind the service to (default: "0.0.0.0")
- `--port`: Port to bind the service to (default: 5000)
- `--debug`: Run in debug mode (optional)

### Example

```bash
python salesforce_metadata_api.py --host 0.0.0.0 --port 5000
```

### API Endpoints

#### Health Check

```
GET /health
```

Response:
```json
{
  "status": "healthy",
  "message": "Salesforce Metadata API is running"
}
```

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

### Example API Usage with curl

```bash
# Health check
curl http://localhost:5000/health

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

## Using the Generated Excel File

Once you have the Excel file with Salesforce metadata, you can use it with the `generate_metadata.py` script to generate metadata files:

```bash
python generate_metadata.py --excel-file metadata.xlsx --output-dir data/metadata
```

These metadata files will be used by the SOQL query generator to generate accurate queries based on your Salesforce schema.

## Deployment

For instructions on deploying the web API to AWS EC2, see the [Deployment Guide](DEPLOYMENT_GUIDE.md).

## Security Considerations

- Never hardcode credentials in your code
- Use HTTPS in production to encrypt data in transit
- Consider adding authentication to the API
- Restrict access to the API by IP address

## Troubleshooting

### Common Issues

1. **Authentication Failed**: Verify your Salesforce credentials and ensure your Connected App is properly configured.
2. **Object Not Found**: Ensure the object name is correct and that you have access to it in Salesforce.
3. **API Connection Issues**: Check your network connection and ensure the API server is running.

### Debugging

For more detailed logging, run the API server in debug mode:

```bash
python salesforce_metadata_api.py --debug
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.