# ResolveAI — Deployment Guide

This guide provides step-by-step instructions to deploy ResolveAI to production for live presentation and testing.

---

## Architecture Overview in Production

```
                                  ┌───────────────────────────────┐
                                  │      Vercel / Render Static    │
                                  │  ResolveAI React + Vite UI    │
                                  └───────────────┬───────────────┘
                                                  │ HTTPS (/api)
                                                  ▼
                                  ┌───────────────────────────────┐
                                  │    Render / Railway Web       │
                                  │     FastAPI Backend           │
                                  ├───────────────┬───────────────┤
                                  │   SQLite DB   │   ChromaDB    │
                                  │  (Cases + FTS)│ (Vector Embed)│
                                  └───────────────┴───────────────┘
                                                  │
                                                  ▼
                                      Google Gemini 3.8 Flash
                                         (gemini-flash-latest)
```

---

## Option 1: Render 1-Click Blueprint (Recommended & Easiest)

Render can build and run both the Python FastAPI backend and the React static frontend together from the included `render.yaml`.

### Steps:
1. Push your code to GitHub: `https://github.com/inferno571/resolveai` (already completed).
2. Go to **[Render Dashboard](https://dashboard.render.com/)** and log in with GitHub.
3. Click **"New +"** in the top right → Select **"Blueprint"**.
4. Connect the repository `inferno571/resolveai`.
5. Render will automatically detect `render.yaml` and create 2 services:
   - `resolveai-backend` (Python Web Service)
   - `resolveai-frontend` (Static Web Site)
6. Under `resolveai-backend`, click **Advanced** / **Environment Variables**:
   - Add your `GEMINI_API_KEY`: `your_gemini_api_key_here`
7. Click **"Apply"** / **"Create Blueprint Instance"**.
8. Render will:
   - Install dependencies and build both services.
   - Run `python -m data.seed_loader` to ingest all 55+ seed cases and 179 chunks into ChromaDB.
   - Serve the backend and link it automatically to the frontend.
9. Your live frontend will be available at `https://resolveai-frontend.onrender.com`!

---

## Option 2: Split Cloud (Vercel Frontend + Render/Railway Backend)

If you prefer Vercel for lightning-fast frontend delivery:

### Step 1: Deploy Backend to Render or Railway
1. **On Render / Railway**:
   - Create a new **Web Service** from GitHub repo `inferno571/resolveai`.
   - **Root Directory**: `backend`
   - **Build Command**: `pip install --upgrade pip && pip install -e .`
   - **Start Command**: `python -m data.seed_loader && uvicorn main:app --host 0.0.0.0 --port $PORT`
   - **Environment Variables**:
     - `PYTHON_VERSION`: `3.11.0`
     - `LLM_PROVIDER`: `gemini`
     - `GEMINI_MODEL`: `gemini-flash-latest`
     - `GEMINI_API_KEY`: `<your-key>`
     - `CORS_ORIGINS`: `*`
   - Deploy and copy your backend URL (e.g. `https://resolveai-backend.onrender.com`).

### Step 2: Deploy Frontend to Vercel
1. Go to **[Vercel Dashboard](https://vercel.com/new)**.
2. Import `inferno571/resolveai`.
3. Set:
   - **Framework Preset**: Vite
   - **Root Directory**: `frontend`
4. Add Environment Variable:
   - `VITE_API_URL`: `https://your-backend-url.onrender.com`
5. Click **Deploy**. Vercel will build and host your frontend globally with instant CDN caching.

---

## Option 3: Docker / Self-Hosted VPS

If you have a Linux server (AWS EC2, DigitalOcean, Hetzner, GCP):

1. Clone the repository on your server:
   ```bash
   git clone https://github.com/inferno571/resolveai.git
   cd resolveai
   ```
2. Create `backend/.env`:
   ```bash
   cp backend/.env.example backend/.env
   # Add your GEMINI_API_KEY in backend/.env
   ```
3. Run with Docker Compose:
   ```bash
   docker compose up -d --build
   ```
4. Access the web app at `http://<your-server-ip>:80`!

---

## Production Verification Checklist

Once deployed, verify the installation by testing:
- [ ] Open the frontend URL: Confirm Stack Overflow styling and the **"Gemini 3.8 Flash Online"** indicator in the navbar.
- [ ] Go to **Ask Question**: Submit a query (e.g. *"Kubernetes Pod CrashLoopBackOff OOMKilled"*).
- [ ] Verify that:
  1. The resolution plan is generated with numbered copyable steps.
  2. Related historical cases appear on the right sidebar with similarity scores.
  3. Official documentation citations are linked at the bottom.
- [ ] Test the **Feedback Loop**: Click the green "Yes, this resolved my issue" button and confirm the toast confirmation.
