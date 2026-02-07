# Copy Sitemaps to JavaScript Project - Complete Guide

## Quick Overview
Your Django app generates sitemaps in `storefront/static/sitemaps/`. Google cannot fetch them from `nexassearch.com` (goes to your JS project, not Django). **Solution:** Copy the sitemap files to your JS project and deploy them so Google can fetch them.

---

## Step 1: Files to Copy FROM Django Project TO JavaScript Project

### Source (Django) → Destination (JavaScript)

```
FROM:  c:\nexus websites\nexus_web\storefront\static\sitemaps\sitemap_index.xml
TO:    <your-js-project>\public\static\sitemaps\sitemap_index.xml

FROM:  c:\nexus websites\nexus_web\storefront\static\sitemaps\official-beddings_sitemap.xml
TO:    <your-js-project>\public\static\sitemaps\official-beddings_sitemap.xml

FROM:  c:\nexus websites\nexus_web\storefront\static\sitemaps\chill_sitemap.xml
TO:    <your-js-project>\public\static\sitemaps\chill_sitemap.xml

FROM:  c:\nexus websites\nexus_web\storefront\static\sitemaps\sampleshop_sitemap.xml
TO:    <your-js-project>\public\static\sitemaps\sampleshop_sitemap.xml

FROM:  c:\nexus websites\nexus_web\storefront\static\sitemaps\loom_sitemap.xml
TO:    <your-js-project>\public\static\sitemaps\loom_sitemap.xml

FROM:  c:\nexus websites\nexus_web\storefront\static\sitemaps\rphones_sitemap.xml
TO:    <your-js-project>\public\static\sitemaps\rphones_sitemap.xml

FROM:  c:\nexus websites\nexus_web\storefront\static\sitemaps\metadata.json
TO:    <your-js-project>\public\static\sitemaps\metadata.json
```

**In other words:** Copy **ALL files** from `storefront\static\sitemaps\` into your JS project's `public\static\sitemaps\` folder.

---

## Step 2: How to Copy (Windows Command)

Run this in PowerShell (replace path to your JS project):

```powershell
# Create destination folder if it doesn't exist
mkdir "path\to\js-project\public\static\sitemaps" -Force

# Copy all sitemap files
Copy-Item "c:\nexus websites\nexus_web\storefront\static\sitemaps\*" `
  -Destination "path\to\js-project\public\static\sitemaps\" -Force
```

Example (if your JS project is at `C:\nexus websites\nexus_frontend`):

```powershell
mkdir "C:\nexus websites\nexus_frontend\public\static\sitemaps" -Force

Copy-Item "c:\nexus websites\nexus_web\storefront\static\sitemaps\*" `
  -Destination "C:\nexus websites\nexus_frontend\public\static\sitemaps\" -Force
```

---

## Step 3: Configuration Changes to Make

### File: robots.txt

**What to change:** Make sure your `robots.txt` on the main domain points to the correct sitemap path.

**Update:** Add or verify this line in your JS project's `public/robots.txt`:

```txt
Sitemap: https://nexassearch.com/static/sitemaps/sitemap_index.xml
```

**Full example robots.txt:**
```txt
User-agent: *
Allow: /
Disallow: /admin/
Disallow: /login/
Disallow: /signup/
Disallow: /checkout/

