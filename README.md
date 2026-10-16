# Báo cáo thực hành: Kiểm thử hiệu năng API kiểm tra số nguyên tố

## 1. Giới thiệu đề tài

Sản phẩm thực hành xây dựng một API HTTP nhỏ bằng Python và Flask để xác định một số nguyên có phải số nguyên tố hay không, sau đó dùng Apache JMeter kiểm thử chức năng và tải cơ bản. Phạm vi chỉ gồm API và kịch bản kiểm thử; không có website, giao diện frontend hay cơ sở dữ liệu.

Thời lượng gợi ý: khoảng 60 phút, bao gồm cài đặt, chạy thử API, chạy JMeter và ghi nhận kết quả trên máy cá nhân.

## 2. Mục tiêu kiểm thử

- Xác minh API trả kết quả đúng với số nguyên tố, hợp số, số âm, 0 và 1.
- Xác minh đầu vào thiếu hoặc không phải số nguyên trả HTTP 400 cùng thông báo JSON.
- Dùng JMeter quan sát thời gian phản hồi và thông lượng dưới tải nhỏ, có kiểm soát.
- Ghi số request, request lỗi, error rate, thời gian phản hồi trung bình, percentile 90 và throughput từ lần chạy thực tế.

## 3. Công nghệ sử dụng

- Python 3 và Flask: triển khai API HTTP.
- Apache JMeter 5.x: kiểm thử chức năng và tải.
- XML/JMX: lưu test plan mở được trong giao diện JMeter.
- Git/GitHub: quản lý và chia sẻ mã nguồn.

Không sử dụng dịch vụ bên ngoài, cơ sở dữ liệu hay thư viện JMeter bổ sung.

## 4. Mô tả thuật toán kiểm tra số nguyên tố

Hàm `is_prime` trong `app.py` xử lý các trường hợp nhỏ trước: số nhỏ hơn 2 không phải số nguyên tố; 2 là số nguyên tố; các số chẵn lớn hơn 2 là hợp số. Với số lẻ còn lại, thuật toán thử các ước lẻ từ 3 đến căn bậc hai nguyên của số đó. Nếu không có ước nào chia hết thì số đó là số nguyên tố.

Độ phức tạp thời gian trong trường hợp tổng quát là O(√n); bộ nhớ phụ trợ là O(1).

## 5. Mô tả API

API mặc định chạy tại `http://127.0.0.1:5000`.

| Phương thức | Đường dẫn | Mô tả |
|---|---|---|
| GET | `/` | Trả thông báo API đang hoạt động dưới dạng JSON. |
| GET | `/is-prime?n=97` | Kiểm tra số nguyên và trả đầu vào, kết quả đúng/sai cùng thời gian xử lý thuật toán tính bằng mili giây. |

Ví dụ phản hồi thành công:

```json
{
  "input": 97,
  "is_prime": true,
  "processing_time_ms": 0.004
}
```

Thời gian cụ thể thay đổi theo lần chạy và máy. Khi thiếu `n` hoặc `n` không thể chuyển thành số nguyên, API trả HTTP 400 và JSON có khóa `error`. Số âm, 0 và 1 là đầu vào hợp lệ về kiểu dữ liệu; kết quả kiểm tra của chúng là `false`.

## 6. Thiết kế kịch bản kiểm thử

### Kiểm thử chức năng — `jmeter/functional_test.jmx`

Một Thread Group chạy tuần tự ba request:

1. `n=97`: kỳ vọng HTTP 200, `input=97`, `is_prime=true`.
2. `n=100`: kỳ vọng HTTP 200, `input=100`, `is_prime=false`.
3. `n=abc`: kỳ vọng HTTP 400 và nội dung lỗi cho biết `n` phải là số nguyên.

Mỗi request có Response Assertion kiểm tra mã HTTP; assertion nội dung kiểm tra các trường JSON cần thiết. Có thể mở View Results Tree để xem request, response và trạng thái assertion.

### Kiểm thử tải — `jmeter/load_test.jmx`

