import json
import time
import hmac
import hashlib
import paho.mqtt.client as mqtt

# --- CẤU HÌNH BẢO MẬT ---
BROKER = "test.mosquitto.org"
PORT = 1883
TOPIC = "iot/door/control"
SECRET_KEY = b"SecretKey123"  # Khóa Kdev chia sẻ giữa ESP32 và Gateway
DELTA_T = 5                   # Cửa sổ thời gian hợp lệ (5 giây)

# --- BỘ NHỚ TRẠNG THÁI CỦA GATEWAY ---
last_seq = 0                  # Lưu Sequence Number lớn nhất đã nhận
replay_cache = set()          # Lưu các Nonce đã sử dụng

def verify_message(data):
    global last_seq, replay_cache
    current_time = time.time()

    try:
        device_id = data["device_id"]
        cmd = data["command"]
        ts = float(data["timestamp"])
        seq = int(data["sequence"])
        nonce = str(data["nonce"])
        received_mac = str(data["hmac"])
    except KeyError:
        return False, "REJECT: Thiếu trường dữ liệu trong gói tin JSON"

    # 1. LỚP PHÒNG THỦ 1: Kiểm tra Cửa sổ thời gian (Chống Replay trễ - KB02)
    if abs(current_time - ts) > DELTA_T:
        return False, f"REJECT: Giá trị Timestamp quá hạn (Khoảng cách > {DELTA_T}s)"

    # 2. LỚP PHÒNG THỦ 2: Kiểm tra tính tuần tự và duy nhất (Chống Replay tức thì - KB03)
    if seq <= last_seq:
         return False, "REJECT: Sequence không hợp lệ hoặc bị lặp (Replay Attack)"
    
    if nonce in replay_cache:
         return False, "REJECT: Nonce đã được sử dụng (Replay Attack)"

    # 3. LỚP PHÒNG THỦ 3: Kiểm tra tính toàn vẹn (Chống Tampering - KB04)
    # Tái tạo chuỗi dữ liệu gốc để băm đối chiếu
    payload_to_sign = {
        "device_id": device_id,
        "command": cmd,
        "timestamp": ts,
        "sequence": seq,
        "nonce": nonce
    }
    
    msg_string = json.dumps(payload_to_sign, separators=(',', ':'))
    print(f"[DEBUG] Chuỗi Gateway đang băm là: {msg_string}")
    
    calculated_mac = hmac.new(SECRET_KEY, msg_string.encode('utf-8'), hashlib.sha256).hexdigest()
    
    print(f"[DEBUG] HMAC của ESP32   : {received_mac}")
    print(f"[DEBUG] HMAC của Gateway : {calculated_mac}")

    if not hmac.compare_digest(received_mac, calculated_mac):
        return False, "REJECT: Chữ ký HMAC không khớp (Sai khóa hoặc bị sửa đổi dữ liệu)"

    # 4. GHI NHẬN TRẠNG THÁI: Cập nhật nếu gói tin hợp pháp
    last_seq = seq
    replay_cache.add(nonce)

    return True, f"ACCEPT: Gói tin hợp lệ, thực thi lệnh {cmd}!"

def on_connect(client, userdata, flags, rc):
    print("[*] Gateway đã kích hoạt lớp phòng thủ toàn diện!")
    print(f"[*] Đang lắng nghe trên topic: {TOPIC}...")
    client.subscribe(TOPIC)

def on_message(client, userdata, msg):
    print("\n======================================================================")
    print(f"[+] Nhận gói tin từ topic {msg.topic}:")
    payload_str = msg.payload.decode('utf-8')
    print(payload_str)
    
    try:
        data = json.loads(payload_str)
        is_valid, result_msg = verify_message(data)
        
        if is_valid:
            print(f"[V] THÀNH CÔNG: {result_msg}")
        else:
            print(f"[!!!] BÁO ĐỘNG PHÒNG THỦ: {result_msg}")
    except json.JSONDecodeError:
        print("[!!!] LỖI: Payload không phải định dạng JSON hợp lệ")
    print("======================================================================")

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

try:
    client.connect(BROKER, PORT, 60)
    client.loop_forever()
except KeyboardInterrupt:
    print("\n[*] Đóng Gateway.")
