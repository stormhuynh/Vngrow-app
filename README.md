# VNGROW Logistics Platform

App thật cho VNGROW Logistics. Giai đoạn 1: **Module Shipment (Client Portal)**.
Roadmap & checklist: xem [`plan.md`](./plan.md).

## Stack
- Backend: Django 5 + DRF + SimpleJWT (PostgreSQL, fallback SQLite cho dev)
- Frontend: Vue 3 + TypeScript + Vite + Pinia + Vue Router

## Chạy backend (cổng 8000)
```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe manage.py migrate
.\.venv\Scripts\python.exe manage.py seed
.\.venv\Scripts\python.exe manage.py runserver 8000
```

Dùng Postgres: copy `.env.example` -> `.env` và set `DATABASE_URL`.

## Chạy frontend (cổng 5173)
```powershell
cd frontend
npm install
npm run dev
```
> Trên máy này npm bị chặn qua PowerShell, dùng `npm.cmd install` / `npm.cmd run dev`.

## Tài khoản demo
- Khách: `khachhang@minhlong.vn` / `demo1234`
- Admin (Django admin `/admin/`): `admin@vngrow.vn` / `admin1234`

## API chính
- `POST /api/auth/login/`, `POST /api/auth/refresh/`, `GET /api/auth/me/`
- `GET /api/shipments/` (filter: `direction`, `mode`, `op_status`, `ordering=eta|etd`)
- `GET /api/shipments/{id}/`
- `POST /api/shipments/{id}/documents/` (multipart: `doc_type`, `file`)

## Deploy (GitHub + Vercel + Render)
Stack chốt: **frontend Vercel, backend Django trên Render, PostgreSQL managed**.

### Backend — Render
- Render đọc `render.yaml` (blueprint) ở thư mục gốc: tạo web service `vngrow-api` + Postgres `vngrow-db`.
- Build: `backend/build.sh` (`pip install` → `collectstatic` → `migrate`).
- Start: `gunicorn config.wsgi:application`.
- Env cần set thủ công sau khi có domain frontend:
  - `CORS_ALLOWED_ORIGINS=https://<frontend>.vercel.app`
  - `CSRF_TRUSTED_ORIGINS=https://<frontend>.vercel.app`
- `SECRET_KEY` auto-generate, `DEBUG=False`, `DATABASE_URL` lấy từ Postgres tự động.
- Tạo admin/user thật: dùng Render Shell chạy `python manage.py createsuperuser` (và `python manage.py seed` nếu cần dữ liệu mẫu).

### Frontend — Vercel
- Root Directory: `frontend`, framework **Vite** (đã có `frontend/vercel.json`).
- Build `npm run build`, output `dist`.
- Env: `VITE_API_BASE=https://<backend>.onrender.com` (không có dấu `/` cuối).

### Database
- Production dùng PostgreSQL (Render/Supabase/Neon). Local để trống `DATABASE_URL` sẽ fallback SQLite.
