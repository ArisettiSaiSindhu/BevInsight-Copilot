# Live Deployment Steps - BevInsight AI Copilot v2

This document details the production deployment process for hosting the **BevInsight AI Copilot v2** platform live:
* **Backend:** FastAPI hosted on **Render**
* **Frontend:** React hosted on **Netlify**

---

## 1. Prepare the Codebase for Git
Both Render and Netlify deploy directly from your GitHub repository.

1. **Initialize Git Repository:**
   In your workspace root folder, run:
   ```bash
   git init
   git add .
   git commit -m "Initial commit - BevInsight Copilot v2"
   ```
2. **Push to GitHub:**
   Create a new private or public repository on GitHub and link it:
   ```bash
   git remote add origin https://github.com/YOUR_USERNAME/bevinsight-copilot.git
   git branch -M main
   git push -u origin main
   ```

---

## 2. Deploy the FastAPI Backend to Render

Render will host the FastAPI server and the SQLite database.

1. **Log in to Render:** Go to [render.com](https://render.com) and sign in (GitHub authorization recommended).
2. **Create a New Web Service:**
   - Click **New +** and select **Web Service**.
   - Connect your GitHub repository.
3. **Configure Web Service Settings:**
   - **Name:** `bevinsight-backend`
   - **Region:** Choose the region closest to you.
   - **Runtime:** `Python`
   - **Branch:** `main`
   - **Build Command:**
     ```bash
     pip install -r requirements.txt && python -m app.generator
     ```
     *(Note: This builds the python requirements and automatically generates the pre-seeded SQLite transaction database upon deployment)*
   - **Start Command:**
     ```bash
     uvicorn app.main:app --host 0.0.0.0 --port $PORT
     ```
   - **Instance Type:** Select **Free** (or Starter).
4. **Configure Environment Variables:**
   - Click on the **Advanced** button.
   - Add the following variables:
     - `GEMINI_API_KEY` = `[Your Active Gemini API Key]`
     - `DB_PATH` = `bevinsight.db`
5. **Deploy:** Click **Create Web Service**.
6. **Save URL:** Once deployed, copy your service's live URL (e.g. `https://bevinsight-backend.onrender.com`).

---

## 3. Deploy the React Frontend to Netlify

Netlify will host the frontend React app and proxy requests to Render to bypass CORS.

### Step A: Configure API Proxy Redirect
To prevent CORS errors and allow relative `/api/...` fetch calls to route to your Render backend, create a redirect rule:

1. Create a file named `_redirects` inside `static/` (for the static SPA) and `frontend/public/` (for Vite compiles):
   ```
   /api/*  https://YOUR-BACKEND-RENDER-URL/api/:splat  200
   ```
   *Example:*
   ```
   /api/*  https://bevinsight-backend.onrender.com/api/:splat  200
   ```
   *(This tells Netlify to intercept `/api` requests and proxy them securely to your Render domain).*

### Step B: Build & Deploy on Netlify

1. **Log in to Netlify:** Go to [netlify.com](https://www.netlify.com) and log in.
2. **Add a New Site:**
   - Click **Add new site** -> **Import from Git**.
   - Connect to your GitHub account and select your repository.
3. **Configure Build Settings:**
   - **Base directory:** `frontend`
   - **Build command:** `npm run build`
   - **Publish directory:** `frontend/dist`
4. **Deploy:** Click **Deploy site**.
5. **Custom Domain:** Once built, Netlify will publish a live URL (e.g., `https://bevinsight-copilot.netlify.app`).

---

## 4. Alternative Single-Command Deployment (Fastest Demo)
If you wish to demo the entire self-contained application from a single host (FastAPI serving the single-file React SPA):

1. Follow the **Render** steps above.
2. Under Render Advanced settings, make sure the build command is:
   ```bash
   pip install -r requirements.txt && python -m app.generator
   ```
3. Uvicorn will start and automatically host the React SPA at the root Render URL `https://bevinsight-backend.onrender.com/`. 
4. You can navigate directly to the Render URL in your mobile or desktop browser to run the full dashboard without deploying to Netlify!
