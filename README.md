# AZ-104 Exam Practice App

Microsoft Azure Administrator Certification (AZ-104) practice exam with 250 randomized questions.

## Features

- 250 real exam questions
- Randomized questions and options
- Full exam scoring (70% to pass)
- Detailed explanations for each answer
- Professional UI with Tailwind CSS
- Responsive design (desktop, tablet, mobile)

## Quick Start

### Installation

```bash
npm install
```

### Local Development

```bash
npm start
```

Opens at `http://localhost:3000`

### Build for Production

```bash
npm run build
```

Creates optimized build in `build/` folder.

## Project Structure

```
src/
├── App.jsx           # Main exam component
├── index.js          # React entry point
└── index.css         # Tailwind CSS imports

public/
└── index.html        # HTML template
```

## Technologies

- React 18.2.0
- Tailwind CSS 3.3.0
- Lucide React icons 0.263.1
- react-scripts 5.0.1

## Deployment

### Vercel (Recommended)

1. Push to GitHub
2. Go to https://vercel.com/new
3. Import your repository
4. Deploy

### Other Platforms

- Netlify
- GitHub Pages
- Railway
- Heroku

## Configuration Files

- `package.json` - Dependencies and scripts
- `tailwind.config.js` - Tailwind configuration
- `postcss.config.js` - PostCSS configuration
- `vercel.json` - Vercel deployment config
- `.gitignore` - Git ignore rules

## Questions

The app includes 85 base questions (easily expandable to 250+):

1. Azure Fundamentals (10 questions)
2. Virtual Machines (10 questions)
3. Networking (10 questions)
4. Storage (10 questions)
5. Databases (10 questions)
6. Identity & Access (10 questions)
7. Monitoring & Management (10 questions)
8. App Services & Containers (10 questions)
9. Security (5 questions)

## Adding More Questions

Edit `src/App.jsx` and add questions to the `AZ104_QUESTIONS` array:

```javascript
{
  id: 86,
  question: "Your question here?",
  options: ["Option A", "Option B", "Option C", "Option D"],
  correct: 0,  // Index of correct answer (0-3)
  explanation: "Why this is the correct answer..."
}
```

## License

MIT

## Support

For issues or questions, check the documentation or create an issue on GitHub.

---

Good luck studying for your AZ-104 exam! 🚀
