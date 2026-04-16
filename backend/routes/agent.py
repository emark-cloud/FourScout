"""ERC-8004 Agent Identity endpoints."""

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel

router = APIRouter(tags=["agent"])


class RegisterRequest(BaseModel):
    name: str
    image_url: str | None = None
    description: str | None = None


@router.get("/agent/status")
async def agent_status():
    """Get current agent registration status and wallet info."""
    from services.agent_identity import get_agent_status
    return await get_agent_status()


@router.post("/agent/register")
async def register_agent(req: RegisterRequest):
    """Register wallet as ERC-8004 agent on-chain."""
    from services.agent_identity import register_agent
    result = await register_agent(req.name, req.image_url, req.description)
    if not result["success"]:
        return JSONResponse(content=result, status_code=400)
    return result
