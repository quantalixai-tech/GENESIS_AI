import docker
import socket
from typing import Any

from core.logging import get_logger

logger = get_logger(__name__)

class SandboxError(Exception):
    pass

def get_free_port() -> int:
    """Find a free port on localhost."""
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('', 0))
    port = s.getsockname()[1]
    s.close()
    return port

def start_sandbox(project_id: str, repository_path: str) -> dict[str, Any]:
    """
    Start a Docker sandbox for the given project.
    Uses a python slim image to serve static files on a dynamically assigned port.
    Returns details of the running sandbox.
    """
    client = docker.from_env()
    container_name = f"genesis-sandbox-{project_id}"
    
    # Check if a sandbox is already running
    try:
        container = client.containers.get(container_name)
        if container.status != "running":
            container.start()
        
        # Get the assigned port from the existing container
        ports = container.attrs['NetworkSettings']['Ports']
        host_port = None
        if '8000/tcp' in ports and ports['8000/tcp']:
            host_port = int(ports['8000/tcp'][0]['HostPort'])
            
        return {
            "status": "running",
            "container_id": container.id,
            "port": host_port
        }
    except docker.errors.NotFound:
        pass
        
    port = get_free_port()
    
    logger.info(f"Starting sandbox for {project_id} on port {port}")
    
    try:
        container = client.containers.run(
            image="python:3.11-slim",
            name=container_name,
            command="python -m http.server 8000",
            volumes={repository_path: {'bind': '/app', 'mode': 'ro'}},
            working_dir="/app",
            ports={'8000/tcp': port},
            detach=True,
            remove=True, # Auto-remove when stopped
        )
        
        return {
            "status": "running",
            "container_id": container.id,
            "port": port
        }
    except Exception as e:
        logger.error(f"Failed to start sandbox: {e}")
        raise SandboxError(f"Failed to start sandbox: {str(e)}")

def stop_sandbox(project_id: str) -> bool:
    """Stop the sandbox container if it exists."""
    client = docker.from_env()
    container_name = f"genesis-sandbox-{project_id}"
    
    try:
        container = client.containers.get(container_name)
        container.stop()
        return True
    except docker.errors.NotFound:
        return True
    except Exception as e:
        logger.error(f"Failed to stop sandbox: {e}")
        raise SandboxError(f"Failed to stop sandbox: {str(e)}")

def get_sandbox_status(project_id: str) -> dict[str, Any]:
    """Get the current status of the sandbox container."""
    client = docker.from_env()
    container_name = f"genesis-sandbox-{project_id}"
    
    try:
        container = client.containers.get(container_name)
        
        ports = container.attrs['NetworkSettings']['Ports']
        host_port = None
        if '8000/tcp' in ports and ports['8000/tcp']:
            host_port = int(ports['8000/tcp'][0]['HostPort'])
            
        return {
            "status": container.status,
            "container_id": container.id,
            "port": host_port
        }
    except docker.errors.NotFound:
        return {
            "status": "stopped",
            "container_id": None,
            "port": None
        }
    except Exception as e:
        logger.error(f"Failed to get sandbox status: {e}")
        raise SandboxError(f"Failed to get sandbox status: {str(e)}")
