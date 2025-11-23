# Email Agent - Omni-Input

An intelligent email triage and response agent built with LangGraph, FastAPI, and OpenAI. This agent automatically classifies incoming emails, checks calendar availability, schedules meetings, and drafts professional responses.

## Architecture

The project is split into two main components:

- **Server** (`server/`): FastAPI server that hosts the LangGraph email agent
- **Client** (`client/`): CLI client for interacting with the server
    - Additional clients can be added to illustrate multi client usage


## Installation

### Prerequisites

- Python 3.13+
- Virtual environment (recommended)

### Setup

1. **Clone the repository** (if applicable)

2. **Create and activate a virtual environment**:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**:
   
   Create a `.env` file in the project root (see `.env.example` for reference):
   ```bash
   OPENAI_API_KEY=your_openai_api_key_here
   # Add other required environment variables
   ```


## Usage

### Starting the Server

Start the FastAPI server:

```bash
source .venv/bin/activate
uvicorn server.server:app --host 0.0.0.0 --port 8000 --reload
```

The server will be available at `http://localhost:8000`

### Using the CLI Client

The CLI client allows you to send emails to the agent for processing.

#### Basic Usage

```bash
python -m client.cli \
  --from "alice@example.com" \
  --to "bob@example.com" \
  --subject "Meeting Request" \
  "Can we schedule a meeting tomorrow?"
```

#### Continue Existing Thread

```bash
python -m client.cli \
  --from "alice@example.com" \
  --to "bob@example.com" \
  --subject "Re: Meeting Request" \
  --thread-id "thread-123" \
  "Thanks for the help!"
```

#### CLI Options

- `--from` (required): Sender email address
- `--to` (required): Recipient email address  
- `--subject` (required): Email subject line
- `--thread-id` (optional): Thread ID to continue conversation (default: creates new thread)
- `--server-url` (optional): Server URL (default: `http://localhost:8000`)
- `--json` (optional): Output raw JSON response

### API Endpoints

#### POST `/invoke`

Invoke the email agent with an email input.

**Request Body**:
```json
{
  "email_input": {
    "author": "sender@example.com",
    "to": "recipient@example.com",
    "subject": "Email Subject",
    "email_thread": "Email content here"
  },
  "thread_id": "optional-thread-id",
  "source": "CLI"
}
```

**Response**:
```json
{
  "result": {
    "classification_decision": "respond",
    "messages": [...]
  }
}
```
