# Dự án: Chống Replay Attack trong giao tiếp IoT

Đây là kho lưu trữ mã nguồn và tài liệu cho đề tài chống Replay Attack sử dụng cơ chế Timestamp, Sequence Number, Nonce và HMAC-SHA256.

## Cấu trúc thư mục
* `configs/` : Tệp cấu hình Mosquitto Broker.
* `src/`     : Mã nguồn Python (Gateway/Attacker) và Wokwi ESP32.
* `results/` : Bằng chứng kiểm thử (Log/Ảnh chụp).
* `report/`  : Báo cáo tiểu luận.
* `slides/`  : Slide bảo vệ.
## Nhật ký cập nhật
- Tuần 01: Hoàn thiện đề cương, xác định Đề tài 24 – hướng D.
- Tuần 02: Hoàn thành Chương 1, viết nháp 50-70% Chương 2.
- Tuần 03: Hoàn chỉnh Chương 2-3, khởi tạo Gateway và cấu hình Mosquitto.
- Tuần 04: Triển khai 4 kịch bản KB-01 đến KB-04, thu log và ảnh minh chứng.
