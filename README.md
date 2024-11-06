# Angle American Gen AI POC - Data Science Module

This project is a Gen AI Flask service that provides a chat interface using Azure AI Search and Azure OpenAI.

## 1. Setting up the environment and dependencies

To set up the environment and install the necessary dependencies, follow these steps:

1. Ensure you have Python 3.7+ installed on your system.
2. Clone this repository:
   ```
   git clone https://<username>@dev.azure.com/AngloDevOps/APC%20GenAI%20PoC/_git/APC-GenAI-Appt
   cd apc
   ```
3. Create a virtual environment:
   ```
   cd datascience
   python -m venv venv
   ```
4. Activate the virtual environment:
   - On Windows:
     ```
     venv\Scripts\activate
     ```
   - On macOS and Linux:
     ```
     source venv/bin/activate
     ```
5. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

## 2. Configuring environment variables

Before running the service, you need to configure the following environment variables:

1. Create a `.env` file in the root directory of the project.
2. Add the following variables to the `.env` file:

   ```
   AZURE_SEARCH_ENDPOINT=your_azure_search_endpoint
   AZURE_SEARCH_KEY=your_azure_search_key
   AZURE_OPENAI_ENDPOINT=your_azure_openai_endpoint
   AZURE_OPENAI_KEY=your_azure_openai_key
   AZURE_OPENAI_DEPLOYMENT=your_azure_openai_deployment
   ```

   Replace the placeholder values with your actual Azure AI Search and Azure OpenAI credentials.

## 3. Running the Flask Service

### Development Environment
There are two ways to run the Flask service locally for development:

1. Using Flask's built-in server:
```bash
# Set the Flask application
export FLASK_APP=app.py  # On Unix/macOS
set FLASK_APP=app.py     # On Windows

# Optional: Enable debug mode
export FLASK_DEBUG=1     # On Unix/macOS
set FLASK_DEBUG=1        # On Windows

# Run the application
flask run
```

2. Using Python directly:
```bash
python app.py
```

Both methods will start the service on `http://localhost:5000`

### Production Deployment
For production deployment, it's recommended to use a production-grade WSGI server like Gunicorn:

1. Install Gunicorn (if not already installed):
```bash
pip install gunicorn
```

2. Run the service with Gunicorn:
```bash
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

For Windows environments, you can use waitress as an alternative:

1. Install waitress:
```bash
pip install waitress
```

2. Create a `wsgi.py` file:
```python
from app import app
from waitress import serve

if __name__ == '__main__':
    serve(app, host='0.0.0.0', port=5000)
```

3. Run with waitress:
```bash
python wsgi.py
```

## 4. API Documentation

### Chat Endpoint

**URL:** `/chat`  
**Method:** POST  
**Description:** Send questions and receive AI-powered responses based on the document context.

#### Request Parameters
```json
{
    "question": "string (required)",
    "user_id": "string (optional)",
    "session_id": "string (optional)",
    "controller_id": "string (optional)"
}
```

#### Response Format
```json
{
    "answer": "string",
    "user_id": "string",
    "session_id": "string",
    "controller_id": "string"
}
```

#### Available Controllers
The API supports the following controllers:
- **apc-j140-bin-005c**: APC-J140 BIN 005C (Bin Controller)
- **apc-j141-lic-002-004c**: APC-J141 LIC 002/004C (Level Controller)
- **apc-j141-lic-005c**: APC-J141 LIC 005C (Level Controller)
- **pwo-sep-t-crushing-pwo**: PWO Separator Tertiary Crushing (Tertiary Crushing PWO)

#### Example Usage

Using curl:
```bash
curl -X POST http://localhost:5000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What are the main components?",
    "user_id": "user123",
    "session_id": "session456",
    "controller_id": "apc-j140-bin-005c"
  }'
```

Using JavaScript fetch:
```javascript
fetch('/chat', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json'
    },
    body: JSON.stringify({
        question: "What are the main components?",
        user_id: "user123",
        session_id: "session456",
        controller_id: "apc-j140-bin-005c"
    })
})
.then(response => response.json())
.then(data => console.log(data));
```

Using Python requests:
```python
import requests
import json

response = requests.post(
    'http://localhost:5000/chat',
    headers={'Content-Type': 'application/json'},
    json={
        'question': 'What are the main components?',
        'user_id': 'user123',
        'session_id': 'session456',
        'controller_id': 'apc-j140-bin-005c'
    }
)
print(response.json())
```

## Requirements

The project dependencies are listed in the `requirements.txt` file. The main libraries used are:

- flask
- flask-cors
- openai
- python-dotenv
- azure-search-documents
- gunicorn (for production deployment)
- waitress (alternative for Windows deployment)

Make sure to install these dependencies using the instructions in the "Setting up the environment and dependencies" section.
