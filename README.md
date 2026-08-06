# FinTrack — Personal Financial Management App

A personal finance manager built with React and Tailwind CSS. Track income and
expenses, set monthly budgets per category, and work toward savings goals — all
data is stored locally in your browser (localStorage), so nothing leaves your
device.

## Features

### 📊 Dashboard
- Total balance, monthly income, expenses, and savings rate at a glance
- Spending breakdown by category (donut chart)
- 6-month income vs. expense trend
- Recent transactions, with a month selector to browse history

### 💸 Transactions
- Add, edit, and delete income and expense entries
- 14 built-in categories with icons and colors
- Search by description or category, filter by type, grouped by month

### 🐷 Budgets
- Set a monthly spending limit per expense category
- Progress bars with warnings at 80% and over-budget alerts
- Tracks against the month selected on the dashboard

### 🎯 Savings Goals
- Create goals with a target amount (e.g. Emergency Fund, Vacation)
- Log contributions and watch progress toward each target

## Getting Started

```bash
npm install
npm start
```

The app runs at [http://localhost:3000](http://localhost:3000).

## Build for Production

```bash
npm run build
```

Outputs a static build to `build/` (ready to deploy, e.g. to Vercel — a
`vercel.json` is included).

## Tech Stack

- [React 18](https://react.dev/) (Create React App)
- [Tailwind CSS 3](https://tailwindcss.com/)
- [Lucide](https://lucide.dev/) icons
- No backend — data persists in `localStorage`
