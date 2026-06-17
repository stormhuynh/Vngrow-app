# VNGROW Logistics Platform — Plan triển khai

> Tài liệu **sống (living checklist)**. Quy ước: `- [ ]` = chưa làm, `- [~]` = đang làm, `- [x]` = đã xong.
> Mỗi khi hoàn thành một hạng mục, đánh dấu `[x]` và ghi ngày + commit/PR nếu có.
> **Trọng tâm hiện tại: Module Shipment (Client Portal) để dùng sớm**, nhưng phải dựng trên lõi chuẩn để mở rộng lâu dài.

- **Cập nhật lần cuối:** 17/06/2026 (chốt stack + chuẩn hóa deploy GitHub/Vercel/Render/PostgreSQL)
- **Stack:** Django + DRF + PostgreSQL (backend), Vue 3 + TS + Vite + Pinia + Vue Router (frontend), JWT auth.
- **Localization:** Tiếng Việt, timezone Asia/Ho_Chi_Minh, ngày dd/MM/yyyy, VND không thập phân, USD 2 số.

---

## 0. Nguyên tắc lõi (làm đúng từ đầu để không phải đập đi xây lại)

- [x] Tách biệt **backend API** và **frontend SPA** (deploy độc lập).
- [x] **Custom User model** + `Customer` (multi-tenant theo công ty khách) ngay từ đầu.
- [x] Chuẩn hoá **trạng thái chứng từ 2 lớp** (processing + business) dùng chung toàn hệ thống.
- [x] **Audit log** append-only cho shipment (mở rộng cho module khác sau).
- [ ] **Multi-company** (`company_id`, VNGROW = S01) — chuẩn bị field, chưa bật UI.
- [x] **Feature flags / ẩn menu** cho module chưa làm (RFQ, Pricing, Documents, AI) — sidebar hiển thị "Sắp ra mắt".
- [ ] **RBAC** chuẩn: Manager / Operation / Sales / Accounting / Customer (mới có khung role, chưa enforce chi tiết).
- [ ] Quy ước **mã code** (shipment, RFQ, quotation...) tập trung, cấu hình được.
- [ ] **Tài liệu API** (drf-spectacular / OpenAPI) + Postman collection.
- [ ] **CI cơ bản** (lint + test) + môi trường staging.

---

## 1. Foundation — Lõi nền tảng (ưu tiên cao nhất, làm song song Shipment)

### 1.1 Platform & Auth
- [x] Django project `config` + apps `accounts`, `shipments`.
- [x] Settings: DRF, CORS, JWT (SimpleJWT), DB qua `DATABASE_URL` (SQLite dev / Postgres prod).
- [x] Custom `User` (email login) + `Customer` + role choices.
- [x] API: `login`, `refresh`, `me`.
- [ ] Forgot / reset password (email).
- [~] Refresh-token rotation + logout/blacklist (đã có refresh + logout client; chưa blacklist server).
- [ ] Phân quyền theo role ở mức object (queryset filtering nâng cao).

### 1.2 Master data (tối thiểu cho Shipment trước, mở rộng sau)
- [ ] Cảng / sân bay (seed cứng tạm trong Shipment, sẽ tách bảng riêng).
- [ ] Hãng tàu / hãng bay (carrier).
- [ ] Loại hình vận chuyển (FCL/LCL/AIR/EXPRESS) — hiện là enum.
- [ ] Đơn vị, loại chứng từ, incoterm... (config tập trung).

### 1.3 Audit & Settings
- [x] AuditLog model + ghi log khi khách upload chứng từ.
- [ ] Audit log toàn cục (mọi thao tác quan trọng), trang xem log nội bộ.
- [ ] Bảng cấu hình hệ thống (tỉ giá, VAT, rounding) — phục vụ Pricing sau.

---

## 2. MODULE SHIPMENT (Client Portal) — TRỌNG TÂM, LÀM TRƯỚC

