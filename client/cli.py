#!/usr/bin/env python3
"""
CLI client for the email agent server.

Usage:
    python -m client.cli --from "sender@example.com" --to "recipient@example.com" --subject "Subject" "email body"
    python -m client.cli --from "sender@example.com" --to "recipient@example.com" --subject "Subject" --thread-id "thread-123" "continue conversation"
"""

import argparse
import json
import sys
from typing import Optional
import requests


DEFAULT_SERVER_URL = "http://localhost:8000"


def create_email_input(
    content: str,
    from_email: str,
    to_email: str,
    subject: str,
) -> dict:
    """Create email_input dict from CLI arguments."""
    return {
        "author": from_email,
        "to": to_email,
        "subject": subject,
        "email_thread": content,
    }


def invoke_agent(
    email_input: dict,
    server_url: str = DEFAULT_SERVER_URL,
    thread_id: Optional[str] = None,
    source: str = "CLI",
) -> dict:
    """Send request to the email agent server."""
    url = f"{server_url}/invoke"
    
    payload = {
        "email_input": email_input,
        "source": source,
    }
    
    # Only include thread_id if explicitly provided (default is new thread)
    if thread_id:
        payload["thread_id"] = thread_id
    
    try:
        response = requests.post(url, json=payload, timeout=300)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.ConnectionError:
        print(f"Error: Could not connect to server at {server_url}", file=sys.stderr)
        print("Make sure the server is running with: uvicorn server.server:app", file=sys.stderr)
        sys.exit(1)
    except requests.exceptions.HTTPError as e:
        print(f"Error: Server returned {e.response.status_code}", file=sys.stderr)
        try:
            error_detail = e.response.json()
            print(f"Details: {error_detail}", file=sys.stderr)
        except:
            print(f"Details: {e.response.text}", file=sys.stderr)
        sys.exit(1)
    except requests.exceptions.Timeout:
        print("Error: Request timed out after 5 minutes", file=sys.stderr)
        sys.exit(1)


def format_response(result: dict) -> str:
    """Format the agent response for display."""
    # Extract relevant information from the result
    output_parts = []
    
    # Show classification if available
    if "classification_decision" in result:
        classification = result["classification_decision"]
        output_parts.append(f"Classification: {classification}")
        output_parts.append("")
    
    # Show messages if available
    if "messages" in result:
        messages = result["messages"]
        if messages:
            output_parts.append("Agent Response:")
            output_parts.append("=" * 50)
            for msg in messages:
                if hasattr(msg, "content"):
                    content = msg.content
                elif isinstance(msg, dict):
                    content = msg.get("content", str(msg))
                else:
                    content = str(msg)
                output_parts.append(content)
                output_parts.append("")
    
    # If no structured output, show the full result
    if not output_parts:
        output_parts.append("Agent Result:")
        output_parts.append("=" * 50)
        output_parts.append(json.dumps(result, indent=2))
    
    return "\n".join(output_parts)


def main():
    parser = argparse.ArgumentParser(
        description="CLI client for the email agent server",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Create new thread (all fields required)
  python -m client.cli --from "alice@example.com" --to "bob@example.com" \\
                       --subject "Meeting Request" "Can we meet tomorrow?"

  # Continue existing thread
  python -m client.cli --from "alice@example.com" --to "bob@example.com" \\
                       --subject "Re: Meeting Request" --thread-id "thread-123" \\
                       "Thanks for the help!"
        """
    )
    
    parser.add_argument(
        "content",
        help="Email content/body"
    )
    
    parser.add_argument(
        "--from",
        dest="from_email",
        required=True,
        help="Sender email address (required)"
    )
    
    parser.add_argument(
        "--to",
        dest="to_email",
        required=True,
        help="Recipient email address (required)"
    )
    
    parser.add_argument(
        "--subject",
        required=True,
        help="Email subject line (required)"
    )
    
    parser.add_argument(
        "--thread-id",
        help="Thread ID to continue conversation (default: creates new thread)"
    )
    
    parser.add_argument(
        "--server-url",
        default=DEFAULT_SERVER_URL,
        help=f"Server URL (default: {DEFAULT_SERVER_URL})"
    )
    
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output raw JSON response"
    )
    
    args = parser.parse_args()
    
    # Create email input
    email_input = create_email_input(
        content=args.content,
        from_email=args.from_email,
        to_email=args.to_email,
        subject=args.subject,
    )
    
    # Invoke agent
    result = invoke_agent(
        email_input=email_input,
        server_url=args.server_url,
        thread_id=args.thread_id,
        source="CLI",
    )
    
    # Output result
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(format_response(result["result"]))


if __name__ == "__main__":
    main()

