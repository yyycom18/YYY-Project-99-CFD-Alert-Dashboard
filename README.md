# YYY-Project-99-CFD-Alert-Dashboard

**This is the only folder you need for Project99.**  
Push this repo to GitHub. All app code lives inside the `Project99/` folder here.

CFD trading alert dashboard (Phase 1 scoring engine + Phase 2 Streamlit visualization).  
Real 15m data via yfinance (XAUUSD, EURUSD, AUDUSD, HK50).

---

## One folder, no confusion

| Folder | Use it? |
|--------|--------|
| **YYY-Project-99-CFD-Alert-Dashboard** (this repo) | ✅ **Yes** — work here and push to GitHub |
| Standalone **Project99** (sibling folder in workspace) | ❌ No — duplicate; you can delete it after confirming this repo runs |

---

## Clone (if on another machine)

```bash
git clone https://github.com/yyycom18/YYY-Project-99-CFD-Alert-Dashboard.git
cd YYY-Project-99-CFD-Alert-Dashboard
```

## Setup

```bash
pip install -r Project99/requirements.txt
```

## Run locally

From the **repo root** (YYY-Project-99-CFD-Alert-Dashboard):

```bash
streamlit run Project99/app_streamlit.py --server.port 8501
```

Then open: **http://localhost:8501**

## Push to GitHub (GitHub Desktop)

1. **File → Add Local Repository** → choose **YYY-Project-99-CFD-Alert-Dashboard**
2. Commit message → **Commit to main**
3. **Push origin**

Repo: https://github.com/yyycom18/YYY-Project-99-CFD-Alert-Dashboard
