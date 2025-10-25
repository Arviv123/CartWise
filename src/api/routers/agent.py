"""
Agent API Router
================

API endpoints for communication with local Raspberry Pi agents.

Author: CartWise Team
Version: 1.0.0
"""

from fastapi import APIRouter, HTTPException, Header
from typing import Optional, List, Dict
from pydantic import BaseModel
from datetime import datetime
from core import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/api/agent", tags=["Agent"])


# In-memory storage for commands and agent status
# In production, use Redis or database
_agent_commands: Dict[str, List[dict]] = {}  # branch_id -> [commands]
_agent_status: Dict[str, dict] = {}  # branch_id -> status
_command_results: Dict[str, dict] = {}  # command_id -> result
_api_keys: Dict[str, str] = {}  # branch_id -> api_key


# Models
class AgentRegisterRequest(BaseModel):
    branch_id: str
    agent_type: str
    version: str
    capabilities: List[str]


class AgentHeartbeatRequest(BaseModel):
    status: str
    timestamp: str


class CommandRequest(BaseModel):
    branch_id: str
    command_type: str
    params: dict


class CommandResultRequest(BaseModel):
    command_id: str
    branch_id: str
    success: bool
    result: dict
    timestamp: str


def verify_api_key(branch_id: str, authorization: str) -> bool:
    """Verify API key for branch."""
    if not authorization or not authorization.startswith('Bearer '):
        return False

    api_key = authorization[7:]  # Remove 'Bearer '

    # Check if branch has registered API key
    if branch_id not in _api_keys:
        # For demo, accept any key for now
        # In production, check against database
        _api_keys[branch_id] = api_key
        return True

    return _api_keys[branch_id] == api_key


@router.post("/register")
async def register_agent(
    request: AgentRegisterRequest,
    authorization: Optional[str] = Header(None)
):
    """
    Register a new agent (Raspberry Pi).

    This endpoint is called when the agent starts up.
    """
    branch_id = request.branch_id

    # Verify API key
    if not verify_api_key(branch_id, authorization):
        raise HTTPException(status_code=401, detail="Invalid API key")

    # Store agent info
    _agent_status[branch_id] = {
        'agent_type': request.agent_type,
        'version': request.version,
        'capabilities': request.capabilities,
        'status': 'online',
        'last_seen': datetime.now().isoformat(),
        'registered_at': datetime.now().isoformat()
    }

    # Initialize command queue
    if branch_id not in _agent_commands:
        _agent_commands[branch_id] = []

    logger.info(f"Agent registered: {branch_id} ({request.agent_type} v{request.version})")

    return {
        'success': True,
        'message': f'Agent {branch_id} registered successfully',
        'agent_id': branch_id
    }


@router.post("/heartbeat/{branch_id}")
async def agent_heartbeat(
    branch_id: str,
    request: AgentHeartbeatRequest,
    authorization: Optional[str] = Header(None)
):
    """
    Receive heartbeat from agent.

    Agents should send heartbeat every 30 seconds.
    """
    # Verify API key
    if not verify_api_key(branch_id, authorization):
        raise HTTPException(status_code=401, detail="Invalid API key")

    # Update agent status
    if branch_id in _agent_status:
        _agent_status[branch_id]['status'] = request.status
        _agent_status[branch_id]['last_seen'] = request.timestamp
    else:
        _agent_status[branch_id] = {
            'status': request.status,
            'last_seen': request.timestamp
        }

    logger.debug(f"Heartbeat from {branch_id}: {request.status}")

    return {'success': True}


@router.get("/commands/{branch_id}")
async def get_commands(
    branch_id: str,
    authorization: Optional[str] = Header(None)
):
    """
    Get pending commands for an agent.

    Agent polls this endpoint every second.
    """
    # Verify API key
    if not verify_api_key(branch_id, authorization):
        raise HTTPException(status_code=401, detail="Invalid API key")

    # Get commands for this branch
    commands = _agent_commands.get(branch_id, [])

    if commands:
        logger.debug(f"Returning {len(commands)} commands to {branch_id}")
        # Clear commands after sending
        _agent_commands[branch_id] = []
        return {'commands': commands}
    else:
        # No commands - return 204 No Content
        return {'commands': []}


@router.post("/command-result")
async def receive_command_result(
    request: CommandResultRequest,
    authorization: Optional[str] = Header(None)
):
    """
    Receive command execution result from agent.
    """
    # Verify API key
    if not verify_api_key(request.branch_id, authorization):
        raise HTTPException(status_code=401, detail="Invalid API key")

    # Store result
    _command_results[request.command_id] = {
        'branch_id': request.branch_id,
        'success': request.success,
        'result': request.result,
        'timestamp': request.timestamp
    }

    logger.info(f"Command result received: {request.command_id} - {'SUCCESS' if request.success else 'FAILED'}")

    return {'success': True}


@router.post("/disconnect/{branch_id}")
async def disconnect_agent(
    branch_id: str,
    authorization: Optional[str] = Header(None)
):
    """
    Agent disconnecting (shutdown).
    """
    # Verify API key
    if not verify_api_key(branch_id, authorization):
        raise HTTPException(status_code=401, detail="Invalid API key")

    # Update status
    if branch_id in _agent_status:
        _agent_status[branch_id]['status'] = 'offline'
        _agent_status[branch_id]['last_seen'] = datetime.now().isoformat()

    logger.info(f"Agent disconnected: {branch_id}")

    return {'success': True}


# ============================================================================
# Internal API for CartWise API to send commands to agents
# ============================================================================

def send_command_to_agent(branch_id: str, command_type: str, params: dict) -> str:
    """
    Send a command to an agent.

    This is called internally by CartWise API when it needs to unlock a cart.

    Args:
        branch_id: Branch ID
        command_type: Command type (unlock, lock, get_status, check_return)
        params: Command parameters

    Returns:
        command_id: Unique command ID
    """
    import uuid

    # Check if agent is online
    if branch_id not in _agent_status or _agent_status[branch_id]['status'] != 'online':
        logger.error(f"Agent {branch_id} is not online")
        raise Exception(f"Agent {branch_id} is offline")

    # Create command
    command_id = str(uuid.uuid4())
    command = {
        'id': command_id,
        'type': command_type,
        'params': params,
        'created_at': datetime.now().isoformat()
    }

    # Add to command queue
    if branch_id not in _agent_commands:
        _agent_commands[branch_id] = []

    _agent_commands[branch_id].append(command)

    logger.info(f"Command queued for {branch_id}: {command_type} (ID: {command_id})")

    return command_id


def wait_for_command_result(command_id: str, timeout: float = 10.0) -> Optional[dict]:
    """
    Wait for command result from agent.

    Args:
        command_id: Command ID
        timeout: Timeout in seconds

    Returns:
        Command result or None if timeout
    """
    import time

    start_time = time.time()

    while time.time() - start_time < timeout:
        if command_id in _command_results:
            result = _command_results[command_id]
            # Remove from results
            del _command_results[command_id]
            return result

        time.sleep(0.1)  # Check every 100ms

    logger.warning(f"Timeout waiting for command result: {command_id}")
    return None


def get_agent_status(branch_id: str) -> Optional[dict]:
    """
    Get agent status.

    Args:
        branch_id: Branch ID

    Returns:
        Agent status or None
    """
    return _agent_status.get(branch_id)


def list_agents() -> List[dict]:
    """
    List all registered agents.

    Returns:
        List of agent info
    """
    return [
        {'branch_id': branch_id, **status}
        for branch_id, status in _agent_status.items()
    ]
