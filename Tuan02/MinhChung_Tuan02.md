

## 1. Thông tin sinh viên & Đề tài
- [cite_start]**Họ và tên:** Phạm Ngọc Anh 
- [cite_start]**Mã sinh viên:** 231A010382 
- [cite_start]**Tên đề tài:** Chống replay attack trong giao tiếp IoT 
- [cite_start]**Học phần:** INT4410 - Bảo mật trong IoT [cite: 1]

---

## 2. Chuỗi tấn công (Attack Chain) Mô phỏng
Kịch bản tấn công phát lại (Replay Attack) được thực hiện qua 3 giai đoạn cốt lõi:
- **Bước 1 (Sniffing):** Thiết bị IoT giả lập gửi gói tin hợp lệ mang lệnh điều khiển (ví dụ: `{"command": "unlock"}`) tới MQTT Broker. Kẻ tấn công sử dụng các công cụ nghe lén traffic mạng để bắt và lưu trữ lại gói tin này.
- **Bước 2 (Lưu trữ):** Gói tin được giữ nguyên cấu trúc cấu thành bao gồm cả các thông tin định danh mà không cần phải giải mã nội dung bên trong.
- **Bước 3 (Replay):** Kẻ tấn công thực hiện "bơm" ngược (phát lại) chính gói tin đó vào mạng hướng tới MQTT Broker. Do hệ thống không kiểm tra tính tươi mới của dữ liệu, Broker vẫn công nhận gói tin hợp lệ và thực thi lệnh mở cửa một lần nữa.

---

## 3. Bảng điều kiện khai thác (Exploit Conditions)

| STT | Điều kiện cần thiết để khai thác | Mô tả chi tiết trong môi trường IoT |
| :---: | :--- | :--- |
| 1 | Thiếu tính tươi mới của dữ liệu (Data Freshness) | Luồng truyền thông giữa thiết bị IoT và Broker không tích hợp cơ chế kiểm tra thời gian (Timestamp) hoặc số ngẫu nhiên dùng một lần (Nonce). |
| 2 | Kênh truyền không có tính năng chống phát lại | Giao thức MQTT cấu hình ở dạng mặc định, không triển khai TLS/DTLS hoặc tầng ứng dụng không tự xử lý việc xác thực chống Replay. |
| 3 | Khả năng tiếp cận mạng | Kẻ tấn công nằm trong cùng phân đoạn mạng nội bộ hoặc chiếm quyền giám sát luồng traffic đi qua thiết bị Gateway. |

---

## 4. Mô tả môi trường Lab cô lập trên VMware
Hệ thống được triển khai giả lập hoàn toàn trong môi trường ảo hóa biệt lập nhằm đảm bảo an toàn, không gây hại đến hạ tầng mạng thực tế:

- **Máy ảo 1 - Trung tâm điều phối (MQTT Broker):** Chạy hệ điều hành Ubuntu Server, cài đặt và cấu hình dịch vụ Eclipse Mosquitto để tiếp nhận và xử lý các gói tin truyền thông.
- **Máy ảo 2 - Giả lập thiết bị (IoT Device Simulator):** Chạy script Python sử dụng thư viện `paho-mqtt` để tự động gửi các lệnh điều khiển định kỳ về Broker.
- **Máy ảo 3 - Máy tấn công (Attacker Machine):** Sử dụng hệ điều hành Kali Linux tích hợp công cụ Wireshark để capture traffic, kết hợp script Python (Scapy/Raw Sockets) phục vụ hành vi phát lại gói tin.
- **Giám sát tập trung (SIEM):** Tích hợp nền tảng Wazuh thu thập log từ MQTT Broker để phân tích hành vi, thiết lập luật cảnh báo khi phát hiện dấu hiệu gói tin bị rớt hàng loạt do lỗi xác thực.
- **Cấu hình mạng:** Sử dụng chế độ mạng nội bộ (Host-Only hoặc NAT) trên VMware để cô lập hoàn toàn lưu lượng mạng kiểm thử.

---

## 5. Kế hoạch triển khai chi tiết
- **Nhiệm vụ 1:** Hoàn tất cấu hình mạng cho các máy ảo trên VMware, đảm bảo các máy ping thấy nhau ổn định.
- **Nhiệm vụ 2:** Viết hoàn chỉnh script Python tạo luồng giao tiếp IoT cơ bản và tiến hành sniff dữ liệu bằng Wireshark.
- **Nhiệm vụ 3:** Thực hiện kịch bản Replay Attack thành công, thu thập file log và chụp lại ảnh minh chứng ban đầu.

---

## 6. Danh mục tài liệu tham khảo ban đầu
1. *OASIS Standard:* MQTT Version 5.0 Protocol Specification.
2. *OWASP Foundation:* OWASP Top 10 IoT Vulnerabilities Guidance.
3. *Thư viện mã nguồn mở:* `paho-mqtt` - Eclipse Paho MQTT Python Client Library Core Tool.
4. *Tài liệu kỹ thuật:* Nghiên cứu về lỗ hổng Replay Attack trong hạ tầng nhà thông minh và giải pháp phòng ngừa tầng ứng dụng.
5. *Hệ thống giám sát:* Wazuh Core Documentation - Cấu hình Log Analysis và tạo Custom Rules cảnh báo.
