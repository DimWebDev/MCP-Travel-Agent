#!/usr/bin/env python3
"""
**Dev Note:** During local development, agent orchestration and integration can be tested by running all MCP servers in parallel with `run_all_servers.py`. 
This script is for rapid iteration and should be replaced by Docker Compose for full-stack and production testing.
Run all MCP servers in parallel for integration testing.

This script starts all four MCP servers (geocoding, poi_discovery, wikipedia, trivia)
on different ports for testing the full travel agent system.

Usage:
    poetry run python run_all_servers.py

Server Ports:
    - Geocoding: 8001
    - POI Discovery: 8002  
    - Wikipedia: 8003
    - Trivia: 8004
"""

import subprocess
import signal
import sys
import time
from pathlib import Path

def run_server(server_path, port):
    """Run a single MCP server."""
    print(f"Starting {server_path} on port {port}...")
    return subprocess.Popen([
        "poetry", "run", "python", server_path
    ], cwd=Path(__file__).parent)

def main():
    """Run all MCP servers in parallel."""
    servers = [
        ("app/mcp_servers/geocoding/server.py", 8001),
        ("app/mcp_servers/poi_discovery/server.py", 8002),
        ("app/mcp_servers/wikipedia/server.py", 8003),
        ("app/mcp_servers/trivia/server.py", 8004),
    ]
    
    processes = []
    
    try:
        # Start all servers
        for server_path, port in servers:
            proc = run_server(server_path, port)
            processes.append((proc, server_path, port))
            time.sleep(2)  # Give each server time to start
        
        print("\n" + "="*60)
        print("All MCP servers are running!")
        print("="*60)
        for _, server_path, port in processes:
            server_name = Path(server_path).parent.name
            print(f"  {server_name.title()}: http://127.0.0.1:{port}/mcp/")
        print("="*60)
        print("Press Ctrl+C to stop all servers")
        print("="*60)
        
        # Wait for all processes
        for proc, _, _ in processes:
            proc.wait()
            
    except KeyboardInterrupt:
        print("\nShutting down all servers...")
        
        # Terminate all processes
        for proc, server_path, port in processes:
            if proc.poll() is None:  # Process is still running
                print(f"Stopping {Path(server_path).parent.name} server...")
                proc.terminate()
                try:
                    proc.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    print(f"Force killing {Path(server_path).parent.name} server...")
                    proc.kill()
        
        print("All servers stopped.")
        sys.exit(0)

if __name__ == "__main__":
    main()
