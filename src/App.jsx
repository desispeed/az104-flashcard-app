// Personal Financial Management App
// Dashboard, Transactions, Budgets & Savings Goals
// React Component with Tailwind CSS — data persisted to localStorage

import React, { useState, useEffect, useMemo } from 'react';
import {
  Wallet, LayoutDashboard, ArrowLeftRight, PiggyBank, Target, Plus, Trash2,
  TrendingUp, TrendingDown, DollarSign, Pencil, X, Search, ChevronLeft,
  ChevronRight, AlertTriangle, CheckCircle, Utensils, Home, Car, HeartPulse,
  Film, ShoppingBag, GraduationCap, Lightbulb, Briefcase, Gift, Landmark, MoreHorizontal,
} from 'lucide-react';

const CATEGORIES = {
  income: [
    { id: 'salary', label: 'Salary', color: '#059669', Icon: Briefcase },
    { id: 'business', label: 'Business', color: '#0d9488', Icon: Landmark },
    { id: 'investments', label: 'Investments', color: '#2563eb', Icon: TrendingUp },
    { id: 'gifts', label: 'Gifts', color: '#db2777', Icon: Gift },
    { id: 'other-income', label: 'Other', color: '#64748b', Icon: MoreHorizontal },
  ],
  expense: [
    { id: 'housing', label: 'Housing', color: '#7c3aed', Icon: Home },
    { id: 'food', label: 'Food & Dining', color: '#ea580c', Icon: Utensils },
    { id: 'transport', label: 'Transport', color: '#0284c7', Icon: Car },
    { id: 'utilities', label: 'Utilities', color: '#ca8a04', Icon: Lightbulb },
    { id: 'health', label: 'Health', color: '#dc2626', Icon: HeartPulse },
    { id: 'entertainment', label: 'Entertainment', color: '#9333ea', Icon: Film },
    { id: 'shopping', label: 'Shopping', color: '#db2777', Icon: ShoppingBag },
    { id: 'education', label: 'Education', color: '#2563eb', Icon: GraduationCap },
    { id: 'other-expense', label: 'Other', color: '#64748b', Icon: MoreHorizontal },
  ],
};

const findCategory = (id) =>
  [...CATEGORIES.income, ...CATEGORIES.expense].find((c) => c.id === id) ||
  CATEGORIES.expense[CATEGORIES.expense.length - 1];

const fmtMoney = (n) =>
  new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(n);

const fmtDate = (iso) =>
  new Date(iso + 'T00:00:00').toLocaleDateString('en-US', {
    month: 'short', day: 'numeric', year: 'numeric',
  });

const monthKey = (iso) => iso.slice(0, 7); // "YYYY-MM"

const monthLabel = (key) =>
  new Date(key + '-01T00:00:00').toLocaleDateString('en-US', {
    month: 'long', year: 'numeric',
  });

const todayISO = () => new Date().toISOString().slice(0, 10);

const uid = () => Date.now().toString(36) + Math.random().toString(36).slice(2, 8);

function usePersistedState(key, initial) {
  const [value, setValue] = useState(() => {
    try {
      const raw = localStorage.getItem(key);
      return raw ? JSON.parse(raw) : initial;
    } catch {
      return initial;
    }
  });
  useEffect(() => {
    try {
      localStorage.setItem(key, JSON.stringify(value));
    } catch {
      // storage full or unavailable — app keeps working in memory
    }
  }, [key, value]);
  return [value, setValue];
}

// ---------- Small shared UI ----------

function StatCard({ title, value, sub, Icon, tone }) {
  const tones = {
    green: 'bg-emerald-50 text-emerald-600',
    red: 'bg-rose-50 text-rose-600',
    blue: 'bg-blue-50 text-blue-600',
    violet: 'bg-violet-50 text-violet-600',
  };
  return (
    <div className="bg-white rounded-2xl shadow-sm border border-slate-100 p-5 flex items-start gap-4">
      <div className={`p-3 rounded-xl ${tones[tone]}`}>
        <Icon size={22} />
      </div>
      <div className="min-w-0">
        <p className="text-sm text-slate-500">{title}</p>
        <p className="text-2xl font-bold text-slate-800 truncate">{value}</p>
        {sub && <p className="text-xs text-slate-400 mt-1">{sub}</p>}
      </div>
    </div>
  );
}

