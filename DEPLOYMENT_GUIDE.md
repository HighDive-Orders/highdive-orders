# HIGH DIVE ORDER SYSTEM — DEPLOYMENT GUIDE
## From Google Drive → GitHub → Streamlit Cloud (Free)

---

## STEP 1: SAVE FILES TO GOOGLE DRIVE (NOW)

Download all files from this chat and save them to a Google Drive folder.

**Create this folder structure in Google Drive:**
```
High Dive Order System/
├── streamlit_app.py          ← Main web app
├── vendor_schedules.json     ← GFS, WCW, Evans, Last Call schedules
├── recipes_imported.json     ← 29 recipes from plate cost file
├── vendor_mapping_smart.json ← Ingredient → vendor assignments
├── requirements.txt          ← Python dependencies
└── DEPLOYMENT_GUIDE.md       ← This file
```

**Files to download from this chat:**
1. streamlit_app.py
2. vendor_schedules.json
3. recipes_imported.json
4. vendor_mapping_smart.json
5. requirements.txt
6. This guide

**Why Google Drive first:**
- Safe backup of all files
- Easy to share with collaborators
- Access from anywhere
- Free and permanent storage

---

## STEP 2: CREATE FREE GITHUB ACCOUNT

GitHub stores your code and connects to Streamlit Cloud.

1. Go to: **https://github.com**
2. Click "Sign up" (top right)
3. Enter:
   - Username: `highdive-orders` (or your preference)
   - Email address
   - Password
4. Verify your email
5. Choose the **Free plan**

**Cost: $0**

---

## STEP 3: CREATE GITHUB REPOSITORY

1. Log into GitHub
2. Click the **"+"** icon (top right) → "New repository"
3. Fill in:
   - Repository name: `highdive-orders`
   - Description: `High Dive Restaurant Order Management System`
   - Visibility: **Private** (keeps your data secure)
   - Check "Add a README file"
4. Click **"Create repository"**

---

## STEP 4: UPLOAD YOUR FILES TO GITHUB

1. In your new repository, click **"Add file"** → **"Upload files"**
2. Drag and drop all 5 files from your Google Drive folder:
   - streamlit_app.py
   - vendor_schedules.json
   - recipes_imported.json
   - vendor_mapping_smart.json
   - requirements.txt
3. Scroll down, add commit message: `Initial deployment`
4. Click **"Commit changes"**

Your repository should now show all 5 files.

---

## STEP 5: CREATE FREE STREAMLIT CLOUD ACCOUNT

1. Go to: **https://streamlit.io/cloud**
2. Click **"Sign up"**
3. Choose **"Continue with GitHub"** (easiest — links accounts automatically)
4. Authorize Streamlit to access your GitHub
5. You're in — choose the **Free tier**

**Cost: $0**

---

## STEP 6: DEPLOY YOUR APP

1. In Streamlit Cloud, click **"New app"**
2. Fill in:
   - **Repository:** `your-username/highdive-orders`
   - **Branch:** `main`
   - **Main file path:** `streamlit_app.py`
3. Click **"Deploy!"**
4. Wait 2-3 minutes for deployment
5. Your app is live at:
   **`https://highdive-orders.streamlit.app`**

That's it! The app is now live on the internet, free, 24/7.

---

## STEP 7: TEST YOUR APP

1. Open `https://highdive-orders.streamlit.app`
2. You should see the High Dive Order Management System
3. Test the workflow:
   - Go to Sales Dashboard
   - Upload your Toast ProductMix file
   - See sales projections appear
   - Go to Generate Orders
   - Select GFS → Order Sunday → Calculate
   - Download the Excel file
4. If anything looks wrong, let me know and I'll fix it

---

## STEP 8: SHARE WITH YOUR MANAGER

Send your manager this information:
```
Hi [Manager Name],

Here's the link to our new ordering system:
https://highdive-orders.streamlit.app

Weekly workflow:
1. Export Toast data (Reports → Product Mix → Last 7 days → Excel)
2. Open the app and upload the file
3. Review sales projections, adjust for events if needed
4. Generate each vendor's order
5. Download PDFs and place orders

Takes about 10 minutes vs 2+ hours manually!

Let me know if you have questions.
```

---

## STEP 9: ADD TOAST API (WHEN READY)

When you have your Toast API credentials, add them securely:

1. In Streamlit Cloud, go to your app settings
2. Click **"Secrets"**
3. Add:
```toml
[toast]
client_id = "your_client_id_here"
client_secret = "your_client_secret_here"
restaurant_guid = "your_restaurant_guid_here"
```
4. Save — the app will automatically use these credentials
5. Daily data fetching will be enabled — no more manual uploads!

**IMPORTANT:** Never put credentials directly in code files. Always use Streamlit Secrets.

---

## UPDATING THE APP IN THE FUTURE

When you need to make changes (new vendor, recipe update, etc.):

**Option A: Direct Edit on GitHub (Easy)**
1. Go to your GitHub repository
2. Click the file you want to edit
3. Click the pencil icon (Edit)
4. Make your changes
5. Click "Commit changes"
6. Streamlit automatically redeploys in ~1 minute

**Option B: Upload New File (Easiest)**
1. Make changes to file on your computer
2. Go to GitHub → "Add file" → "Upload files"
3. Upload the updated file (replaces the old one)
4. Commit changes
5. Streamlit auto-redeploys

---

## TROUBLESHOOTING

**App shows error on startup:**
- Check that all 5 files are uploaded to GitHub
- Verify requirements.txt is present
- Check Streamlit Cloud logs (click "Manage app" → "Logs")

**"Module not found" error:**
- Check requirements.txt has all packages listed
- Re-deploy from Streamlit Cloud dashboard

**Data not loading:**
- Verify recipes_imported.json and vendor_mapping_smart.json are in the repository
- Check file names match exactly (case-sensitive)

**App is slow:**
- Normal on first load (cold start can take 30 seconds)
- Subsequent loads are fast

**App shows "sleeping":**
- Free tier apps sleep after inactivity
- Click "Wake up" or just wait 30-60 seconds
- Use the app weekly to prevent sleeping

---

## FILE REFERENCE

| File | Purpose | Update When |
|------|---------|-------------|
| streamlit_app.py | Main application | New features needed |
| vendor_schedules.json | Delivery schedules | Vendor schedule changes |
| recipes_imported.json | Menu recipes | Menu changes |
| vendor_mapping_smart.json | Ingredient → vendor | New ingredients added |
| requirements.txt | Python packages | Never (unless told to) |

---

## COST SUMMARY

| Item | Cost |
|------|------|
| GitHub (Private repo) | $0/month |
| Streamlit Cloud (Free tier) | $0/month |
| Google Drive (backup) | $0/month |
| Toast API | $0 (included with Toast) |
| **TOTAL** | **$0/month** |

---

## CONTACTS

**Streamlit Support:** https://discuss.streamlit.io (free community forum)
**GitHub Support:** https://support.github.com (free)
**Toast API Support:** apisupport@toasttab.com or 1-617-273-0305

---

*Last Updated: February 2026*
*High Dive Order Management System v1.0*
