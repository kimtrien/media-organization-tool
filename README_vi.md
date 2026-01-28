# Công Cụ Sắp Xếp Ảnh

Công cụ GUI Windows nhẹ để sắp xếp các tệp ảnh theo ngày EXIF thành cấu trúc thư mục có tổ chức.

## Tính Năng

- **Icon Chuyên Nghiệp**: Biểu tượng ứng dụng tùy chỉnh chất lượng cao
- **Tệp Thực Thi Duy Nhất**: Được đóng gói thành tệp `.exe` độc lập để dễ dàng di chuyển
- **Quét Đệ Quy**: Quét thư mục nguồn với độ sâu không giới hạn
- **Trích Xuất Ngày EXIF**: Trích xuất ngày từ metadata ảnh với cơ chế dự phòng thông minh
- **Sắp Xếp Theo Ngày**: Tổ chức ảnh theo cấu trúc `YYYY/MM/DD/tên_tệp`
- **Phát Hiện Trùng Lặp**: Không bao giờ ghi đè các tệp hiện có
- **Xem Xét Trùng Lặp Thủ Công**: So sánh ảnh cạnh nhau với các tùy chọn quyết định thủ công
- **Tối Ưu Hiệu Suất**: Xử lý mượt mà hơn 10,000 ảnh
- **Giao Diện Phản Hồi**: Xử lý nền giữ cho giao diện luôn phản hồi
- **Xử Lý Lỗi Toàn Diện**: Tiếp tục xử lý ngay cả khi gặp tệp bị hỏng

## Định Dạng Ảnh Được Hỗ Trợ

- `.jpg` / `.jpeg`
- `.png`
- `.heic`
- `.webp`

## Thứ Tự Ưu Tiên Trích Xuất Ngày

1. EXIF `DateTimeOriginal` (đáng tin cậy nhất)
2. EXIF `DateTimeDigitized`
3. EXIF `DateTime`
4. Thời gian sửa đổi tệp (dự phòng)

## Cài Đặt

### 1. Tạo Môi Trường Ảo

```powershell
# Di chuyển đến thư mục dự án
cd g:\project\ToolScanAnh

# Tạo môi trường ảo
python -m venv venv

# Kích hoạt môi trường ảo
.\venv\Scripts\Activate.ps1
```

Nếu gặp lỗi chính sách thực thi, chạy lệnh:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### 2. Cài Đặt Các Thư Viện Phụ Thuộc

```powershell
pip install -r requirements.txt
```

## Sử Dụng

### Chạy Công Cụ

```powershell
# Đảm bảo môi trường ảo đã được kích hoạt
.\venv\Scripts\Activate.ps1

# Chạy ứng dụng
python main.py
```

### Quy Trình Làm Việc

1. **Chọn Thư Mục Nguồn**: Nhấp "Browse" bên cạnh "Source Folder" và chọn thư mục chứa ảnh của bạn
2. **Chọn Thư Mục Đích**: Nhấp "Browse" bên cạnh "Destination Folder" và chọn nơi lưu ảnh đã sắp xếp
3. **Bắt Đầu Xử Lý**: Nhấp nút "Start Processing"
4. **Theo Dõi Tiến Trình**: Xem thanh tiến trình và nhật ký cập nhật theo thời gian thực
5. **Xem Xét Trùng Lặp** (nếu có):
   - Sau khi xử lý, bạn sẽ được nhắc xem xét các tệp trùng lặp
   - Xem so sánh cạnh nhau giữa tệp nguồn và tệp hiện có
   - Chọn hành động cho mỗi tệp trùng lặp:
     - **Skip**: Giữ cả hai tệp (không làm gì)
     - **Replace**: Thay thế tệp hiện có bằng tệp nguồn
     - **Delete Source**: Giữ tệp hiện có, xóa tệp nguồn

### Báo Cáo Trùng Lặp

Sau khi xử lý, tệp `duplicate_report.txt` được tạo trong thư mục công cụ với định dạng:

```
ĐƯỜNG_DẪN_TỆP_NGUỒN  -->  ĐƯỜNG_DẪN_TỆP_ĐÍCH_HIỆN_CÓ
```

## Cấu Trúc Dự Án

```
ToolScanAnh/
├── main.py              # GUI chính và điều phối
├── scanner.py           # Quét tệp đệ quy
├── exif_reader.py       # Trích xuất ngày EXIF
├── copier.py            # Sao chép tệp với phát hiện trùng lặp
├── duplicate_ui.py      # Cửa sổ xem xét trùng lặp thủ công
├── utils.py             # Tiện ích dùng chung
├── requirements.txt     # Thư viện Python phụ thuộc
├── README.md            # Tệp này (tiếng Anh)
├── README_vi.md         # Tệp này (tiếng Việt)
└── venv/                # Môi trường ảo (do bạn tạo)
```

## Xử Lý Lỗi

Công cụ được thiết kế để không bao giờ bị crash:

- **Ảnh Bị Hỏng**: Được ghi nhật ký và bỏ qua, tiếp tục xử lý
- **Thiếu EXIF**: Dự phòng sang thời gian sửa đổi tệp
- **Lỗi Quyền Truy Cập**: Được ghi nhật ký và bỏ qua
- **Đĩa Đầy**: Dừng một cách nhẹ nhàng với thông báo lỗi

Tất cả lỗi được ghi vào:
- Tệp `image_tool.log`
- Cửa sổ nhật ký UI

## Hiệu Suất

Các tối ưu hóa để xử lý bộ sưu tập ảnh lớn:

- Quét dựa trên generator (sử dụng bộ nhớ thấp)
- Đọc EXIF chỉ metadata (nhanh)
- Tải ảnh lười biếng (chỉ khi xem trước)
- Tạo thumbnail cho xem trước (tối đa 400x400)
- Cập nhật UI theo lô (mỗi 10 tệp)
- Threading nền (UI phản hồi)

Đã kiểm tra với hơn 10,000 ảnh.

## Khắc Phục Sự Cố

### Tệp HEIC Không Hoạt Động

Nếu tệp HEIC không xử lý được, đảm bảo `pillow-heif` đã được cài đặt:

```powershell
pip install pillow-heif
```

### Vấn Đề Kích Hoạt Môi Trường Ảo

Nếu `.\venv\Scripts\Activate.ps1` thất bại, thử:

```powershell
# Kiểm tra chính sách thực thi
Get-ExecutionPolicy

# Đặt thành RemoteSigned nếu cần
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### GUI Không Khởi Chạy

Đảm bảo bạn đang sử dụng Python 3.10+ với hỗ trợ tkinter:

```powershell
python --version
python -m tkinter
```

## Giấy Phép

Công cụ này được cung cấp nguyên trạng cho mục đích sử dụng cá nhân.

## Hỗ Trợ

Đối với các vấn đề hoặc câu hỏi, kiểm tra các tệp nhật ký:
- `image_tool.log` - Nhật ký xử lý chi tiết
- `duplicate_report.txt` - Báo cáo tệp trùng lặp
