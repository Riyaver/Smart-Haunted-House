import subprocess
import sys
import time

print("SHH")

try:
    planner_process = subprocess.Popen([sys.executable, "mqtt_calling_sensor.py"])
    
    time.sleep(1.5)

    notif_process = subprocess.Popen([sys.executable, "testing_notif_python_code.py"])


    while True:
        if planner_process.poll() is not None:
            if planner_process.returncode == 0:
                print("\nPLan completed")
            else:
                print(f"\n{planner_process.returncode}")
            break
        time.sleep(1)

    notif_process.terminate()
    notif_process.wait()
    sys.exit(0)

except KeyboardInterrupt:
    planner_process.terminate()
    notif_process.terminate()
    planner_process.wait()
    notif_process.wait()