Mỗi vòng lặp gửi bốn request với các giá trị 2, 97, 104729 và 1000000. Kịch bản chỉ gọi API cục bộ, kiểm tra mỗi phản hồi có HTTP 200, và có Summary Report cùng Aggregate Report để xem số mẫu, số lỗi, thời gian và throughput. Với cấu hình mặc định, tổng số mẫu dự kiến là 10 × 10 × 4 = 400; đây là số lượng suy ra từ cấu hình, không phải kết quả của một lần chạy.

## 7. Cấu hình Thread Group

| Tham số | Kiểm thử chức năng | Kiểm thử tải |
|---|---:|---:|
| Số người dùng ảo (threads) | 1 | 10 |
| Ramp-up (giây) | 1 | 5 |
| Loop Count | 1 | 10 |
| Request mỗi vòng lặp | 3 | 4 |
| Tổng request dự kiến | 3 | 400 |

Các test plan đặt biến `SERVER_HOST=127.0.0.1` và `SERVER_PORT=5000` ở Test Plan → User Defined Variables. Thay giá trị tại đây nếu API chạy ở địa chỉ/cổng khác.

## 8. Hướng dẫn cài đặt và chạy

### Cài đặt và chạy API (PowerShell)

Mở PowerShell tại thư mục repository:

```powershell
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python app.py
```

