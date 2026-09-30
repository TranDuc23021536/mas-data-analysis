# Multi-Agent Data Analysis System

Hệ thống AI đa tác tử cho phép người dùng hỏi về dữ liệu kinh doanh bằng ngôn ngữ tự nhiên (tiếng Việt), hệ thống tự sinh câu lệnh SQL, truy vấn cơ sở dữ liệu, phân tích kết quả, vẽ biểu đồ và trả lời bằng văn xuôi hội thoại.

Mã nguồn: https://github.com/TranDuc23021536/mas-data-analysis

## Kiến trúc

Hệ thống gồm 8 agent chuyên biệt, điều phối bằng LangGraph StateGraph:

- Planner Agent: phân loại câu hỏi (xã giao hay cần dữ liệu), viết lại câu hỏi tiếp nối dựa trên lịch sử hội thoại và bảng dữ liệu đang được thảo luận, xác định có cần biểu đồ, dự báo, phát hiện bất thường hay chỉ đổi cách hiển thị dữ liệu đã có (chart_only)
- SQL Agent: sinh và thực thi câu lệnh SQL dựa trên schema thật và ví dụ mẫu (few-shot), chỉ cho phép câu lệnh đọc (SELECT/WITH)
- Analysis Agent: phân tích kết quả truy vấn, rút insight bằng tiếng Việt, tiếp nhận phản hồi từ Critic Agent để viết lại khi bị từ chối
- Visualization Agent: đề xuất loại biểu đồ (bar, line, pie, scatter, table) và cột trục bằng LLM, sau đó kiểm tra lại bằng code (cột có tồn tại, đúng kiểu dữ liệu), nếu không hợp lệ thì dùng quy tắc dự phòng
- Forecast Agent: tự nhận diện cột thời gian trong dữ liệu, sắp xếp lại theo thời gian, dự báo xu hướng bằng hồi quy tuyến tính
- Anomaly Agent: phát hiện điểm bất thường bằng Z-score đối chiếu thêm phương pháp IQR, giới hạn tối đa 20 điểm trả về
- Critic Agent: kiểm duyệt hai lớp. Lớp một dùng code đối chiếu mọi con số trong phần phân tích với dữ liệu SQL gốc (không gọi LLM). Lớp hai dùng LLM đánh giá SQL có đúng ý câu hỏi, insight có suy diễn sai không, biểu đồ có phù hợp không. Nếu bị từ chối, agent chỉ định rõ cần làm lại ở SQL Agent hay Analysis Agent, tối đa hai lần thử lại
- Responder Agent: viết lại insight thành câu trả lời hội thoại tự nhiên bằng LLM, lồng ghép ghi chú về biểu đồ, dự báo, bất thường vào câu văn thay vì liệt kê máy móc

Luồng xử lý: Planner, SQL, Analysis, Visualization, Forecast, Anomaly, Critic, Responder. Câu hỏi xã giao bỏ qua toàn bộ, trả lời trực tiếp. Yêu cầu chỉ đổi cách hiển thị biểu đồ bỏ qua SQL, Analysis, Critic, dùng lại dữ liệu đã truy vấn trước đó trong phiên.

## Công nghệ sử dụng

Python, LangGraph, LangChain, Groq API, PostgreSQL, SQLAlchemy, FAISS, scikit-learn, FastAPI, Streamlit, Pytest, Docker, GitHub Actions.

## Tính năng

- Trả lời câu hỏi phân tích dữ liệu bằng ngôn ngữ tự nhiên, kèm biểu đồ minh họa
- Giữ ngữ cảnh nhiều lượt hội thoại, nhớ bảng dữ liệu đang được thảo luận
- Tải lên file CSV hoặc Excel để phân tích dữ liệu riêng, không giới hạn ở dữ liệu mẫu có sẵn
- Streaming phản hồi theo thời gian thực, hiển thị tiến trình từng agent đang xử lý
- Xác thực bằng API key
- Kiểm duyệt hai lớp trước khi trả lời, tự động làm lại khi phát hiện sai số liệu hoặc sai ý câu hỏi


## Cài đặt và chạy

### Yêu cầu

Python 3.11 trở lên, Docker Desktop, tài khoản Groq (miễn phí tại console.groq.com để lấy API key).

### Bước 1: Clone và cài đặt
git clone https://github.com/TranDuc23021536/mas-data-analysis.git
cd mas-data-analysis
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
### Bước 2: Cấu hình biến môi trường

Copy `.env.example` thành `.env`, điền `GROQ_API_KEY` và `API_KEY` của bạn.

### Bước 3: Chạy bằng Docker

docker compose up -d --build

Backend API tại http://localhost:8000/docs, giao diện tại http://localhost:8501.

### Bước 4: Chạy kiểm thử
pytest tests/ -v


## Bảo mật

SQL Agent chỉ được phép thực thi câu lệnh SELECT hoặc WITH, chặn toàn bộ từ khóa ghi hoặc xóa dữ liệu (INSERT, UPDATE, DELETE, DROP, ALTER, TRUNCATE, CREATE, GRANT, REVOKE). API được bảo vệ bằng API key qua header X-API-Key, cấu hình trong biến môi trường API_KEY.

## Hạn chế đã biết

Lớp một của Critic Agent chỉ phát hiện con số không suy ra được từ dữ liệu, không phát hiện được số đúng nhưng gán sai ý nghĩa. Hệ thống chưa phân biệt triệt để giữa câu hỏi cần dữ liệu mới và câu hỏi chỉ hỏi về cấu trúc dữ liệu trong một số trường hợp hiếm.