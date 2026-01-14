# 🚀 Deployment Guide - Masterpost.io

## 📋 Overview

This guide covers deploying the Masterpost.io SaaS application to Hetzner VPS with PM2 for backend and Vercel for frontend.

---

## 🏗️ Architecture

- **Frontend**: Next.js 13+ (App Router) → Vercel
- **Backend**: FastAPI + SQLite → Hetzner VPS (PM2)
- **Database**: SQLite (local file-based)
- **Payment**: Stripe (webhook integration)
- **Auth**: SimpleAuth (email + access code)

---

## 🖥️ Backend Deployment (Hetzner VPS)

### Prerequisites

- Ubuntu 22.04 LTS server
- Python 3.12+
- Nginx (reverse proxy)
- PM2 (process manager)
- Domain pointing to server IP

### 1. Server Setup

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python 3.12
sudo apt install python3.12 python3.12-venv python3-pip -y

# Install Nginx
sudo apt install nginx -y

# Install Node.js (for PM2)
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install -y nodejs

# Install PM2 globally
sudo npm install -g pm2
```

### 2. Clone Repository

```bash
cd /var/www
sudo git clone https://github.com/neuracoder/Masterpost-SaaS.git
sudo chown -R $USER:$USER Masterpost-SaaS
cd Masterpost-SaaS/backend
```

### 3. Setup Python Environment

```bash
# Create virtual environment
python3.12 -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Configure Environment Variables

```bash
# Create .env file
nano .env
```

**Required variables**:
```bash
# API Configuration
PORT=8000
API_V1_STR=/api/v1
CORS_ORIGINS=https://masterpost.io,https://www.masterpost.io

# Alibaba Qwen API
DASHSCOPE_API_KEY=sk-your-key-here

# Stripe Configuration
STRIPE_SECRET_KEY=sk_live_your-key-here
STRIPE_PUBLISHABLE_KEY=pk_live_your-key-here
STRIPE_WEBHOOK_SECRET=whsec_your-webhook-secret

# Stripe Price IDs (Production)
STRIPE_PRICE_STARTER=price_your-starter-id
STRIPE_PRICE_PRO=price_your-pro-id
STRIPE_PRICE_BUSINESS=price_your-business-id

# Supabase (legacy - can be removed if fully migrated)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key
SUPABASE_JWT_SECRET=your-jwt-secret
```

### 5. Initialize Database

```bash
# The database will be created automatically on first run
# To test database initialization:
python3 -c "from app.database_sqlite.sqlite_client import sqlite_client; print('DB initialized at:', sqlite_client.db_path)"
```

### 6. Start Backend with PM2

```bash
# From backend directory
pm2 start ecosystem.config.js

# Save PM2 process list
pm2 save

# Setup PM2 to start on boot
pm2 startup
# Follow the instructions printed by the command above
```