Nếu PowerShell không cho kích hoạt virtual environment, có thể bỏ qua bước Activate và chạy trực tiếp:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe app.py
```

Giữ cửa sổ API đang chạy. Mở một PowerShell khác để kiểm tra:

```powershell
Invoke-RestMethod http://127.0.0.1:5000/
Invoke-RestMethod "http://127.0.0.1:5000/is-prime?n=97"
Invoke-RestMethod "http://127.0.0.1:5000/is-prime?n=100"
try {
    Invoke-WebRequest "http://127.0.0.1:5000/is-prime?n=abc"
} catch {
    [int]$_.Exception.Response.StatusCode
}
```

Request cuối phải có HTTP 400.

### Cài đặt và chạy Apache JMeter

1. Cài Java nếu máy chưa có Java runtime.
2. Tải bản Apache JMeter 5.x từ trang chính thức trong mục tài liệu tham khảo; giải nén, không cần cài đặt bằng trình cài đặt.
3. Mở `bin\jmeter.bat` để chạy giao diện JMeter.
4. Trong JMeter, chọn **File → Open**, mở lần lượt `jmeter\functional_test.jmx` và `jmeter\load_test.jmx`, sau đó bấm **Start**.
5. Chạy kiểm thử chức năng trước. Xem **View Results Tree** và xác nhận các assertion đều thành công. Với kiểm thử tải, đọc **Summary Report** và **Aggregate Report** sau khi chạy xong.

Có thể chạy không giao diện từ PowerShell, thay đường dẫn dưới đây bằng nơi đã giải nén JMeter:

```powershell
& "C:\tools\apache-jmeter-5.6.3\bin\jmeter.bat" -n -t ".\jmeter\functional_test.jmx" -l ".\results\functional-results.jtl"
& "C:\tools\apache-jmeter-5.6.3\bin\jmeter.bat" -n -t ".\jmeter\load_test.jmx" -l ".\results\load-results.jtl" -e -o ".\results\load-report"
```

Đảm bảo thư mục `results` đã tồn tại trước khi chạy. Báo cáo HTML cần một thư mục output mới hoặc trống. Các file kết quả `.jtl` và báo cáo HTML được loại khỏi Git theo `.gitignore`; chỉ đưa chúng vào repository nếu muốn chia sẻ dữ liệu đo và điều chỉnh `.gitignore`.

## 9. Bảng ghi nhận kết quả thực nghiệm

**Trạng thái ban đầu:** chưa chạy JMeter trong môi trường này; chưa có dữ liệu thực nghiệm. Không điền số liệu dự đoán vào bảng dưới đây. Sau khi chạy thật, chép các giá trị từ Summary/Aggregate Report hoặc báo cáo HTML vào bảng.

| Kịch bản/lần chạy | Số request | Request lỗi | Error rate (%) | Average response time (ms) | 90th percentile (ms) | Throughput (requests/giây) |
|---|---:|---:|---:|---:|---:|---:|
| Functional test | — | — | — | — | — | — |
| Load test | — | — | — | — | — | — |

Error rate = số request lỗi / tổng số request × 100%. Trong JMeter, lấy số lỗi và tổng mẫu trong Summary/Aggregate Report; thời gian trung bình và percentile 90 ở các cột tương ứng; throughput là throughput của báo cáo. Ghi rõ ngày chạy, cấu hình máy, phiên bản Java/JMeter và có tính request lỗi assertion hay không để người khác diễn giải kết quả chính xác.

## 10. Phân tích kết quả và kết luận

Hiện chưa có lần chạy JMeter thực tế nên chưa thể kết luận về response time, throughput hoặc khả năng chịu tải. Sau khi đo, kiểm tra trước rằng request lỗi bằng 0 (hoặc giải thích lỗi), rồi so sánh average và 90th percentile. Throughput chỉ có ý nghĩa khi so sánh cùng máy, cùng cấu hình tải và cùng điều kiện chạy; đây là bài thực hành tải nhỏ, không phải phép đo năng lực production.

Khi hoàn tất đo đạc, ghi nhận liệu các test chức năng đạt assertion và đối chiếu số mẫu thực tế với 400 request dự kiến của load test. Đính kèm ảnh chụp và không thay thế số liệu thu được bằng số liệu ước lượng.

## 11. Ảnh minh họa cần chụp

Lưu ảnh chụp màn hình thật vào thư mục `screenshots/` sau khi tự chạy thử. Không có ảnh minh họa được tạo sẵn.

- **API đang chạy và response JSON:** `screenshots/api-response.png`
- **Functional test với assertion thành công:** `screenshots/functional-test.png`
- **Load test — Summary/Aggregate Report:** `screenshots/load-test-summary.png`
- **(Tùy chọn) Báo cáo HTML của JMeter:** `screenshots/load-test-dashboard.png`

Chèn ảnh sau khi chụp:

```markdown
![API trả về JSON](screenshots/api-response.png)
![Kết quả kiểm thử chức năng](screenshots/functional-test.png)
![Tóm tắt kiểm thử tải](screenshots/load-test-summary.png)
```

## 12. Cấu trúc repository và tài liệu tham khảo

```text
.
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
├── jmeter/
│   ├── functional_test.jmx
│   └── load_test.jmx
├── results/
│   └── .gitkeep
└── screenshots/
    └── .gitkeep
```

Tài liệu chính thức:

- Apache JMeter: <https://jmeter.apache.org/>
- Apache JMeter — Getting Started: <https://jmeter.apache.org/usermanual/get-started.html>
- Flask — Quickstart: <https://flask.palletsprojects.com/en/stable/quickstart/>
- Python — `math.isqrt`: <https://docs.python.org/3/library/math.html#math.isqrt>

### Tạo GitHub Repository và push bằng PowerShell

1. Tạo repository GitHub mới (ví dụ `jmeter-prime-api`); nếu đã có README trên GitHub thì nên tạo repository trống để tránh xung đột ban đầu.
2. Mở PowerShell trong thư mục gốc repository, thay URL bằng URL repository của bạn, rồi chạy:

```powershell
git init
git add .
git commit -m "Add prime API and JMeter practice tests"
git branch -M main
git remote add origin "https://github.com/<username>/jmeter-prime-api.git"
git push -u origin main
```

GitHub sẽ yêu cầu xác thực qua trình duyệt hoặc credential manager. Không ghi token hay mật khẩu vào mã nguồn hoặc URL remote. Nếu `origin` đã tồn tại, kiểm tra bằng `git remote -v` và cập nhật URL bằng `git remote set-url origin "<repository-url>"` thay vì thêm remote lần nữa.
