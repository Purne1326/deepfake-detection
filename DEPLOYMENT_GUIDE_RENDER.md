# 🚀 Deployment Guide: Render.com

I have prepared your repository for a **hassle-free, one-click deployment** to Render. This uses a **Blueprint** (`render.yaml`) that automatically sets up:
1.  **Deepfake Dashboard** (Web Service)
2.  **Dummy Social Platform** (Web Service)
3.  **Public Reporting System** (Web Service)
4.  **Detection Orchestrator** (Background Worker)
5.  **PostgreSQL Database** (Shared Persistence)

---

## 📋 Prerequisites
1.  **GitHub Account**: Your code must be pushed to a repository on GitHub.
2.  **Render Account**: Sign up at [dashboard.render.com](https://dashboard.render.com).

---

## 🛠️ Deployment Steps

### 1. Push to GitHub
Ensure you have committed and pushed the latest changes (including `render.yaml` and `requirements.txt`) to your GitHub repository.

```bash
git add .
git commit -m "Configure Render Deployment Blueprint"
git push origin main
```

### 2. Create a "Blueprint" on Render
1.  Go to the [Render Dashboard](https://dashboard.render.com).
2.  Click the **"New +"** button and select **"Blueprint"**.
3.  Connect your GitHub account (if not already connected).
4.  Select your **Deepfake Detection System** repository.
5.  Render will automatically detect the `render.yaml` file. Give your group a name (e.g., `deepfake-detection-group`).
6.  Click **Apply**.

### 3. Verification
Render will start spinning up all 4 services and the PostgreSQL database.
-   **Database**: Will be ready first.
-   **Web Services**: Might take 2–5 minutes to install dependencies and start.
-   Once finished, you will see URLs for:
    -   `deepfake-dashboard.onrender.com`
    -   `dummy-social-platform.onrender.com`
    -   `public-reporting-system.onrender.com`

---

## 💡 Important Considerations

### 1. Gunicorn Port Handling
Render automatically assigns a port through the `$PORT` environment variable. I have updated the `render.yaml` to use Gunicorn which respects this natively.

### 2. Free Tier Limitations
-   **Spin-down**: Free web services spin down after 15 minutes of inactivity. The first request after spin-down might take ~30 seconds to wake up.
-   **Database**: Render's Free PostgreSQL instance expires after 90 days. For production, consider a paid tier.

### 3. Static Files & Binary Data
The `forensic-scan` uploads files to local storage. On Render's web services, this storage is **ephemeral** (deleted on redeploy). 
> [!TIP]
> For permanent storage of uploaded forensic scans, you would normally connect an **AWS S3 bucket** or **Google Cloud Storage**. For this demo, local storage is fine but resets on each deploy.
