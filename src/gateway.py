import json
import time
import hmac
import hashlib
import paho.mqtt.client as mqtt

# --- CẤU HÌNH BẢO MẬT ---
SECRET_KEY = b"SecretKey123"      # Khóa Kdev chia sẻ giữa ESP32 và Gateway
DELTA_T = 5                        # Cửa sổ thời gian hợp lệ (5 giây)

# --- BỘ NHỚ TRẠNG THÁI CỦA GATEWAY ---
last_seq = 0                       # Lưu Sequence Number lớn nhất đã nhận
replay_cache = set()               # Lưu các Nonce đã sử dụng trong cửa sổ Δt

def verify_message(data):
    global last_seq, replay_cache
    current_time = time.time()
    
    try:
        device_id = data["device_id"]
        cmd = data["cmd"]
        ts = float(data["ts"])
        seq = int(data["seq"])
        nonce = str(data["nonce"])
        received_mac = str(data["mac"])
    except KeyError:
        return False, "REJECT: Thieu truong du lieu trong JSON"

    # 1. Kiểm tra Cửa sổ thời gian (Timestamp)
    if abs(current_time - ts) > DELTA_T:
        return False, f"REJECT: Gia tri Timestamp quai han (|{int(current_time - ts)}s| > {DELTA_T}s)"

    # 2. Kiểm tra Sequence Number & Replay Cache (Nonce)
    if seq <= last_seq:
        return False, f"REJECT: Sequence Number bi lặp hoặc cũ (seq={seq} <= last={last_seq})"
    
    if nonce in replay_cache:
        return False, f"REJECT: Nonce da ton tai trong Replay Cache (nonce={nonce})"

    # 3. Tính toán lại mã HMAC để kiểm tra Tính toàn vẹn (Integrity)
    raw_payload = f"{device_id}{cmd}{ts}{seq}{nonce}"
    expected_mac = hmac.new(SECRET_KEY, raw_payload.encode('utf-8'), hashlib.sha256).hexdigest()

    if not hmac.compare_digest(expected_mac, received_mac):
        return False, "REJECT: Sai ma HMAC (Payload bi can thiep hoac sai khoa)"

    # --- NẾU TẤT CẢ ĐỀU HỢP LỆ ---
    last_seq = seq
    replay_cache.add(nonce)
    return True, f"ACCEPT: Lenh {cmd} hop le! Mo khoa cua thanh cong."

# --- CALLBACK CỦA MQTT BROKER ---
def on_message(client, userdata, msg):
    try:
        payload_str = msg.payload.decode('utf-8')
        data = json.loads(payload_str)
        
        print("\n-------------------------------------------")
        print(f"[REC] Nhan goi tin tu topic '{msg.topic}':")
        print(json.dumps(data, indent=2))
        
        is_valid, reason = verify_message(data)
        
        if is_valid:
            print(f"✅ {reason}")
        else:
            print(f"❌ {reason}")
            
    except Exception as e:
        print(f"⚠️ Lỗi xử lý gói tin: {e}")

# --- KẾT NỐI VÀ LẮNG NGHE ---
client = mqtt.Client()
client.on_message = on_message

print("🚀 Gateway dang khoi dong va lang nghe tren topic 'iot/lock'...")
client.connect("localhost", 1883, 60)
client.subscribe("iot/lock")
client.loop_forever()