### 2.1 Backend
- [x] Models: `Shipment`, `ShipmentTask`, `ShipmentDocument`, `Payment`, `AuditLog`.
- [x] Serializers: list + detail (lồng tasks/documents/payment/audit).
- [x] ViewSet: list + filter (direction, mode, op_status, ordering eta/etd) + detail.
- [x] Endpoint upload chứng từ (tự tăng version + ghi audit log).
- [x] Django Admin cho toàn bộ model shipment.
- [x] Lệnh seed dữ liệu mẫu + user demo + superuser.
- [x] Migrations đã chạy & kiểm tra trên máy (`makemigrations` + `migrate` + `seed`).
- [ ] Filter nâng cao: khoảng thời gian (7/30 ngày trước–sau), search theo code.
- [ ] Phân trang + sắp xếp khớp UI list.
- [x] Quyền: khách chỉ thấy shipment của công ty mình (đã filter + test qua API).
- [ ] B/L business status flow (Draft → Confirmed → Released) qua API nội bộ.

### 2.2 Frontend
- [x] Scaffold Vue 3 + TS + Vite (package.json, tsconfig, vite.config, env).
- [x] App shell: router, Pinia, api client (axios + interceptor JWT + auto refresh), auth store.
- [x] Trang Login + route guard.
- [x] Layout Client Portal (sidebar menu cố định, account box, đăng xuất).
- [x] Shipment **list**: filter 3 lớp (Export/Import; mode; sắp xếp ETA/ETD).
- [x] Shipment **detail**: 2 box info, bảng Tiến độ công việc, Hồ sơ & chứng từ (download/upload), box Thanh toán, Lịch sử ghi nhận thay đổi.
- [x] Upload modal chọn loại chứng từ + gọi API + cập nhật audit log.
- [x] Responsive desktop/tablet (split view) + mobile (list-first).
- [x] Badge trạng thái 2 lớp (processing + business) cho chứng từ.
- [ ] Filter khoảng thời gian (7/30 ngày) + search theo code trên UI.

### 2.3 Hoàn thiện & phát hành sớm
- [x] Ẩn menu RFQ / Pricing / Documents (SI-VGM) / AI Assistant (trạng thái "Sắp ra mắt").
- [x] Chạy thử end-to-end: đăng nhập → list → detail → upload.
- [ ] Deploy staging (backend + frontend) cho khách dùng thử.
- [ ] Thu thập phản hồi & sửa nhanh vòng 1.

---

## 3. Các module tiếp theo (theo thứ tự ưu tiên sau Shipment)

> Thứ tự bám sát MVP priority trong PRD, nhưng Shipment được kéo lên làm trước để dùng sớm.

### 3.1 Document module độc lập (SI / VGM)
- [ ] Form SI trong portal + tải template Excel + upload offline.
- [ ] Form VGM + cut-off theo shipment (khoá sau cut-off).
- [ ] Liên kết SI/VGM với shipment.

### 3.2 CRM & Master data đầy đủ
- [ ] Quản lý khách hàng, người liên hệ, hợp đồng.
- [ ] Master data: cảng, carrier, tuyến, local charges, surcharge.

### 3.3 Pricing engine (MVP)
- [ ] 5 cấp giá: Vendor cost / Base cost / Public price / Sales quote / Contract price.
- [ ] Ưu tiên giá: contract → sales quote → discounted public → public.
- [ ] Guardrail xanh/vàng/đỏ + duyệt khi dưới base.
- [ ] Import rate card Excel/CSV.
- [ ] Public check price + bảng giá quốc tế (đã có wireframe).

### 3.4 Local charges / Surcharge / VAT / Currency
- [ ] Quản lý phụ phí, VAT, tỉ giá, rounding, đa tiền tệ.

### 3.5 Quotation / Báo giá
- [ ] Tạo báo giá, revision nội bộ, link chia sẻ 30 ngày, xuất PDF, snapshot.

### 3.6 Internal Shipment & Tracking (nội bộ)
- [x] Operation tạo/quản lý shipment bước đầu qua Django Admin (nhập shipment, task, chứng từ, payment).
- [ ] Checklist template, cảnh báo trễ.
- [ ] Đồng bộ dữ liệu nội bộ ↔ client portal.

### 3.7 Reporting / Commission / Notification
- [ ] Dashboard theo role (Sales/Operation/Manager/Accounting).
- [ ] Hoa hồng (ước tính khi tạo, chốt khi hoàn thành, đóng sổ ngày 02).
- [ ] Thông báo Zalo / in-app / email.

### 3.8 AI Assistant
- [ ] Trợ lý hỏi đáp shipment / chứng từ / tra cứu.

---

