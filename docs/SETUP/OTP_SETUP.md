# OTP Email & Authentication Setup

## Issue: OTP Not Sending & Frontend Not Redirecting

Your `.env` file has placeholder values. The system is working, but email isn't configured.

---

## Step 1: Configure Gmail for OTP Emails

### 1. Generate Gmail App Password

1. Go to: https://myaccount.google.com/apppasswords
2. **Select app**: `Mail`
3. **Select device**: `Windows Computer` (or your device)
4. Click **Generate**
5. Copy the generated **16-character password**

### 2. Update `.env` File

Replace these lines in your `.env`:

```env
# Email Configuration (Gmail)
EMAIL_ADDRESS=your-email@gmail.com
EMAIL_PASSWORD=your-16-char-app-password
```

**Example:**
```env
EMAIL_ADDRESS=neelsyedabdulrehaman@gmail.com
EMAIL_PASSWORD=abcd efgh ijkl mnop
```

> ⚠️ **Important**: Use the **App Password** (16 chars), NOT your regular Gmail password!

---

## Step 2: Configure Supabase (Required for OTP Storage)

The OTP system stores verification codes in Supabase database.

### 1. Create Supabase Project

1. Go to: https://supabase.com
2. Sign up / Log in
3. Click **New Project**
4. Fill in project details and create

### 2. Create `users` Table

In Supabase dashboard:

1. Go to **SQL Editor** → Click **New Query**
2. Run this SQL:

```sql
CREATE TABLE users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email TEXT UNIQUE NOT NULL,
  otp TEXT,
  otp_expires_at TIMESTAMP,
  created_at TIMESTAMP DEFAULT now()
);
```

3. Click **Run**

### 3. Get Your Credentials

1. Go to **Project Settings** → **API**
2. Copy:
   - **Project URL** → `SUPABASE_URL`
   - **API Key (anon, public)** → `SUPABASE_KEY`

### 4. Update `.env` File

```env
# Supabase Configuration
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key-here
```

---

## Step 3: Restart Server & Test

1. Stop the server (Ctrl+C)
2. Restart with:
   ```powershell
   python -m uvicorn main:app --reload
   ```

3. Test OTP flow:
   - Visit app in browser
   - Enter your email → Click "Send OTP"
   - **You should receive an email within 5 seconds**
   - Enter the 6-digit code → Login

---

## Troubleshooting

### "Email not configured" Error

```
Email not configured - set EMAIL_ADDRESS in .env
```

**Fix**: Make sure `EMAIL_ADDRESS` and `EMAIL_PASSWORD` are NOT placeholder values in `.env`

### "Email authentication failed"

- Verify you used **App Password** (not regular Gmail password)
- Verify Gmail account has 2FA enabled (required for App Passwords)
- Check 16-character password is correct (no extra spaces)

### "User not found" when verifying OTP

- First OTP request should create user in Supabase
- Make sure Supabase credentials are correct in `.env`
- Check if `users` table exists in Supabase

### OTP Email Shows in Logs but Doesn't Arrive

- Check Gmail spam folder
- Verify Gmail SMTP is not blocked
- Try sending from a test account first

---

## Environment File Template

Here's the complete `.env` setup:

```env
# API Keys
COHERE_API_KEY=your_cohere_api_key_here
TAVILY_API_KEY=your_tavily_api_key_here

# Email Configuration (Gmail) - MUST BE CONFIGURED
EMAIL_ADDRESS=your-email@gmail.com
EMAIL_PASSWORD=xxxx xxxx xxxx xxxx

# Supabase Configuration - MUST BE CONFIGURED
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key

# Server Configuration
API_PORT=8000
API_HOST=0.0.0.0
ENVIRONMENT=development

# CORS Configuration
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8081,https://yourdomain.com

# Logging
LOG_LEVEL=INFO
```

---

## What Changed in Code

I improved error handling and logging:

### `send_otp_email()` Function
- ✅ Now returns error message, not just True/False
- ✅ Checks if credentials are configured (detects placeholder values)
- ✅ Logs email errors to app logger
- ✅ Better error messages to frontend

### `request_otp()` Function
- ✅ Passes email error messages to frontend
- ✅ Logs success/failure

### Result
When email fails, user sees actual error (e.g., "Email not configured") instead of generic "Failed to send OTP"

---

## Quick Test Commands

**Test email configuration:**
```powershell
python -c "from utils.auth import send_otp_email; print(send_otp_email('test@gmail.com', '123456'))"
```

**Test Supabase connection:**
```powershell
python -c "from utils.auth import get_supabase; print('Supabase connected!')" 
```

**Check all imports:**
```powershell
python -c "from main import app; from graph.pipeline import run_price_pipeline; print('✅ All imports working!')"
```

---

## Next Steps

1. ✅ Configure `EMAIL_ADDRESS` and `EMAIL_PASSWORD`
2. ✅ Configure `SUPABASE_URL` and `SUPABASE_KEY`
3. ✅ Restart server
4. ✅ Test OTP flow
5. 🎯 Once working, complete React Native frontend UI