Sitemap: https://nexassearch.com/static/sitemaps/sitemap_index.xml
```

### No other code changes needed
- The sitemaps are plain XML files — no code changes required.
- Just copy the files and deploy.

---

## Step 4: Deploy to Production

After copying files, you must deploy your JS project:

### If using Netlify/Vercel:
```bash
git add public/static/sitemaps/*
git commit -m "Add production sitemaps for SEO"
git push origin main
```
(Netlify/Vercel will auto-deploy and make files publicly available)

### If using GitHub Pages:
```bash
git add public/static/sitemaps/*
git commit -m "Add sitemaps"
git push origin main
```

### If using your own web server:
```bash
# Upload the sitemaps folder to your web server at:
/var/www/nexassearch.com/public/static/sitemaps/
```

---

## Step 5: Verify Files Are Accessible

After deploying, test that Google can fetch the sitemap:

```powershell
curl -I https://nexassearch.com/static/sitemaps/sitemap_index.xml
```

**Expected result:**
```
HTTP/1.1 200 OK
Content-Type: application/xml
```

If you see `404 Not Found` — the files weren't deployed correctly. Re-check Step 2 and Step 4.

---

## Step 6: Update Google Search Console

1. Go to: https://search.google.com/search-console/sitemaps/info-drilldown?resource_id=sc-domain:nexassearch.com
2. Delete the old failed submissions (the ones showing "Couldn't fetch")
3. Click "Add new sitemap"
4. Submit: `https://nexassearch.com/static/sitemaps/sitemap_index.xml`
5. Wait 24-48 hours — Google will crawl and index

---

## What Happens After You Deploy

✅ Google fetches `sitemap_index.xml` from your JS project (status 200)
✅ Sitemap index lists all business sitemaps
✅ Google crawls each business sitemap
✅ Google finds all products and images
✅ Products appear in Google Search results (1-2 weeks)

---

## Summary Checklist

- [ ] Copy all files from `c:\nexus websites\nexus_web\storefront\static\sitemaps\*` to JS project `public\static\sitemaps\`
- [ ] Ensure `public\robots.txt` (or `public\index.html` header) references: `Sitemap: https://nexassearch.com/static/sitemaps/sitemap_index.xml`
- [ ] Deploy JS project (git push or upload to server)
- [ ] Verify with: `curl -I https://nexassearch.com/static/sitemaps/sitemap_index.xml` → should return 200 OK
- [ ] Delete old failed sitemaps in Google Search Console
- [ ] Submit `https://nexassearch.com/static/sitemaps/sitemap_index.xml` in Search Console
- [ ] Wait 24-48 hours for Google to crawl

---

## Troubleshooting

### "Couldn't fetch" in Google Search Console
- Reason: Files not deployed to JS project or wrong path
- Fix: Re-run copy command and re-deploy JS project

### Files is HTML instead of XML
- Reason: Netlify/Vercel serving a custom 404 page
- Fix: Check that files are correctly in `public/static/sitemaps/` folder before deploying

### Content-Type is text/html instead of application/xml
- Reason: Web server not configured for .xml files
- Fix: Ask your hosting provider to serve `.xml` files as MIME type `application/xml`

### Files keep getting deleted after deploy
- Reason: Your JS build process is removing static files
- Fix: Check your build config and ensure `public/` folder is preserved during build

---

## Daily Updates (Automation)

After initial setup, you need to **regenerate sitemaps daily** and **copy them to JS project**.

### Option A: Manual (once per day)
```powershell
# In Django project
python run_sitemap_generation.py

# Copy to JS project
Copy-Item "c:\nexus websites\nexus_web\storefront\static\sitemaps\*" `
  -Destination "C:\nexus websites\nexus_frontend\public\static\sitemaps\" -Force

# Deploy JS project
cd C:\nexus websites\nexus_frontend
git add public/static/sitemaps/*
git commit -m "Update sitemaps"
git push origin main
```

### Option B: Automated (Recommended)
Create a Windows Task Scheduler job that runs a PowerShell script daily at 3 AM:

**Script: `C:\nexus websites\update_sitemaps.ps1`**
```powershell
# Generate sitemaps
cd "c:\nexus websites\nexus_web"
python run_sitemap_generation.py

# Copy to JS project
Copy-Item "c:\nexus websites\nexus_web\storefront\static\sitemaps\*" `
  -Destination "C:\nexus websites\nexus_frontend\public\static\sitemaps\" -Force

# Deploy (if using git)
cd "C:\nexus websites\nexus_frontend"
git add public/static/sitemaps/*
git commit -m "Update sitemaps - $(Get-Date -Format 'yyyy-MM-dd')"
git push origin main
```

Then schedule it in Task Scheduler to run daily at 3 AM (after Django cron at 2 AM).

---

## After You Complete These Steps

Contact me when:
- ✅ Files are copied and deployed
- ✅ `curl -I https://nexassearch.com/static/sitemaps/sitemap_index.xml` returns 200 OK
- ✅ You submitted the sitemap in Google Search Console

Then I can help you monitor the indexing progress in Google Search Console.