## 4. Hạ tầng & vận hành (làm dần)
- [ ] Lưu trữ tài liệu: hiện local FileField → chuyển Google Drive / S3 sau.
- [ ] Backup DB định kỳ.
- [ ] Logging / monitoring.
- [ ] Tài liệu hướng dẫn nội bộ + training.

---

## Nhật ký tiến độ
- **14/06/2026 (sáng)** — Khởi tạo backend (Django + DRF + JWT), models & API Shipment, seed data, Django Admin; scaffold frontend Vue 3 + TS.
- **14/06/2026 (chiều)** — Hoàn thiện frontend Shipment (login, layout sidebar, list + filter, detail, upload chứng từ, audit log). Cài deps backend + frontend, chạy migrate + seed. Backend `:8000`, frontend `:5173` chạy OK; verify end-to-end login → list (3 shipment) → detail → upload. Tick các mục tương ứng trong plan.
- **15/06/2026** — Tinh chỉnh Shipment detail theo phản hồi: bảng Tiến độ công việc hiển thị tối đa 6 dòng rồi scroll; Hồ sơ & chứng từ bỏ trạng thái nghiệp vụ, ẩn phiên bản và chỉ hiện chứng từ upload cuối cùng theo từng loại; Lịch sử ghi nhận thay đổi hiển thị tối đa 3 dòng rồi scroll; audit actor khi khách upload dùng email khách hàng, không thêm ghi chú "(khách)".
- **15/06/2026** — Hoàn thiện nhập liệu nội bộ Shipment bước đầu bằng Django Admin: bỏ `op_status` khỏi form/filter admin để Operation không nhập tay; hệ thống tự đồng bộ `op_status` từ công việc có trạng thái Hoàn thành/Đang xử lí gần ngày hiện tại nhất; kiểm tra `manage.py check` OK và không phát sinh migration.
- **15/06/2026** — Sửa thẻ Shipment bên trái trong Client Portal: API list/detail trả thêm `current_task_name`, `current_task_status`, `current_task_status_display`; frontend ưu tiên hiển thị tên công việc hiện tại thay vì `op_status_display`, ví dụ `Tiếp nhận lô hàng - Đang xử lí` sẽ hiển thị `Tiếp nhận lô hàng` trên card.
- **15/06/2026** — Áp dụng màu thương hiệu VNGrow cho dashboard Client Portal: gradient xanh làm màu primary/action/highlight, gradient cam làm accent; thêm trường `actual_date` cho `ShipmentTask`, migration `shipments.0002`, bảng Tiến độ công việc tách `Dự kiến` màu xanh dương và `Thực tế` màu xanh lá.
- **15/06/2026** — Gộp hai cột `Dự kiến` và `Thực tế` trong bảng Tiến độ công việc thành một cột `Lịch trình`; nếu có `actual_date` thì hiển thị ngày thực tế màu xanh lá và ghi đè ngày dự kiến, nếu chưa có thì hiển thị ngày dự kiến màu xanh dương.
- **15/06/2026** — Audit project trước go-live Shipment: thêm `.gitignore`, tạo `backend/.env` dev với `SECRET_KEY` đủ dài, sửa cấu hình TypeScript để `npm.cmd run build` chạy chính thức, xóa cache `__pycache__` và build artifacts tạm, xác nhận backend `manage.py check` OK, migrations đã apply, DB có dữ liệu demo, API login/me/shipments hoạt động.
- **17/06/2026** — Chốt stack triển khai dài hạn, tối ưu chi phí, ít phụ thuộc dev: **frontend Vercel + backend Django/Render + PostgreSQL managed**. Thêm `gunicorn`, `whitenoise` vào requirements; bật static production (`STATIC_ROOT`, `CompressedManifestStaticFilesStorage`) + WhiteNoise middleware; thêm security hardening tự bật khi `DEBUG=False` (SSL redirect, HSTS, secure cookies, proxy SSL header) và `CSRF_TRUSTED_ORIGINS`, tự nhận `RENDER_EXTERNAL_HOSTNAME`. Thêm blueprint `render.yaml` (web service + Postgres), `backend/build.sh`, `frontend/vercel.json` (SPA rewrite), `frontend/.env.example`, cập nhật `.env.example` và README phần Deploy. Verify `collectstatic` (162 files) và `manage.py check` OK.
