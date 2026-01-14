# 🚀 Masterpost.io - Production Deployment Guide

Complete step-by-step guide to deploy **Masterpost-SaaS** to production (GitHub + Vercel + Supabase).

---

## 📋 Pre-Deployment Checklist

### ✅ Files Created

- [x] `.gitignore` - Excludes `.env`, `uploads/`, `node_modules/`, etc.
- [x] `.env.example` - Template without real values
- [x] `vercel.json` - Vercel deployment configuration
- [x] `README.md` - Professional documentation
- [x] `backend/requirements.txt` - All Python dependencies
- [x] `backend/supabase_setup.sql` - Database schema

### ✅ Current Status

- [x] Landing page complete with slider (6 images)
- [x] User authentication (Supabase Auth)
- [x] Credit system structure ready
- [x] Green/yellow branding implemented
- [x] Split logo design (green/white with yellow M)
- [x] Backend API endpoints created
- [ ] Payment system (Phase 2 - after deployment)

---

## 🎯 Deployment Phases

### **Phase 1:** MVP Deployment (Current)
- Landing page
- Authentication
- Credit system database
- Gallery showcase

### **Phase 2:** Payments (After deployment)
- Stripe integration
- Credit pack purchase
- Webhook handling

### **Phase 3:** Processing (Future)
- Image upload
- Background removal
- Bulk processing

---

## 📦 Step 1: Prepare Local Repository

### 1.1 Verify .env is NOT in git

```bash
# Check that .env is ignored
git status

# .env should NOT appear in the list
# If it does, add to .gitignore:
echo ".env" >> .gitignore
```

### 1.2 Verify example images are included

```bash
# These 6 images MUST be in git for the gallery:
ls backend/img_original/
# Should show: bicicleta.jpg, lampara.jpg, joyeria.jpg, botella.jpg, zapato.jpg, peluche.jpg

ls backend/img_procesada/
# Should show: same 6 files (processed versions)
```

### 1.3 Test locally

```bash
# Start backend
cd backend
uvicorn app.main:app --reload --port 8002

# Open http://localhost:8002/docs
# Verify endpoints are working
```

---

## 🐙 Step 2: Push to GitHub

### 2.1 Initialize git repository

```bash
# Navigate to project root
cd c:\Users\Neuracoder\OneDrive\Desktop\PROYECTOS_HP\SaaS-Proyects\Masterpost-SaaS

# Initialize git
git init

# Check status
git status
```

### 2.2 Verify .env is excluded

```bash
# .env should NOT appear in git status
# Only .env.example should appear
```

### 2.3 Add all files

```bash
git add .
```

### 2.4 First commit

```bash
git commit -m "Initial commit: MVP ready for production deployment

- Landing page with 6-image showcase slider
- Supabase authentication (signup/login)
- Credit system database structure
- Green/yellow branding with split logo
- API endpoints for auth and credits
- Gallery with before/after examples
- Phase 2 (Stripe payments) coming next"
```

### 2.5 Add remote repository

```bash
# Add GitHub remote
git remote add origin https://github.com/neuracoder/Masterpost-SaaS.git

# Rename branch to main
git branch -M main
```

### 2.6 Push to GitHub

```bash
# Push to GitHub
git push -u origin main
```

### 2.7 Verify on GitHub

Visit: https://github.com/neuracoder/Masterpost-SaaS

**Check that these files exist:**
- ✅ README.md
- ✅ .gitignore
- ✅ .env.example
- ✅ vercel.json
- ✅ backend/requirements.txt
- ✅ backend/img_original/ (6 images)
- ✅ backend/img_procesada/ (6 images)

**Check that .env is NOT there!**
- ❌ .env (should NOT exist)

---

## 🗄️ Step 3: Setup Production Supabase

### 3.1 Create new Supabase project

1. Go to: https://supabase.com/dashboard
2. Click **"New project"**
3. Fill in details:
   - **Name:** Masterpost Production
   - **Database Password:** [Generate strong password - SAVE IT!]
   - **Region:** Choose closest to your users
   - **Plan:** Free (upgrade later if needed)
