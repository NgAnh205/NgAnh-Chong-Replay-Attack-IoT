#include <WiFi.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>
#include "mbedtls/md.h"

const char* ssid = "Wokwi-GUEST";
const char* password = "";
const char* mqtt_server = "test.mosquitto.org";
const char* secret_key = "SecretKey123";

WiFiClient espClient;
PubSubClient client(espClient);

int sequence = 1;

void setup() {
  Serial.begin(115200);
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) { delay(500); }
  client.setServer(mqtt_server, 1883);
}

// Hàm băm HMAC-SHA256
String generateHMAC(String payload) {
  byte hmacResult[32];
  mbedtls_md_context_t ctx;
  mbedtls_md_type_t md_type = MBEDTLS_MD_SHA256;
  
  mbedtls_md_init(&ctx);
  mbedtls_md_setup(&ctx, mbedtls_md_info_from_type(md_type), 1);
  mbedtls_md_hmac_starts(&ctx, (const unsigned char *) secret_key, strlen(secret_key));
  mbedtls_md_hmac_update(&ctx, (const unsigned char *) payload.c_str(), payload.length());
  mbedtls_md_hmac_finish(&ctx, hmacResult);
  mbedtls_md_free(&ctx);

  String hash = "";
  for(int i=0; i<32; i++) {
    char str[3];
    sprintf(str, "%02x", (int)hmacResult[i]);
    hash += str;
  }
  return hash;
}

void sendSecureMessage() {
  long timestamp = time(nullptr); // Lấy thời gian thực
  String nonce = String(random(10000, 99999)); // Sinh nonce ngẫu nhiên
  
  // 1. Tạo chuỗi dữ liệu gốc
  String raw_payload = "{\"device_id\":\"ESP32_Door_01\",\"command\":\"UNLOCK\",\"timestamp\":" + String(timestamp) + ",\"sequence\":" + String(sequence) + ",\"nonce\":\"" + nonce + "\"}";
  
  // 2. Tính HMAC
  String hmac_sig = generateHMAC(raw_payload);
  
  // 3. Đóng gói JSON cuối cùng
  String final_payload = "{\"device_id\":\"ESP32_Door_01\",\"command\":\"UNLOCK\",\"timestamp\":" + String(timestamp) + ",\"sequence\":" + String(sequence) + ",\"nonce\":\"" + nonce + "\",\"hmac\":\"" + hmac_sig + "\"}";
  
  client.publish("iot/door/control", final_payload.c_str());
  sequence++;
}

void loop() {
  if (!client.connected()) { client.connect("ESP32_Door_01"); }
  client.loop();
  
  // Nút nhấn để gửi lệnh (Giả lập)
  // if (digitalRead(BUTTON_PIN) == LOW) { sendSecureMessage(); delay(1000); }
}
