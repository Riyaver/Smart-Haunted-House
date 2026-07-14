import tkinter as tk
import threading
import paho.mqtt.client as mqtt
from paho.mqtt.enums import CallbackAPIVersion

root = tk.Tk()
root.title("SHH Admin Bindow")
root.geometry("600x600")
root.configure(bg="#121212") 

p1_heart = tk.StringVar(value="80 BPM")
p2_heart = tk.StringVar(value="80 BPM")
p3_heart = tk.StringVar(value="80 BPM")
p1_notif = tk.StringVar(value="Clear")
p2_notif = tk.StringVar(value="Clear")
p3_notif = tk.StringVar(value="Clear")
system_status = tk.StringVar(value="Yuh")

def create_card(parent, title, text_var, bg_color):
    frame = tk.Frame(parent, bg=bg_color, bd=2, relief="groove", padx=15, pady=15)
    tk.Label(frame, text=title, font=("Arial", 12, "bold"), fg="#888888", bg=bg_color).pack()
    tk.Label(frame, textvariable=text_var, font=("Arial", 16, "bold"), fg="white", bg=bg_color).pack(pady=5)
    return frame

tk.Label(root, text="SYSTEM STATUS MONITOR", font=("Arial", 20, "bold"), fg="red", bg="#121212").pack(pady=20)

grid_frame = tk.Frame(root, bg="#121212")
grid_frame.pack(fill="x", padx=30, pady=10)

p1_frame = create_card(grid_frame, "PLAYER 1", p1_heart, "#1e1e1e")
p1_frame.grid(row=0, column=0, padx=10, sticky="nsew")
tk.Label(p1_frame, textvariable=p1_notif, font=("Arial", 10, "italic"), fg="#ffaa00", bg="#1e1e1e").pack()

p2_frame = create_card(grid_frame, "PLAYER 2", p2_heart, "#1e1e1e")
p2_frame.grid(row=0, column=1, padx=10, sticky="nsew")
tk.Label(p2_frame, textvariable=p2_notif, font=("Arial", 10, "italic"), fg="#ffaa00", bg="#1e1e1e").pack()

p3_frame = create_card(grid_frame, "PLAYER 3", p3_heart, "#1e1e1e")
p3_frame.grid(row=0, column=2, padx=10, sticky="nsew")
tk.Label(p3_frame, textvariable=p3_notif, font=("Arial", 10, "italic"), fg="#ffaa00", bg="#1e1e1e").pack()

grid_frame.columnconfigure((0, 1, 2), weight=1)

log_frame = tk.Frame(root, bg="#1a1a1a", bd=1, relief="solid", padx=15, pady=15)
log_frame.pack(fill="both", expand=True, padx=30, pady=30)
tk.Label(log_frame, text="AI PLANNER DECISIONS / LOGS", font=("Arial", 10, "bold"), fg="red", bg="#1a1a1a").pack(anchor="w")
tk.Label(log_frame, textvariable=system_status, font=("Arial", 12), fg="#00FF00", bg="#1a1a1a", wraplength=500, justify="left").pack(anchor="w", pady=10)


def on_connect(client, userdata, flags, rc, properties=None):
    client.subscribe("room/#")

def on_message(client, userdata, msg):
    topic = msg.topic
    payload = msg.payload.decode()

    if "heartbeat" in topic:
        player = topic.split("/")[1]
        if player == "player1": p1_heart.set(f"{payload} BPM")
        elif player == "player2": p2_heart.set(f"{payload} BPM")
        elif player == "player3": p3_heart.set(f"{payload} BPM")

    elif "notifications" in topic:
        player = topic.split("/")[1]
        display_text = payload if payload != "" else "Clear"
        
        if player == "player1": p1_notif.set(display_text)
        elif player == "player2": p2_notif.set(display_text)
        elif player == "player3": p3_notif.set(display_text)
        
        if "BOO" in payload:
            system_status.set(f"AI Planner idk not yet added: Creepy msg to {player.upper()}!")

def start_mqtt():
    client = mqtt.Client(callback_api_version=CallbackAPIVersion.VERSION2)
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect("localhost", 1883, 60)
    client.loop_forever()

mqtt_thread = threading.Thread(target=start_mqtt, daemon=True)
mqtt_thread.start()

root.mainloop()