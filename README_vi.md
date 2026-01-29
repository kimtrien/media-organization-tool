# Công Cụ Sắp Xếp Media

Công cụ GUI Windows nhẹ để sắp xếp các tệp ảnh và video theo ngày EXIF/Metadata thành cấu trúc thư mục có tổ chức.

## Tính Năng

- **Hỗ Trợ Video & HEIC**: Xử lý mượt mà ảnh, video (MP4, MOV,...) và tệp HEIC.
- **Quản Lý Trùng Lặp Thông Minh**:
  - **So Sánh Binary**: Tùy chọn kiểm tra từng bit (Binary Match) để xác định chính xác các tệp giống hệt nhau.
  - **Tự Động Đánh Dấu**: Các tệp giống hệt nhau sẽ được tự động chọn để xóa, giúp bạn tiết kiệm thời gian.
  - **Xóa Theo Lô**: Xem xét toàn bộ danh sách trùng lặp trước, sau đó xóa tất cả các tệp đã chọn chỉ với một cú nhấp chuột.
- **Vận Hành An Toàn**:
  - **Tích Hợp Thùng Rác**: Các tệp bị xóa sẽ được đưa vào Thùng Rác (Recycle Bin) của Windows, không phải xóa vĩnh viễn.
  - **Không Ghi Đè**: Không bao giờ ghi đè lên tệp hiện có; các tệp trùng lặp luôn được giữ lại để bạn xem xét.
- **Trải Nghiệm Người Dùng (UX) Cải Tiến**:
  - **Phím Tắt**: Sử dụng phím `←`/`→` để điều hướng, phím `Space` hoặc `X` để đánh dấu xóa.
  - **Tải Ảnh Bất Đồng Bộ**: Xem trước ảnh được tải ngầm, giúp giao diện luôn mượt mà và không bị khựng.
  - **Giao Diện Chuyên Nghiệp**: Biểu tượng ứng dụng chất lượng cao và bố cục sạch sẽ.
- **Tính Di Động**: Bao gồm tệp `.exe` độc lập để sử dụng ngay mà không cần cài đặt Python.
- **Nhật Ký Theo Phiên**: Lưu trữ nhật ký, báo cáo thành công và danh sách tệp lỗi trong các thư mục riêng biệt theo thời gian.
- **Lịch Sử Thông Minh**: Ghi nhớ các thư mục đích bạn đã sử dụng gần đây.
- **Đáng Tin Cậy**: Xử lý hơn 10,000 tệp với cơ chế xử lý lỗi toàn diện và chạy đa luồng.

## Định Dạng Được Hỗ Trợ

### Ảnh (Images)
- `.jpg` / `.jpeg`, `.png`, `.heic`, `.webp`, `.gif`, `.bmp`, `.tiff`

### Video
- `.mp4`, `.mov`, `.avi`, `.mkv`, `.wmv`, `.flv`, `.webm`, `.m4v`, `.3gp`

## Thứ Tự Ưu Tiên Trích Xuất Ngày

### Ảnh
1. EXIF `DateTimeOriginal`
2. EXIF `DateTimeDigitized`
3. EXIF `DateTime`
4. Thời gian sửa đổi tệp (dự phòng)

### Video
1. Video `creation_time` metadata
2. Thời gian sửa đổi tệp (dự phòng)

## Cài Đặt (Cho Lập Trình Viên)

### 1. Yêu Cầu
- **Python 3.10+**
- **FFmpeg**: Cần thiết để trích xuất metadata video (phải có trong PATH hệ thống)

### 2. Thiết Lập
```powershell
# Tạo & Kích hoạt môi trường ảo
python -m venv venv
.\venv\Scripts\Activate.ps1

# Cài đặt thư viện
pip install -r requirements.txt
```

## Cách Sử Dụng

1. **Chọn Thư Mục**: Chọn Thư mục nguồn (chứa ảnh) và Thư mục đích (nơi lưu trữ).
2. **Tùy Chọn**: 
   - Tích "Move files" nếu muốn di chuyển (xóa gốc sau khi chép).
   - Tích "Check for Duplicate Content" để dùng so sánh Binary chính xác hơn.
3. **Bắt Đầu**: Nhấn "Start Processing".
4. **Xem Xét Trùng Lặp**:
   - Điều hướng bằng nút bấm hoặc phím `←` / `→`.
   - Đánh dấu xóa bằng checkbox hoặc phím `Space`/`X`.
   - Các tệp giống hệt nhau sẽ được đánh dấu **[DEL]** tự động.
   - Nhấn **"DELETE MARKED FILES NOW"** để đưa chúng vào Thùng Rác.

## Cấu Trúc Dự Án
- `main.py`: Giao diện chính và điều phối.
- `copier.py`: Logic xử lý chính và so sánh binary.
- `duplicate_ui.py`: Giao diện review nâng cao với tải ảnh bất đồng bộ.
- `exif_reader.py`: Trích xuất metadata cho ảnh và video.
- `scanner.py`: Quét tệp đệ quy.

## Xử Lý Lỗi
Tất cả nhật ký được lưu trong `logs/<dấu_thời_gian>/`:
- `session.log`: Chi tiết kỹ thuật đầy đủ.
- `success_report.txt`: Danh sách tệp đã sắp xếp thành công.
- `invalid_files.log`: Tệp bị bỏ qua do hỏng hoặc thiếu dữ liệu.
- `duplicate_report.txt`: Tổng hợp các cặp tệp trùng lặp tìm thấy.

## Giấy Phép
Cung cấp nguyên trạng cho mục đích sử dụng cá nhân.
