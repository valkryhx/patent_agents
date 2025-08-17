#!/usr/bin/env python3
"""
Startup script for FastAPI-based Patent Agent System
Launches coordinator and agent services
"""

import subprocess
import time
import sys
import os
from typing import List, Dict

def start_service(service_name: str, port: int, script_path: str):
    """Start a service in a subprocess"""
    print(f"🚀 Starting {service_name} service on port {port}...")
    
    try:
        # Start the service
        process = subprocess.Popen([
            sys.executable, script_path
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Wait a moment for startup
        time.sleep(2)
        
        # Check if process is still running
        if process.poll() is None:
            print(f"✅ {service_name} service started successfully (PID: {process.pid})")
            return process
        else:
            stdout, stderr = process.communicate()
            print(f"❌ {service_name} service failed to start")
            print(f"   stdout: {stdout.decode()}")
            print(f"   stderr: {stderr.decode()}")
            return None
            
    except Exception as e:
        print(f"❌ Error starting {service_name} service: {str(e)}")
        return None

def main():
    """Main startup function"""
    print("🚀 Starting FastAPI-based Patent Agent System")
    print("=" * 50)
    
    # Service configurations
    services = [
        {
            "name": "Coordinator",
            "port": 8000,
            "script": "main.py"
        },
        {
            "name": "Planner Agent",
            "port": 8001,
            "script": "agent_planner.py"
        },
        {
            "name": "Searcher Agent", 
            "port": 8002,
            "script": "agent_searcher.py"
        }
    ]
    
    # Start all services
    processes = []
    
    for service in services:
        process = start_service(service["name"], service["port"], service["script"])
        if process:
            processes.append(process)
        else:
            print(f"❌ Failed to start {service['name']}, stopping all services...")
            # Stop all started processes
            for p in processes:
                p.terminate()
            sys.exit(1)
    
    print("\n🎉 All services started successfully!")
    print("📡 Service URLs:")
    print("   - Coordinator: http://localhost:8000")
    print("   - Planner Agent: http://localhost:8001")
    print("   - Searcher Agent: http://localhost:8002")
    print("\n📚 API Documentation:")
    print("   - Coordinator: http://localhost:8000/docs")
    print("   - Planner Agent: http://localhost:8001/docs")
    print("   - Searcher Agent: http://localhost:8002/docs")
    
    print("\n⏹️  Press Ctrl+C to stop all services...")
    
    try:
        # Keep the script running
        while True:
            time.sleep(1)
            
            # Check if any process has died
            for i, process in enumerate(processes):
                if process.poll() is not None:
                    print(f"❌ {services[i]['name']} service has stopped unexpectedly")
                    # Stop all other processes
                    for p in processes:
                        p.terminate()
                    sys.exit(1)
                    
    except KeyboardInterrupt:
        print("\n🛑 Stopping all services...")
        
        # Terminate all processes
        for process in processes:
            process.terminate()
        
        # Wait for processes to terminate
        for process in processes:
            process.wait()
        
        print("✅ All services stopped")

if __name__ == "__main__":
    main()