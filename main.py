import subprocess
import sys
import time
import os

print("             Smart Haunted House                ")
print("    Dashboard -> http://localhost:3000   ")

base_dir = os.path.dirname(os.path.abspath(__file__))
dashboard_dir = os.path.join(base_dir, "dashboard")

try:
    print("Starting Dashboard")
    dashboard_process = subprocess.Popen(
        ["node", "server.js"], 
        cwd=dashboard_dir
    )
    time.sleep(1.0)

    print("Starting AI Planner")
    planner_process = subprocess.Popen(
        [sys.executable, "mqtt_calling_sensor.py"], 
        cwd=base_dir
    )
    time.sleep(1.5)

    print("Starting Heartbeat Monitor")
    notif_process = subprocess.Popen(
        [sys.executable, "testing_notif_python_code.py"], 
        cwd=base_dir
    )
    
    while True:
        if planner_process.poll() is not None:
            if planner_process.returncode == 0:
                print("\nPlan completed successfully.")
            else:
                print(f"\nPlanner exited with code: {planner_process.returncode}")
            break
        time.sleep(1)

    notif_process.terminate()
    notif_process.wait()
    
    dashboard_process.terminate()
    dashboard_process.wait()
    
    sys.exit(0)

except KeyboardInterrupt:
    planner_process.terminate()
    notif_process.terminate()
    dashboard_process.terminate()
    
    planner_process.wait()
    notif_process.wait()
    dashboard_process.wait()
    sys.exit(0)