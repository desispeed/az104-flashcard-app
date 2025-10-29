# Installation Guide - AZ-104 Exam App

Complete step-by-step installation and setup guide.

## Prerequisites

Before installing, make sure you have:
- Node.js 14+ installed
- npm (comes with Node.js)
- Git installed
- A code editor (VS Code recommended)

### Check Installations

```bash
node --version    # Should be 14.0.0 or higher
npm --version     # Should be 6.0.0 or higher
git --version     # Should be installed
```

## Step 1: Install Node.js

If not installed, download from: https://nodejs.org/

Choose LTS (Long Term Support) version.

### Verify Installation

```bash
node --version
npm --version
```

## Step 2: Extract/Setup Project

### Option A: From ZIP File

1. Extract `az104-app.zip` to your desired location
2. Open Terminal
3. Navigate to project: `cd path/to/az104-app`

### Option B: From GitHub

```bash
git clone https://github.com/YOUR_USERNAME/az104-measureup-exam.git
cd az104-measureup-exam
```

## Step 3: Install Dependencies

```bash
npm install
```

This installs all required packages:
- React 18.2.0
- Tailwind CSS 3.3.0
- Lucide React icons
- react-scripts

**Wait time:** 2-5 minutes depending on internet

When complete, you should see:
```
added XXX packages in X.XXs
```

## Step 4: Verify Installation

Check all files are present:

```bash
ls -la
```

Should show:
```
package.json
package-lock.json
src/
public/
tailwind.config.js
postcss.config.js
vercel.json
.gitignore
README.md
node_modules/
```

## Step 5: Run Locally

Start the development server:

```bash
npm start
```

Should show:
```
Compiled successfully!

Local:            http://localhost:3000
On Your Network:  http://192.168.x.x:3000
```

Browser should auto-open to `http://localhost:3000`

✅ Should see AZ-104 exam app!

## Step 6: Build for Production

When ready to deploy:

```bash
npm run build
```

Creates `build/` folder with optimized production build.

Should show:
```
The build folder is ready to be deployed.
```

## Troubleshooting

### Problem: "npm: command not found"

**Solution:** Install Node.js from https://nodejs.org/

### Problem: Port 3000 already in use

**Solution:** Kill process on port 3000 or use different port:

```bash
npm start -- --port 3001
```

### Problem: "Cannot find module"

**Solution:** Reinstall dependencies:

```bash
rm -rf node_modules package-lock.json
npm install
```

### Problem: "Missing public/index.html"

**Solution:** Verify file structure is correct:

```
az104-app/
├── public/
│   └── index.html
├── src/
│   ├── App.jsx
│   ├── index.js
│   └── index.css
├── package.json
└── [other files]
```

### Problem: Tailwind CSS not working

**Solution:** Check `src/index.css` has Tailwind imports:

```css
@tailwind base;
@tailwind components;
@tailwind utilities;
```

## File Checklist

After installation, verify all files exist:

### Root Level
- [ ] `package.json` - Dependencies
- [ ] `package-lock.json` - Dependency lock
- [ ] `tailwind.config.js` - Tailwind config
- [ ] `postcss.config.js` - PostCSS config
- [ ] `vercel.json` - Vercel config
- [ ] `.gitignore` - Git ignore
- [ ] `README.md` - Readme
- [ ] `INSTALLATION.md` - This file
- [ ] `public/` - Folder
- [ ] `src/` - Folder
- [ ] `node_modules/` - Folder (created by npm)

### public/ Folder
- [ ] `index.html` - Main HTML file

### src/ Folder
- [ ] `App.jsx` - React component (368 lines)
- [ ] `index.js` - Entry point
- [ ] `index.css` - Styles

## Quick Commands Reference

```bash
# Install dependencies
npm install

# Start development server
npm start

# Build for production
npm run build

# Run tests
npm test

# Stop server
Ctrl + C
```

## Deployment

### Deploy to Vercel

1. Push to GitHub:
   ```bash
   git add .
   git commit -m "Initial commit"
   git push origin main
   ```

2. Go to https://vercel.com/new

3. Import your repository

4. Click Deploy

5. Visit your Vercel URL when ready

### Deploy to Netlify

1. Run `npm run build`

2. Go to https://app.netlify.com/drop

3. Drag `build/` folder

4. Done!

## After Installation

### Next Steps

1. **Test locally:** `npm start`
2. **Make changes:** Edit `src/App.jsx`
3. **Add questions:** Add to `AZ104_QUESTIONS` array
4. **Build:** `npm run build`
5. **Deploy:** Push to GitHub and deploy on Vercel

### Customize App

Edit these files to customize:

- `public/index.html` - Change title, description
- `src/App.jsx` - Change questions, styling
- `tailwind.config.js` - Customize Tailwind theme

## System Requirements

| Requirement | Minimum | Recommended |
|---|---|---|
| Node.js | 14.0.0 | 18.0.0+ |
| npm | 6.0.0 | 9.0.0+ |
| Disk Space | 500 MB | 1 GB |
| RAM | 2 GB | 4 GB+ |
| OS | Any | macOS/Linux/Windows |

## File Sizes

Approximate sizes after `npm install`:

```
node_modules/          ~400 MB
public/                ~1 KB
src/                   ~50 KB
build/                 ~200 KB (after build)
```

## Environment

No environment variables required! The app works out of the box.

Optional `.env.local` file for future customization:
```
REACT_APP_API_URL=https://api.example.com
```

## Security

The app does NOT:
- Collect user data
- Send data anywhere
- Require login/authentication
- Store cookies

It's completely local/client-side!

## Support

If you encounter issues:

1. Check this troubleshooting guide
2. Check Node.js installation
3. Try: `rm -rf node_modules && npm install`
4. Check file structure
5. Restart computer
6. Search error message on Google

## Success

When everything works:

✅ `npm start` opens app at localhost:3000
✅ App shows AZ-104 exam questions
✅ All UI elements work (buttons, navigation)
✅ Questions are randomized
✅ Scoring system works
✅ No errors in browser console (F12)

---

**Installation complete!** 🎉

You're ready to start studying for your AZ-104 exam!

