# Bản Phát Hành AutoClip-Pro v0.2.0

**Ngày Phát Hành:** 13/04/2026

Bản cập nhật v0.2.0 mang đến một loạt các tính năng mới đột phá, tập trung tối ưu hóa nhận diện ngôn ngữ (đặc biệt là Tiếng Việt), cải thiện giao diện tương tác, và bổ sung khả năng xử lý hình ảnh thông minh bằng AI. So với phiên bản v0.1.0 (nhánh main trên Github), v0.2.0 là một bước tiến vượt bậc về chất lượng và tốc độ.

## 🚀 Các Tính Năng Mới & Cải Tiến Đáng Chú Ý

### 1. 🇻🇳 Tối ưu Hóa Nhận Diện Tiếng Việt & GPU (Whisper)
- **Tăng Tốc qua phần cứng (Hardware Acceleration):** Tích hợp phân giải tự động phần cứng, ưu tiên chạy Whisper Engine trên GPU **MPS** của thiết bị Apple Silicon hoặc **CUDA**. Thời gian dịch Transcribe rút ngắn xuống từ 3-5 lần so với CPU.
- **Whisper "Warm" Singleton Mode:** Chuyển đổi trạng thái xử lý Model sang Singleton. Dữ liệu Model được nạp một lần và lưu trực tiếp trong bộ nhớ hệ thống (Memory), **tiết kiệm từ 5 - 15 giây** cho những lần xử lý tiếp theo vì không cần tải lại Model.
- **Tiếng Việt Siêu Chuẩn:** 
  - Mặc định Model chuyển từ `base` lên thành `medium`.
  - Tuỳ chỉnh tham số giảm ảo giác (Hallucination) triệt để: Sử dụng Greedy Decoding (`temperature=0`), `beam_size=5` và `word_timestamps=True`.
  - Trang bị **`_VIETNAMESE_INITIAL_PROMPT`** ép Whisper khởi tạo chuẩn ngữ cảnh và giữ chuẩn âm điệu của người Việt.

### 2. 📱 Khung Hình Dọc Cải Tiến (Vertical Crop AI)
- Loại bỏ kiểu crop chết từ giữa màn hình bằng lệnh `ffmpeg` trước đây.
- Thích hợp thư viện mới **`auto_reframe.py`**: Tích hợp trí tuệ nhân tạo (AI) trong việc nhận diện và tự động quay, lấy nét trọn vẹn chủ thể (Khuôn mặt), khiến cho clip tạo cho Tiktok/Reels mượt mà và tập trung hơn.

### 3. 📂 Hỗ trợ Đăng tải Video (File Upload)
- Bổ sung đường dẫn Endpoint `/jobs/upload` cho phép API đón nhận đầu vào là Video Upload trực tiếp thay vì chỉ nhận qua đường link URL.
- Phân tích linh hoạt trường dữ liệu thông qua thư viện `ffprobe` nhằm đưa ra độ dài thời gian phân giải chính xác (Duration Extraction).

### 4. 🗂️ Phân Tách Mục Đích Tính Năng (Task Type Choice)
- Khai báo thêm thuộc tính Database: Bổ sung Job Schema cung cấp lựa chọn **chỉ cần làm Transcript** chứ không cần cắt gọt Clips (`task_type`). 
- Nếu chọn `task_type="transcribe"`, hệ thống tiến hành tạo ra `transcript.txt` qua `transcript_url` mà không đòi hỏi Render lãng phí. 
- Hệ thống Concurrent Thread nâng từ 2 lên 4 `max_workers` hỗ trợ chia tải đồng thời đa nhiệm luồng lớn.

### 5. 🖥️ Giao diện Chọn Lựa Người dùng
- Cập nhật **Next.js Frontend UI**.
- Trang chủ giờ hỗ trợ Tab Switch dễ nhận dạng **Upload Local Video** và **YouTube Link**.
- Hỗ trợ Select ngôn ngữ và tính năng bật tắt "chỉ lấy bản dịch Transcribe".

## Tương Quan Bảng So Sánh Báo Cáo

| Tính Năng | v1.0.0 (Github Main) | v2.0.0 (Hiện Tại - Local) |
| --- | --- | --- |
| **Whisper Platform** | CPU | Multi platforms (MPS, CUDA) ~ 3-5x Faster |
| **Model State** | Reload per Job | Warm Singleton |
| **Vietnamese Detect** | Poor, Base Model | Excellent, Medium Model + Prompt Injection |
| **Video Format (9:16)**| Static crop | AI Face Tracking Crop |
| **Data Ingestion** | Online URLs Exclusively | Allow Uploads Offline (.mp4/.mov) |
| **Threads Support** | 2 Workers | 4 Workers |

**Note cho Developer:** Nhớ kiểm tra `configs/pipeline.yaml` và `.env.example` để xác nhận cấu hình Model Medium đã được bật trước khi khởi chạy.
