# Deploying to Render

This guide walks you through deploying the QA Agent to Render.

## Prerequisites

1. A [Render](https://render.com) account (free tier works)
2. Your Gemini API key
3. Git repository with this code

## Deployment Steps

### 1. Push to Git

Ensure your code is in a Git repository (GitHub, GitLab, or Bitbucket):

```bash
git add .
git commit -m "Prepare for Render deployment"
git push origin main
```

### 2. Connect to Render

1. Go to [Render Dashboard](https://dashboard.render.com/)
2. Click **"New +"** → **"Blueprint"**
3. Connect your Git repository
4. Render will automatically detect `render.yaml`

### 3. Configure Environment Variables

Before deploying, set the following in the Render dashboard:

#### For `qa-agent-backend`:
- **`GEMINI_API_KEY`**: Your Google Gemini API key

The `BACKEND_URL` for the frontend will be automatically set by Render.

### 4. Deploy

1. Click **"Apply"** to start the deployment
2. Wait for both services to build and deploy (5-10 minutes)
3. Once deployed, you'll get two URLs:
   - **Backend**: `https://qa-agent-backend.onrender.com`
   - **Frontend**: `https://qa-agent-frontend.onrender.com`

### 5. Access Your App

Visit the **frontend URL** to use your QA Agent!

## Important Notes

### Free Tier Limitations

- **Cold Starts**: Services spin down after 15 minutes of inactivity. First request after inactivity will be slow (~30 seconds).
- **Data Loss**: ChromaDB data is stored in ephemeral storage and will be lost on restarts. Users need to re-upload documents after each restart.
- **Compute**: Limited CPU and memory.

### Upgrading for Persistence

To keep your ChromaDB data between restarts:

1. Upgrade backend to a paid plan ($7/month minimum)
2. Add a persistent disk in Render dashboard:
   - Go to backend service → **"Disks"**
   - Add disk mounted at `/opt/render/project/src/chroma_db`
   - Size: 1GB minimum

## Troubleshooting

### Services Won't Start

- Check build logs in Render dashboard
- Verify `GEMINI_API_KEY` is set correctly
- Ensure `requirements.txt` includes all dependencies

### Frontend Can't Connect to Backend

- Verify `BACKEND_URL` environment variable is set
- Check backend service is running
- Look for CORS errors in browser console

### ChromaDB Errors

- Ensure `chroma_db` directory exists (it's created automatically)
- If using persistent disk, verify mount path is correct

## Local Testing

Test the deployment configuration locally:

```bash
# Terminal 1 - Backend
export PORT=8000
export GEMINI_API_KEY="your-key-here"
uvicorn src.backend:app --host 0.0.0.0 --port $PORT

# Terminal 2 - Frontend
export BACKEND_URL="http://localhost:8000"
export PORT=8501
streamlit run src/app.py --server.port $PORT --server.address 0.0.0.0
```

## Monitoring

- View logs in Render dashboard under each service
- Monitor service health and uptime
- Check for API rate limits on Gemini

## Cost Estimate

- **Free Tier**: $0/month (with limitations above)
- **With Persistence**: ~$8/month (paid plan + 1GB disk)