function EmptyState({ Icon, title, hint }) {
  return (
    <div className="text-center py-12">
      <Icon size={40} className="mx-auto text-slate-300 mb-3" />
      <p className="text-slate-600 font-medium">{title}</p>
      <p className="text-sm text-slate-400 mt-1">{hint}</p>
    </div>
  );
}

function Modal({ title, onClose, children }) {
  return (
    <div
      className="fixed inset-0 bg-slate-900/50 flex items-center justify-center p-4 z-50"
      onClick={onClose}
    >
      <div
        className="bg-white rounded-2xl shadow-xl w-full max-w-md max-h-[90vh] overflow-y-auto"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-center justify-between px-6 py-4 border-b border-slate-100">
          <h3 className="font-semibold text-slate-800">{title}</h3>
          <button onClick={onClose} className="text-slate-400 hover:text-slate-600">
            <X size={20} />
          </button>
        </div>
        <div className="p-6">{children}</div>
      </div>
    </div>
  );
}

const inputCls =
  'w-full border border-slate-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent';
const labelCls = 'block text-sm font-medium text-slate-600 mb-1';

// ---------- Charts (inline SVG, no extra dependencies) ----------

function DonutChart({ data }) {
  // data: [{ label, value, color }]
  const total = data.reduce((s, d) => s + d.value, 0);
  if (total === 0) return null;
  const R = 70;
  const C = 2 * Math.PI * R;
  let offset = 0;
  return (
    <div className="flex flex-col sm:flex-row items-center gap-6">
      <svg width="180" height="180" viewBox="0 0 180 180" className="shrink-0 -rotate-90">
        {data.map((d) => {
          const frac = d.value / total;
          const seg = (
            <circle
              key={d.label}
              cx="90" cy="90" r={R} fill="none"
              stroke={d.color} strokeWidth="26"
              strokeDasharray={`${frac * C} ${C}`}
              strokeDashoffset={-offset * C}
            />
          );
          offset += frac;
          return seg;
        })}
      </svg>
      <div className="space-y-2 w-full">
        {data.map((d) => (
          <div key={d.label} className="flex items-center gap-2 text-sm">
            <span className="w-3 h-3 rounded-full shrink-0" style={{ background: d.color }} />
            <span className="text-slate-600 flex-1 truncate">{d.label}</span>
            <span className="font-medium text-slate-800">{fmtMoney(d.value)}</span>
            <span className="text-slate-400 w-12 text-right">
              {Math.round((d.value / total) * 100)}%
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}

function TrendBars({ months }) {
  // months: [{ key, income, expense }] oldest → newest
  const max = Math.max(1, ...months.flatMap((m) => [m.income, m.expense]));
  return (
    <div className="flex items-end justify-between gap-3 h-44">
      {months.map((m) => (
        <div key={m.key} className="flex-1 flex flex-col items-center gap-1 h-full justify-end">
          <div className="flex items-end gap-1 w-full justify-center h-full">
            <div
              className="w-3 sm:w-5 rounded-t bg-emerald-500"
              style={{ height: `${(m.income / max) * 100}%` }}
              title={`Income ${fmtMoney(m.income)}`}
            />
            <div
              className="w-3 sm:w-5 rounded-t bg-rose-400"
              style={{ height: `${(m.expense / max) * 100}%` }}
              title={`Expenses ${fmtMoney(m.expense)}`}
            />
          </div>
          <span className="text-xs text-slate-400">
            {new Date(m.key + '-01T00:00:00').toLocaleDateString('en-US', { month: 'short' })}
          </span>
        </div>
      ))}
    </div>
  );
}

// ---------- Transaction form ----------

function TransactionForm({ initial, onSave, onClose }) {
  const [type, setType] = useState(initial?.type || 'expense');
  const [amount, setAmount] = useState(initial?.amount ?? '');
  const [category, setCategory] = useState(initial?.category || '');
  const [description, setDescription] = useState(initial?.description || '');
  const [date, setDate] = useState(initial?.date || todayISO());

  const cats = CATEGORIES[type];
  const valid = Number(amount) > 0 && category && date;

  const submit = (e) => {
    e.preventDefault();
    if (!valid) return;
    onSave({
      id: initial?.id || uid(),
      type,
      amount: Number(amount),
      category,
      description: description.trim(),
      date,
    });
    onClose();
  };

  return (
    <form onSubmit={submit} className="space-y-4">
      <div className="grid grid-cols-2 gap-2">
        {['expense', 'income'].map((t) => (
          <button
            key={t}
            type="button"
            onClick={() => { setType(t); setCategory(''); }}
            className={`py-2 rounded-lg text-sm font-medium border transition-colors ${
              type === t
                ? t === 'expense'
                  ? 'bg-rose-50 border-rose-300 text-rose-600'
                  : 'bg-emerald-50 border-emerald-300 text-emerald-600'
                : 'border-slate-200 text-slate-500 hover:bg-slate-50'
            }`}
          >
            {t === 'expense' ? 'Expense' : 'Income'}
          </button>
        ))}
      </div>
      <div>
        <label className={labelCls}>Amount</label>
        <input
          type="number" min="0.01" step="0.01" required autoFocus
          value={amount} onChange={(e) => setAmount(e.target.value)}
          placeholder="0.00" className={inputCls}
        />
      </div>
      <div>
        <label className={labelCls}>Category</label>
        <div className="grid grid-cols-3 gap-2">
          {cats.map(({ id, label, Icon }) => (
            <button
              key={id} type="button" onClick={() => setCategory(id)}
              className={`flex flex-col items-center gap-1 p-2 rounded-lg border text-xs transition-colors ${
                category === id
                  ? 'border-blue-400 bg-blue-50 text-blue-700'
                  : 'border-slate-200 text-slate-500 hover:bg-slate-50'
              }`}
            >
              <Icon size={16} />
              {label}
            </button>
          ))}
        </div>
      </div>
      <div>
        <label className={labelCls}>Description</label>
        <input
          type="text" value={description} onChange={(e) => setDescription(e.target.value)}
          placeholder="Optional note" className={inputCls}
        />
      </div>
      <div>
        <label className={labelCls}>Date</label>
        <input
          type="date" required value={date} onChange={(e) => setDate(e.target.value)}
          className={inputCls}
        />
      </div>
      <button
        type="submit" disabled={!valid}
        className="w-full py-2.5 rounded-lg bg-blue-600 text-white font-medium hover:bg-blue-700 disabled:opacity-40 disabled:cursor-not-allowed"
      >
        {initial ? 'Save Changes' : 'Add Transaction'}
      </button>
    </form>
  );
}

function TransactionRow({ tx, onEdit, onDelete }) {
  const cat = findCategory(tx.category);
  const { Icon } = cat;
  return (
    <div className="flex items-center gap-3 py-3 group">
      <div className="p-2.5 rounded-xl shrink-0" style={{ background: cat.color + '18', color: cat.color }}>
        <Icon size={18} />
      </div>
      <div className="flex-1 min-w-0">
        <p className="text-sm font-medium text-slate-800 truncate">
          {tx.description || cat.label}
        </p>
        <p className="text-xs text-slate-400">{cat.label} · {fmtDate(tx.date)}</p>
      </div>
      <span className={`text-sm font-semibold ${tx.type === 'income' ? 'text-emerald-600' : 'text-slate-800'}`}>
        {tx.type === 'income' ? '+' : '−'}{fmtMoney(tx.amount)}
      </span>
      {onEdit && (
        <div className="flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
          <button onClick={() => onEdit(tx)} className="p-1.5 text-slate-400 hover:text-blue-600" aria-label="Edit">
            <Pencil size={15} />
          </button>
          <button onClick={() => onDelete(tx.id)} className="p-1.5 text-slate-400 hover:text-rose-600" aria-label="Delete">
            <Trash2 size={15} />
          </button>
        </div>
      )}
    </div>
  );
}

// ---------- Views ----------

function Dashboard({ transactions, month, setMonth }) {
  const monthTx = transactions.filter((t) => monthKey(t.date) === month);
  const income = monthTx.filter((t) => t.type === 'income').reduce((s, t) => s + t.amount, 0);
  const expenses = monthTx.filter((t) => t.type === 'expense').reduce((s, t) => s + t.amount, 0);
  const balance = transactions.reduce(
    (s, t) => s + (t.type === 'income' ? t.amount : -t.amount), 0
  );
  const savingsRate = income > 0 ? Math.round(((income - expenses) / income) * 100) : null;

  const byCategory = useMemo(() => {
    const map = {};
    monthTx.filter((t) => t.type === 'expense').forEach((t) => {
      map[t.category] = (map[t.category] || 0) + t.amount;
    });
    return Object.entries(map)
      .map(([id, value]) => {
        const cat = findCategory(id);
        return { label: cat.label, color: cat.color, value };
      })
      .sort((a, b) => b.value - a.value);
  }, [transactions, month]); // eslint-disable-line react-hooks/exhaustive-deps

  const trend = useMemo(() => {
    const base = new Date(month + '-01T00:00:00');
    return Array.from({ length: 6 }, (_, i) => {
      const d = new Date(base.getFullYear(), base.getMonth() - (5 - i), 1);
      const key = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}`;
      const txs = transactions.filter((t) => monthKey(t.date) === key);
      return {
        key,
        income: txs.filter((t) => t.type === 'income').reduce((s, t) => s + t.amount, 0),
        expense: txs.filter((t) => t.type === 'expense').reduce((s, t) => s + t.amount, 0),
      };
    });
  }, [transactions, month]);

  const shiftMonth = (delta) => {
    const d = new Date(month + '-01T00:00:00');
    d.setMonth(d.getMonth() + delta);
    setMonth(`${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}`);
  };

  const recent = [...monthTx].sort((a, b) => b.date.localeCompare(a.date)).slice(0, 6);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold text-slate-800">Overview</h2>
        <div className="flex items-center gap-2 bg-white border border-slate-200 rounded-lg px-2 py-1">
          <button onClick={() => shiftMonth(-1)} className="p-1 text-slate-400 hover:text-slate-700" aria-label="Previous month">
            <ChevronLeft size={16} />
          </button>
          <span className="text-sm font-medium text-slate-700 w-32 text-center">{monthLabel(month)}</span>
          <button onClick={() => shiftMonth(1)} className="p-1 text-slate-400 hover:text-slate-700" aria-label="Next month">
            <ChevronRight size={16} />
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard title="Total Balance" value={fmtMoney(balance)} sub="All time" Icon={Wallet} tone="blue" />
        <StatCard title="Income" value={fmtMoney(income)} sub={monthLabel(month)} Icon={TrendingUp} tone="green" />
        <StatCard title="Expenses" value={fmtMoney(expenses)} sub={monthLabel(month)} Icon={TrendingDown} tone="red" />
        <StatCard
          title="Savings Rate"
          value={savingsRate === null ? '—' : `${savingsRate}%`}
          sub={savingsRate === null ? 'No income this month' : 'Of monthly income'}
          Icon={PiggyBank} tone="violet"
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <div className="bg-white rounded-2xl shadow-sm border border-slate-100 p-6">
          <h3 className="font-semibold text-slate-800 mb-4">Spending by Category</h3>
          {byCategory.length ? (
            <DonutChart data={byCategory} />
          ) : (
            <EmptyState Icon={DollarSign} title="No expenses this month" hint="Add a transaction to see the breakdown." />
          )}
        </div>
        <div className="bg-white rounded-2xl shadow-sm border border-slate-100 p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="font-semibold text-slate-800">6-Month Trend</h3>
            <div className="flex items-center gap-3 text-xs text-slate-500">
              <span className="flex items-center gap-1"><span className="w-2.5 h-2.5 rounded-sm bg-emerald-500" /> Income</span>
              <span className="flex items-center gap-1"><span className="w-2.5 h-2.5 rounded-sm bg-rose-400" /> Expenses</span>
            </div>
          </div>
          <TrendBars months={trend} />
        </div>
      </div>

      <div className="bg-white rounded-2xl shadow-sm border border-slate-100 p-6">
        <h3 className="font-semibold text-slate-800 mb-2">Recent Transactions</h3>
        {recent.length ? (
          <div className="divide-y divide-slate-50">
            {recent.map((tx) => <TransactionRow key={tx.id} tx={tx} />)}
          </div>
        ) : (
          <EmptyState Icon={ArrowLeftRight} title="Nothing recorded yet" hint="Use the “Add Transaction” button to get started." />
        )}
      </div>
    </div>
  );
}

function Transactions({ transactions, onEdit, onDelete }) {
  const [query, setQuery] = useState('');
  const [typeFilter, setTypeFilter] = useState('all');

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase();
    return [...transactions]
      .filter((t) => typeFilter === 'all' || t.type === typeFilter)
      .filter((t) =>
        !q ||
        t.description.toLowerCase().includes(q) ||
        findCategory(t.category).label.toLowerCase().includes(q)
      )
      .sort((a, b) => b.date.localeCompare(a.date));
  }, [transactions, query, typeFilter]);

  const grouped = useMemo(() => {
    const map = new Map();
    filtered.forEach((t) => {
      const k = monthKey(t.date);
      if (!map.has(k)) map.set(k, []);
      map.get(k).push(t);
    });
    return [...map.entries()];
  }, [filtered]);

  return (
    <div className="space-y-4">
      <div className="flex flex-col sm:flex-row gap-3">
        <div className="relative flex-1">
          <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
          <input
            value={query} onChange={(e) => setQuery(e.target.value)}
            placeholder="Search description or category…"
            className={`${inputCls} pl-9`}
          />
        </div>
        <div className="flex rounded-lg border border-slate-200 overflow-hidden bg-white">
          {['all', 'income', 'expense'].map((t) => (
            <button
              key={t} onClick={() => setTypeFilter(t)}
              className={`px-4 py-2 text-sm capitalize ${
                typeFilter === t ? 'bg-blue-600 text-white' : 'text-slate-500 hover:bg-slate-50'
              }`}
            >
              {t}
            </button>
          ))}
        </div>
      </div>

      {grouped.length ? (
        grouped.map(([key, txs]) => (
          <div key={key} className="bg-white rounded-2xl shadow-sm border border-slate-100 p-6">
            <h3 className="font-semibold text-slate-800 mb-2">{monthLabel(key)}</h3>
            <div className="divide-y divide-slate-50">
              {txs.map((tx) => (
                <TransactionRow key={tx.id} tx={tx} onEdit={onEdit} onDelete={onDelete} />
              ))}
            </div>
          </div>
        ))
      ) : (
        <div className="bg-white rounded-2xl shadow-sm border border-slate-100">
          <EmptyState
            Icon={ArrowLeftRight}
            title={transactions.length ? 'No matching transactions' : 'No transactions yet'}
            hint={transactions.length ? 'Try a different search or filter.' : 'Add your first income or expense to get started.'}
          />
        </div>
      )}
    </div>
  );
}

function Budgets({ transactions, budgets, setBudgets, month }) {
  const [editing, setEditing] = useState(null); // category id
  const [draft, setDraft] = useState('');

  const spentFor = (catId) =>
    transactions
      .filter((t) => t.type === 'expense' && t.category === catId && monthKey(t.date) === month)
      .reduce((s, t) => s + t.amount, 0);

  const save = (catId) => {
    const n = Number(draft);
    setBudgets((b) => {
      const next = { ...b };
      if (n > 0) next[catId] = n;
      else delete next[catId];
      return next;
    });
    setEditing(null);
  };

  const totalBudget = Object.values(budgets).reduce((s, n) => s + n, 0);
  const totalSpent = CATEGORIES.expense.reduce(
    (s, c) => s + (budgets[c.id] ? spentFor(c.id) : 0), 0
  );

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold text-slate-800">Budgets · {monthLabel(month)}</h2>
        {totalBudget > 0 && (
          <span className="text-sm text-slate-500">
            {fmtMoney(totalSpent)} of {fmtMoney(totalBudget)} budgeted
          </span>
        )}
      </div>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {CATEGORIES.expense.map((cat) => {
          const { Icon } = cat;
          const limit = budgets[cat.id];
          const spent = spentFor(cat.id);
          const pct = limit ? Math.min(100, (spent / limit) * 100) : 0;
          const over = limit && spent > limit;
          const near = limit && !over && spent >= limit * 0.8;
          return (
            <div key={cat.id} className="bg-white rounded-2xl shadow-sm border border-slate-100 p-5">
              <div className="flex items-center gap-3 mb-3">
                <div className="p-2 rounded-xl" style={{ background: cat.color + '18', color: cat.color }}>
                  <Icon size={18} />
                </div>
                <span className="font-medium text-slate-800 flex-1">{cat.label}</span>
                {editing === cat.id ? (
                  <div className="flex items-center gap-2">
                    <input
                      type="number" min="0" step="1" autoFocus value={draft}
                      onChange={(e) => setDraft(e.target.value)}
                      onKeyDown={(e) => e.key === 'Enter' && save(cat.id)}
                      className="w-24 border border-slate-200 rounded-lg px-2 py-1 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                    <button onClick={() => save(cat.id)} className="text-blue-600 text-sm font-medium">Save</button>
                  </div>
                ) : (
                  <button
                    onClick={() => { setEditing(cat.id); setDraft(limit || ''); }}
                    className="text-sm text-slate-400 hover:text-blue-600 flex items-center gap-1"
                  >
                    <Pencil size={13} />
                    {limit ? fmtMoney(limit) : 'Set limit'}
                  </button>
                )}
              </div>
              {limit ? (
                <>
                  <div className="h-2.5 bg-slate-100 rounded-full overflow-hidden">
                    <div
                      className={`h-full rounded-full transition-all ${
                        over ? 'bg-rose-500' : near ? 'bg-amber-400' : 'bg-emerald-500'
                      }`}
                      style={{ width: `${pct}%` }}
                    />
                  </div>
                  <div className="flex items-center justify-between mt-2 text-xs">
                    <span className="text-slate-500">{fmtMoney(spent)} spent</span>
                    {over ? (
                      <span className="flex items-center gap-1 text-rose-600 font-medium">
                        <AlertTriangle size={12} /> {fmtMoney(spent - limit)} over
                      </span>
                    ) : (
                      <span className="flex items-center gap-1 text-emerald-600">
                        <CheckCircle size={12} /> {fmtMoney(limit - spent)} left
                      </span>
                    )}
                  </div>
                </>
              ) : (
                <p className="text-xs text-slate-400">
                  No budget set{spent > 0 && ` · ${fmtMoney(spent)} spent this month`}
                </p>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}

function Goals({ goals, setGoals }) {
  const [showForm, setShowForm] = useState(false);
  const [contributing, setContributing] = useState(null); // goal id
  const [contribAmount, setContribAmount] = useState('');
  const [name, setName] = useState('');
  const [target, setTarget] = useState('');
  const [saved, setSaved] = useState('');

  const addGoal = (e) => {
    e.preventDefault();
    if (!name.trim() || !(Number(target) > 0)) return;
    setGoals((g) => [
      ...g,
      { id: uid(), name: name.trim(), target: Number(target), saved: Number(saved) || 0 },
    ]);
    setName(''); setTarget(''); setSaved(''); setShowForm(false);
  };

  const contribute = (id) => {
    const n = Number(contribAmount);
    if (n > 0) {
      setGoals((g) => g.map((goal) =>
        goal.id === id ? { ...goal, saved: goal.saved + n } : goal
      ));
    }
    setContributing(null);
    setContribAmount('');
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold text-slate-800">Savings Goals</h2>
        <button
          onClick={() => setShowForm(true)}
          className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-lg hover:bg-blue-700"
        >
          <Plus size={16} /> New Goal
        </button>
      </div>

      {goals.length ? (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {goals.map((goal) => {
            const pct = Math.min(100, (goal.saved / goal.target) * 100);
            const done = goal.saved >= goal.target;
            return (
              <div key={goal.id} className="bg-white rounded-2xl shadow-sm border border-slate-100 p-5">
                <div className="flex items-center gap-3 mb-3">
                  <div className={`p-2 rounded-xl ${done ? 'bg-emerald-50 text-emerald-600' : 'bg-violet-50 text-violet-600'}`}>
                    {done ? <CheckCircle size={18} /> : <Target size={18} />}
                  </div>
                  <span className="font-medium text-slate-800 flex-1">{goal.name}</span>
                  <button
                    onClick={() => setGoals((g) => g.filter((x) => x.id !== goal.id))}
                    className="text-slate-300 hover:text-rose-500" aria-label="Delete goal"
                  >
                    <Trash2 size={15} />
                  </button>
                </div>
                <div className="h-2.5 bg-slate-100 rounded-full overflow-hidden">
                  <div
                    className={`h-full rounded-full transition-all ${done ? 'bg-emerald-500' : 'bg-violet-500'}`}
                    style={{ width: `${pct}%` }}
                  />
                </div>
                <div className="flex items-center justify-between mt-2 text-sm">
                  <span className="text-slate-500">
                    {fmtMoney(goal.saved)} of {fmtMoney(goal.target)}
                  </span>
                  <span className={`font-medium ${done ? 'text-emerald-600' : 'text-slate-700'}`}>
                    {done ? 'Reached! 🎉' : `${Math.round(pct)}%`}
                  </span>
                </div>
                {!done && (
                  contributing === goal.id ? (
                    <div className="flex gap-2 mt-3">
                      <input
                        type="number" min="0.01" step="0.01" autoFocus
                        value={contribAmount}
                        onChange={(e) => setContribAmount(e.target.value)}
                        onKeyDown={(e) => e.key === 'Enter' && contribute(goal.id)}
                        placeholder="Amount" className={inputCls}
                      />
                      <button
                        onClick={() => contribute(goal.id)}
                        className="px-4 py-2 bg-violet-600 text-white text-sm font-medium rounded-lg hover:bg-violet-700"
                      >
                        Add
                      </button>
                    </div>
                  ) : (
                    <button
                      onClick={() => setContributing(goal.id)}
                      className="mt-3 w-full py-2 border border-violet-200 text-violet-600 text-sm font-medium rounded-lg hover:bg-violet-50"
                    >
                      + Add contribution
                    </button>
                  )
                )}
              </div>
            );
          })}
        </div>
      ) : (
        <div className="bg-white rounded-2xl shadow-sm border border-slate-100">
          <EmptyState
            Icon={Target}
            title="No savings goals yet"
            hint="Create a goal like “Emergency Fund” or “Vacation” and track your progress."
          />
        </div>
      )}

      {showForm && (
        <Modal title="New Savings Goal" onClose={() => setShowForm(false)}>
          <form onSubmit={addGoal} className="space-y-4">
            <div>
              <label className={labelCls}>Goal name</label>
              <input
                type="text" required autoFocus value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="e.g. Emergency Fund" className={inputCls}
              />
            </div>
            <div>
              <label className={labelCls}>Target amount</label>
              <input
                type="number" min="1" step="0.01" required value={target}
                onChange={(e) => setTarget(e.target.value)}
                placeholder="5000" className={inputCls}
              />
            </div>
            <div>
              <label className={labelCls}>Already saved (optional)</label>
              <input
                type="number" min="0" step="0.01" value={saved}
                onChange={(e) => setSaved(e.target.value)}
                placeholder="0" className={inputCls}
              />
            </div>
            <button
              type="submit"
              className="w-full py-2.5 rounded-lg bg-blue-600 text-white font-medium hover:bg-blue-700"
            >
              Create Goal
            </button>
          </form>
        </Modal>
      )}
    </div>
  );
}

// ---------- App shell ----------

const TABS = [
  { id: 'dashboard', label: 'Dashboard', Icon: LayoutDashboard },
  { id: 'transactions', label: 'Transactions', Icon: ArrowLeftRight },
  { id: 'budgets', label: 'Budgets', Icon: PiggyBank },
  { id: 'goals', label: 'Goals', Icon: Target },
];

export default function App() {
  const [tab, setTab] = useState('dashboard');
  const [transactions, setTransactions] = usePersistedState('finance.transactions', []);
  const [budgets, setBudgets] = usePersistedState('finance.budgets', {});
  const [goals, setGoals] = usePersistedState('finance.goals', []);
  const [month, setMonth] = useState(() => todayISO().slice(0, 7));
  const [formOpen, setFormOpen] = useState(false);
  const [editingTx, setEditingTx] = useState(null);

  const saveTx = (tx) => {
    setTransactions((txs) => {
      const exists = txs.some((t) => t.id === tx.id);
      return exists ? txs.map((t) => (t.id === tx.id ? tx : t)) : [...txs, tx];
    });
  };

  const deleteTx = (id) => setTransactions((txs) => txs.filter((t) => t.id !== id));

  const openEdit = (tx) => { setEditingTx(tx); setFormOpen(true); };
  const closeForm = () => { setFormOpen(false); setEditingTx(null); };

  return (
    <div className="min-h-screen bg-slate-50">
      <header className="bg-white border-b border-slate-100 sticky top-0 z-40">
        <div className="max-w-6xl mx-auto px-4 sm:px-6">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center gap-2.5">
              <div className="p-2 bg-blue-600 rounded-xl text-white">
                <Wallet size={20} />
              </div>
              <div>
                <h1 className="font-bold text-slate-800 leading-tight">FinTrack</h1>
                <p className="text-xs text-slate-400 leading-tight">Personal finance manager</p>
              </div>
            </div>
            <button
              onClick={() => setFormOpen(true)}
              className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-lg hover:bg-blue-700"
            >
              <Plus size={16} />
              <span className="hidden sm:inline">Add Transaction</span>
              <span className="sm:hidden">Add</span>
            </button>
          </div>
          <nav className="flex gap-1 -mb-px overflow-x-auto">
            {TABS.map(({ id, label, Icon }) => (
              <button
                key={id} onClick={() => setTab(id)}
                className={`flex items-center gap-2 px-4 py-3 text-sm font-medium border-b-2 whitespace-nowrap transition-colors ${
                  tab === id
                    ? 'border-blue-600 text-blue-600'
                    : 'border-transparent text-slate-500 hover:text-slate-700'
                }`}
              >
                <Icon size={16} />
                {label}
              </button>
            ))}
          </nav>
        </div>
      </header>

      <main className="max-w-6xl mx-auto px-4 sm:px-6 py-6">
        {tab === 'dashboard' && (
          <Dashboard transactions={transactions} month={month} setMonth={setMonth} />
        )}
        {tab === 'transactions' && (
          <Transactions transactions={transactions} onEdit={openEdit} onDelete={deleteTx} />
        )}
        {tab === 'budgets' && (
          <Budgets transactions={transactions} budgets={budgets} setBudgets={setBudgets} month={month} />
        )}
        {tab === 'goals' && <Goals goals={goals} setGoals={setGoals} />}
      </main>

      {formOpen && (
        <Modal title={editingTx ? 'Edit Transaction' : 'Add Transaction'} onClose={closeForm}>
          <TransactionForm initial={editingTx} onSave={saveTx} onClose={closeForm} />
        </Modal>
      )}
    </div>
  );
}
