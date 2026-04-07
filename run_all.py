import subprocess
import time
import sys
import os

def run_all():
    print("=== DEEPFAKE DETECTION SYSTEM: MASTER LAUNCHER ===")
    
    # 1. Seeding Data
    print("\n[Step 1] Seeding Demo Data...")
    subprocess.run([sys.executable, "scripts/seed_demo_data.py"])
    
    processes = []
    
    try:
        # 2. Start Dummy Social Platform (Port 5001)
        print("\n[Step 2] Starting Dummy Social Platform on Port 5001...")
        p_social = subprocess.Popen([sys.executable, "-m", "dummy_social_platform.app"], 
                                    env={**os.environ, "PYTHONPATH": "."})
        processes.append(p_social)
        
        time.sleep(2) # Give it a moment to bind to port
        
        # 3. Start Dashboard (Port 5000)
        print("\n[Step 3] Starting Dashboard Oversight on Port 5000...")
        # Since app.py is inside the package, we might need a wrapper or run as module
        p_dash = subprocess.Popen([sys.executable, "-m", "member5_dashboard_oversight.app"], 
                                   env={**os.environ, "PYTHONPATH": "."})
        processes.append(p_dash)
        
        time.sleep(2)
        
        # 4. Start Public Reporting System (Port 5002)
        print("\n[Step 4] Starting Public Identity Protection Shield on Port 5002...")
        p_public = subprocess.Popen([sys.executable, "-m", "public_reporting_system.app"], 
                                    env={**os.environ, "PYTHONPATH": "."})
        processes.append(p_public)
        
        time.sleep(2)
        
        # 5. Start Orchestrator
        print("\n[Step 5] Starting Orchestrator Pipeline...")
        p_orch = subprocess.Popen([sys.executable, "scripts/orchestrator.py"], 
                                   env={**os.environ, "PYTHONPATH": "."})
        processes.append(p_orch)
        
        print("\n" + "="*50)
        print("SYSTEM LIVE!")
        print("Social Platform:  http://localhost:5001")
        print("Dashboard:        http://localhost:5000")
        print("Public Shield:    http://localhost:5002")
        print("Orchestrator:     Running in background...")
        print("="*50)
        print("\nPress Ctrl+C to stop everything.")
        
        # Wait for processes
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\nShutting down all components...")
        for p in processes:
            p.terminate()
        print("All processes terminated.")

if __name__ == "__main__":
    run_all()