4. Click **"Create new project"**
5. Wait 2-3 minutes for provisioning

### 3.2 Get production credentials

1. Go to **Settings** → **API**
2. Copy these values (you'll need them for Vercel):
   ```
   SUPABASE_URL: https://xxxxxxxxxxxxx.supabase.co
   SUPABASE_ANON_KEY: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
   SUPABASE_SERVICE_ROLE_KEY: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
   ```

### 3.3 Create database tables

1. Go to **SQL Editor** (database icon in sidebar)
2. Click **"New Query"**
3. Open `backend/supabase_setup.sql` from your project
4. Copy ALL content
5. Paste in SQL Editor
6. Click **"Run"** (or Ctrl+Enter)
7. Verify success: "Success. No rows returned"

### 3.4 Verify tables created

1. Go to **Table Editor** (grid icon)
2. Verify these tables exist:
   - ✅ `user_credits`
   - ✅ `transactions`
   - ✅ `stripe_customers`

### 3.5 Verify functions created

Run this query in SQL Editor:

```sql
SELECT routine_name
FROM information_schema.routines
WHERE routine_schema = 'public'
AND routine_name IN ('use_credits', 'add_credits', 'get_user_credits');
```

Should return 3 functions.

---

## ☁️ Step 4: Deploy to Vercel

### 4.1 Create Vercel account

1. Go to: https://vercel.com
2. Sign up with GitHub
3. Authorize Vercel to access your repositories

### 4.2 Import repository

1. Click **"Add New"** → **"Project"**
2. Find **"Masterpost-SaaS"** in the list
3. Click **"Import"**

### 4.3 Configure project

**Framework Preset:** Other
**Root Directory:** `./`
**Build Command:** (leave empty)
**Output Directory:** `./`

### 4.4 Add environment variables

Click **"Environment Variables"** and add these:

```bash
# Supabase (from Step 3.2)
SUPABASE_URL=https://xxxxxxxxxxxxx.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

# Qwen AI
QWEN_API_KEY=your-qwen-api-key-here
QWEN_API_URL=https://dashscope.aliyuncs.com/api/v1/services/aigc/multimodal-generation/generation

# Application URLs (update after deployment)
FRONTEND_URL=https://masterpost-saas.vercel.app
BACKEND_URL=https://masterpost-saas.vercel.app

# Environment
ENVIRONMENT=production
```

### 4.5 Deploy

1. Click **"Deploy"**
2. Wait 2-5 minutes
3. Check deployment logs for errors
4. If successful, you'll get a URL: `https://masterpost-saas-xxxxx.vercel.app`

### 4.6 Test deployment

1. Visit your Vercel URL
2. Check that landing page loads
3. Check API docs: `https://your-url.vercel.app/docs`
4. Test signup/login functionality

---

## 🌐 Step 5: Configure Custom Domain

### 5.1 Add domain in Vercel

1. Go to project **Settings** → **Domains**
2. Add **masterpost.io**
3. Vercel will provide DNS instructions

### 5.2 Update DNS records

In your domain registrar (GoDaddy, Namecheap, etc.):

1. Add **A Record**:
   ```
   Type: A
   Name: @
   Value: 76.76.21.21
   ```

2. Add **CNAME Record**:
   ```
   Type: CNAME
   Name: www
   Value: cname.vercel-dns.com
   ```

3. Wait 5-60 minutes for DNS propagation

### 5.3 Update environment variables

Once custom domain is working, update these in Vercel:

```bash
FRONTEND_URL=https://masterpost.io
BACKEND_URL=https://masterpost.io
```

### 5.4 Redeploy

Click **"Redeploy"** in Vercel dashboard to apply new URLs.

---

## 🔧 Step 6: Configure CORS

### 6.1 Update backend CORS settings

The `backend/app/main.py` should already have CORS configured:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3002",
        "https://masterpost.io",
        "https://*.masterpost.io",
        "https://masterpost-saas.vercel.app"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)
