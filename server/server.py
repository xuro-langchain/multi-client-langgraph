from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any
from contextlib import asynccontextmanager
from pathlib import Path
from dotenv import load_dotenv

# Load .env from project root
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)

from server.email_agent import studio_email_assistant, StateInput, ContextSchema


# Request/Response models
class InvokeRequest(BaseModel):
    email_input: Dict[str, Any]
    thread_id: Optional[str] = None
    source: Optional[str] = None


class InvokeResponse(BaseModel):
    result: Dict[str, Any]


# Global agent instance
email_assistant = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage agent lifecycle"""
    global email_assistant
    async with studio_email_assistant() as agent:
        email_assistant = agent
        yield
    email_assistant = None


# Create FastAPI app with lifespan
app = FastAPI(lifespan=lifespan)


@app.post("/invoke", response_model=InvokeResponse)
async def invoke_agent(request: InvokeRequest):
    """
    Invoke the email agent with email input and optional config.
    """
    if email_assistant is None:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    
    try:
        # Prepare input
        input_data: StateInput = {
            "email_input": request.email_input
        }
        
        # Construct context for source (runtime configuration)
        context = ContextSchema(source=request.source) if request.source else None
        
        # Construct config for thread_id (checkpointing/thread management)
        config = {}
        if request.thread_id:
            config["configurable"] = {"thread_id": request.thread_id}
        
        # Invoke agent with context and/or config
        invoke_kwargs = {}
        if context:
            invoke_kwargs["context"] = context
        if config:
            invoke_kwargs["config"] = config
        
        result = await email_assistant.ainvoke(input_data, **invoke_kwargs)
        
        return InvokeResponse(result=result)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error invoking agent: {str(e)}")


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy", "agent_initialized": email_assistant is not None}