**ecosystem.config.js** (create if doesn't exist):
```javascript
module.exports = {
  apps: [{
    name: 'masterpost-api',
    script: 'venv/bin/uvicorn',
    args: 'app.main:app --host 0.0.0.0 --port 8000 --workers 4',
    cwd: '/var/www/Masterpost-SaaS/backend',
    instances: 1,
    autorestart: true,
    watch: false,
    max_memory_restart: '1G',
    env: {
      NODE_ENV: 'production'
    }
  }]
}
```

### 7. Configure Nginx

```bash
sudo nano /etc/nginx/sites-available/masterpost
```

**Nginx configuration**:
```nginx
server {
    listen 80;
    server_name api.masterpost.io;

    client_max_body_size 100M;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;

        # Timeouts for long-running requests
        proxy_connect_timeout 600s;
        proxy_send_timeout 600s;
        proxy_read_timeout 600s;
    }
}
```

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/masterpost /etc/nginx/sites-enabled/

# Test configuration
sudo nginx -t

# Restart Nginx
sudo systemctl restart nginx
```

### 8. Setup SSL with Certbot

```bash
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d api.masterpost.io
```

### 9. PM2 Monitoring Commands

```bash
# View logs
pm2 logs masterpost-api

# Monitor processes
pm2 monit

# Restart backend
pm2 restart masterpost-api

# Stop backend
pm2 stop masterpost-api

# View status
pm2 status
```

---

## 🌐 Frontend Deployment (Vercel)

### 1. Push to GitHub

```bash
# From project root
git add .
git commit -m "Ready for production deployment"
git push origin main
```

### 2. Deploy to Vercel

1. Go to [vercel.com](https://vercel.com)
2. Click "Import Project"
3. Select your GitHub repository
4. Configure project:
   - **Framework Preset**: Next.js
   - **Root Directory**: `./` (project root)
   - **Build Command**: `npm run build`
   - **Output Directory**: `.next`

### 3. Environment Variables (Vercel Dashboard)

Add these in Vercel project settings:

```
NEXT_PUBLIC_API_URL=https://api.masterpost.io
```

### 4. Custom Domain

1. Go to Vercel project → Settings → Domains
2. Add your domain: `masterpost.io`
3. Follow DNS instructions to point domain to Vercel

---

## 🔧 Stripe Webhook Configuration

### Production Webhook Setup

1. Go to [Stripe Dashboard → Webhooks](https://dashboard.stripe.com/webhooks)
2. Click "Add endpoint"
3. **Endpoint URL**: `https://api.masterpost.io/api/v1/stripe/webhook`
4. **Events to send**: Select `checkout.session.completed`
5. Copy the **Signing secret** (starts with `whsec_`)
6. Update `.env` on server:
   ```bash
   STRIPE_WEBHOOK_SECRET=whsec_your_production_secret
   ```
7. Restart backend: `pm2 restart masterpost-api`

### Test Webhook

```bash
# From local machine
stripe listen --forward-to https://api.masterpost.io/api/v1/stripe/webhook

# Trigger test event
stripe trigger checkout.session.completed
```

---

## 🗄️ Database Management

### Backup SQLite Database

```bash
# Create backup
sqlite3 /var/www/Masterpost-SaaS/backend/masterpost.db ".backup '/var/www/Masterpost-SaaS/backend/backups/masterpost_$(date +%Y%m%d_%H%M%S).db'"

# Or use automated script
#!/bin/bash
DB_PATH="/var/www/Masterpost-SaaS/backend/masterpost.db"
BACKUP_DIR="/var/www/Masterpost-SaaS/backend/backups"
mkdir -p $BACKUP_DIR
sqlite3 $DB_PATH ".backup '$BACKUP_DIR/masterpost_$(date +%Y%m%d_%H%M%S).db'"

# Keep only last 7 days of backups
find $BACKUP_DIR -name "masterpost_*.db" -mtime +7 -delete
```

### Restore Database

```bash
# Stop backend
pm2 stop masterpost-api

# Restore from backup
cp /var/www/Masterpost-SaaS/backend/backups/masterpost_20250101_120000.db /var/www/Masterpost-SaaS/backend/masterpost.db

# Start backend
pm2 start masterpost-api
```

### View Database Content

```bash
# Open SQLite CLI
sqlite3 /var/www/Masterpost-SaaS/backend/masterpost.db

# Useful queries
.tables
SELECT * FROM users LIMIT 10;
SELECT * FROM jobs WHERE status='completed' LIMIT 10;
SELECT * FROM transactions ORDER BY created_at DESC LIMIT 10;
.exit
```

---

## 🔐 Security Checklist

- [ ] All `.env` files excluded from git
- [ ] Stripe keys using **live mode** (sk_live_, pk_live_)
- [ ] CORS configured for production domain only
- [ ] SSL certificates installed (HTTPS)
- [ ] Nginx configured with proper headers
- [ ] Database file permissions set to 600
- [ ] PM2 running as non-root user
- [ ] Firewall configured (UFW):
  ```bash
  sudo ufw allow 22/tcp    # SSH
  sudo ufw allow 80/tcp    # HTTP
  sudo ufw allow 443/tcp   # HTTPS
  sudo ufw enable
  ```

---

## 📊 Monitoring & Logs

### Backend Logs

```bash
# View live logs
pm2 logs masterpost-api

# View error logs only
pm2 logs masterpost-api --err

# Clear logs
pm2 flush
```

### Nginx Logs

```bash
# Access logs
sudo tail -f /var/log/nginx/access.log

# Error logs
sudo tail -f /var/log/nginx/error.log
```

### Database Size Monitoring

```bash
# Check database size
du -h /var/www/Masterpost-SaaS/backend/masterpost.db

# Check uploads folder size
du -sh /var/www/Masterpost-SaaS/backend/uploads
du -sh /var/www/Masterpost-SaaS/backend/processed
```

---

## 🔄 Updates & Maintenance

### Deploy Backend Updates

```bash
cd /var/www/Masterpost-SaaS
git pull origin main
cd backend
source venv/bin/activate
pip install -r requirements.txt
pm2 restart masterpost-api
```

### Deploy Frontend Updates

```bash
# Push to GitHub
git push origin main

# Vercel will auto-deploy
# Or trigger manual deploy from Vercel Dashboard
```

---

## 🧪 Health Checks

### Backend Health Check

```bash
curl https://api.masterpost.io/health
```

**Expected response**:
```json
{
  "status": "healthy",
  "database": "sqlite",
  "version": "2.0.0 (SQLite migration)"
}
```

### Frontend Health Check

Visit: `https://masterpost.io`

---

## 🆘 Troubleshooting

### Backend Not Starting

```bash
# Check PM2 status
pm2 status

# View detailed logs
pm2 logs masterpost-api --lines 100

# Check if port 8000 is in use
sudo lsof -i :8000

# Restart PM2
pm2 restart masterpost-api
```

### Database Locked Error

```bash
# Check who's using the database
fuser /var/www/Masterpost-SaaS/backend/masterpost.db

# Kill process if needed
pm2 restart masterpost-api
```

### Stripe Webhook Failing

```bash
# Check webhook signature in logs
pm2 logs masterpost-api | grep webhook

# Verify webhook secret in .env
cat /var/www/Masterpost-SaaS/backend/.env | grep STRIPE_WEBHOOK_SECRET

# Test webhook manually
stripe listen --forward-to https://api.masterpost.io/api/v1/stripe/webhook
```

### Out of Disk Space

```bash
# Check disk usage
df -h

# Clean old processed images (older than 7 days)
find /var/www/Masterpost-SaaS/backend/processed -type f -mtime +7 -delete

# Clean old uploads (older than 7 days)
find /var/www/Masterpost-SaaS/backend/uploads -type f -mtime +7 -delete
```

---

## 📞 Support

- **GitHub Issues**: https://github.com/neuracoder/Masterpost-SaaS/issues
- **Stripe Dashboard**: https://dashboard.stripe.com
- **Vercel Dashboard**: https://vercel.com/dashboard

---

## ✅ Deployment Checklist

### Pre-Deployment
- [ ] All environment variables configured in `.env`
- [ ] Stripe products and webhooks created
- [ ] Database initialized and tested locally
- [ ] All tests passing
- [ ] `.gitignore` properly configured

### Backend Deployment
- [ ] Server provisioned (Hetzner VPS)
- [ ] Python 3.12+ installed
- [ ] Dependencies installed from `requirements.txt`
- [ ] PM2 configured and running
- [ ] Nginx configured with SSL
- [ ] Database backups scheduled
- [ ] Firewall configured

### Frontend Deployment
- [ ] GitHub repository synced
- [ ] Vercel project created
- [ ] Environment variables set in Vercel
- [ ] Custom domain configured
- [ ] SSL certificate active

### Post-Deployment
- [ ] Health checks passing
- [ ] Stripe webhook tested
- [ ] Test user registration
- [ ] Test image processing (local + premium)
- [ ] Test credit purchase flow
- [ ] Monitor logs for errors
- [ ] Document any issues

---

**Last Updated**: 2025-12-16
**Version**: 2.0.0 (SQLite Migration)