```

If production URL is different, update and redeploy.

---

## ✅ Step 7: Post-Deployment Testing

### 7.1 Test landing page

- [ ] Visit https://masterpost.io
- [ ] Check hero section loads
- [ ] Verify slider shows 6 images
- [ ] Test "Get Started" button
- [ ] Check responsive design (mobile/tablet)

### 7.2 Test authentication

- [ ] Click "Sign Up"
- [ ] Create test account
- [ ] Verify email confirmation (if enabled)
- [ ] Login with test account
- [ ] Check JWT token is returned

### 7.3 Test API endpoints

Visit: https://masterpost.io/docs

Test these endpoints:
- [ ] `POST /api/auth/signup`
- [ ] `POST /api/auth/login`
- [ ] `GET /api/auth/me` (with token)
- [ ] `GET /api/credits/balance` (with token)

### 7.4 Test credit system

1. Signup new user
2. Verify 10 free credits assigned
3. Check balance endpoint returns 10
4. Check transaction history shows "free_pack"

### 7.5 Check database

In Supabase:
- [ ] Open **Table Editor** → **user_credits**
- [ ] Verify test user has 10 credits
- [ ] Check **transactions** table shows signup transaction

---

## 📊 Step 8: Monitoring and Analytics

### 8.1 Vercel Analytics

1. Go to project **Analytics** tab
2. Enable **Web Analytics**
3. Monitor traffic and performance

### 8.2 Supabase Monitoring

1. Go to **Database** → **Logs**
2. Monitor database queries
3. Check for errors

### 8.3 Setup error tracking (optional)

Consider integrating:
- **Sentry** (error tracking)
- **LogRocket** (session replay)
- **Google Analytics** (user analytics)

---

## 🔒 Step 9: Security Checklist

- [x] `.env` not in git
- [x] Service role key in environment variables only
- [x] CORS configured for production domain
- [x] HTTPS enabled (automatic with Vercel)
- [x] Row Level Security (RLS) enabled on Supabase tables
- [x] Input validation on all endpoints
- [ ] Rate limiting (add in future)
- [ ] DDoS protection (Vercel provides basic)

---

## 🚧 Step 10: Next Phase - Stripe Integration

After successful deployment, implement Phase 2:

### Tasks for Phase 2:

1. **Get Stripe account**
   - Sign up at https://stripe.com
   - Get test keys (pk_test_..., sk_test_...)
   - Get production keys later

2. **Add Stripe env variables**
   ```bash
   STRIPE_SECRET_KEY=sk_test_...
   STRIPE_PUBLISHABLE_KEY=pk_test_...
   STRIPE_WEBHOOK_SECRET=whsec_...
   ```

3. **Test payment flow**
   - Create checkout session
   - Use test card: 4242 4242 4242 4242
   - Verify credits added

4. **Configure webhook**
   - Add endpoint in Stripe Dashboard
   - URL: https://masterpost.io/api/payments/webhook
   - Listen for: `checkout.session.completed`

5. **Go live**
   - Replace test keys with live keys
   - Test with real payment
   - Monitor transactions

---

## 🎉 Deployment Complete!

Your Masterpost.io SaaS is now live in production!

### Production URLs:

- **Landing:** https://masterpost.io
- **API Docs:** https://masterpost.io/docs
- **GitHub:** https://github.com/neuracoder/Masterpost-SaaS

### Next Steps:

1. ✅ Share with beta testers
2. ✅ Collect feedback
3. ✅ Implement Phase 2 (Stripe)
4. ✅ Add image processing functionality
5. ✅ Scale as needed

---

## 📞 Support

**Issues?** Check:
- Vercel deployment logs
- Supabase database logs
- Browser console (F12)
- Network tab for API errors

**Need help?**
- Email: info@neuracoder.com
- GitHub Issues: https://github.com/neuracoder/Masterpost-SaaS/issues

---

<div align="center">

**🎉 Congratulations on your deployment!** 🎉

Built with ❤️ by [Neuracoder](https://neuracoder.com)

🟢 🟡 ⚪

</div>
