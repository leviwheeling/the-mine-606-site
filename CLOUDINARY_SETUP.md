# Cloudinary Setup Guide

Your app now supports **Cloudinary** for fast, optimized image storage! Here's how to set it up:

## 🚀 Quick Setup (5 minutes)

### 1. Create Free Cloudinary Account
- Go to [cloudinary.com](https://cloudinary.com)
- Sign up for free (15GB storage included!)
- After signup, go to your **Dashboard**

### 2. Get Your Credentials
From your Cloudinary Dashboard, copy these 3 values:
- **Cloud Name** (e.g., `dxy123abc`)
- **API Key** (e.g., `123456789012345`)
- **API Secret** (e.g., `abcdef123456789`)

### 3. Add to Your Environment
Create/update your `.env` file with:

```bash
# Cloudinary Configuration
CLOUDINARY_CLOUD_NAME=your_cloud_name_here
CLOUDINARY_API_KEY=your_api_key_here
CLOUDINARY_API_SECRET=your_api_secret_here
```

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

### 5. Restart Your App
```bash
uvicorn app.main:app --reload
```

## ✨ What You Get

### Automatic Benefits:
- **15GB free storage** (way more than you need for menu photos)
- **Automatic image optimization** (WebP conversion, compression)
- **Fast CDN delivery** (images load faster for customers)
- **Automatic resizing** (images are optimized to 800px width max)
- **Local fallback** (if Cloudinary fails, saves locally)

### Admin Experience:
- Upload photos exactly like before
- Photos automatically go to cloud
- Faster page loading
- Better mobile experience

## 🔄 Fallback System

**Don't worry!** Your app has smart fallbacks:

1. **With Cloudinary**: Photos go to cloud, load super fast
2. **Without Cloudinary**: Photos save locally like before
3. **If Cloudinary fails**: Automatically saves locally as backup

## 💡 Pro Tips

### For Restaurant Owners:
- Take photos with your phone
- Upload directly through admin panel
- Photos automatically get optimized
- No need to resize or compress manually

### For Developers:
- Check storage status: Visit `/admin` to see if Cloudinary is active
- Images are stored in `mine606/menu/` folder on Cloudinary
- Old local images still work fine
- Migration is seamless

## 🆘 Troubleshooting

**Images not uploading?**
1. Check your `.env` file has all 3 Cloudinary variables
2. Restart your app after adding env variables
3. Check the console for error messages

**Want to see what's happening?**
- Your app automatically detects if Cloudinary is configured
- Without setup: Uses local storage (works fine!)
- With setup: Uses Cloudinary + local fallback

## 📊 Free Tier Limits

Cloudinary Free includes:
- **15GB storage** (thousands of menu photos)
- **15GB monthly bandwidth** (plenty for restaurant traffic)
- **Basic transformations** (resize, optimize, format conversion)

Perfect for restaurant websites! 🎉
