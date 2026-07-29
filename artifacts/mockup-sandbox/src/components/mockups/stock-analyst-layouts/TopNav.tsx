import React from 'react';
import {
  LayoutDashboard,
  TrendingUp,
  Upload,
  MessageSquare,
  User,
  BrainCircuit,
  ArrowUpRight,
  ArrowDownRight,
  Sparkles,
  Wallet,
  Activity,
  LineChart
} from 'lucide-react';

const DONUT_DATA = [
  { ticker: "AAPL", value: 42300, pct: 28, color: "#4f46e5" },
  { ticker: "MSFT", value: 31100, pct: 21, color: "#3b82f6" },
  { ticker: "NVDA", value: 28500, pct: 19, color: "#0ea5e9" },
  { ticker: "GOOGL", value: 19800, pct: 13, color: "#06b6d4" },
  { ticker: "TSLA", value: 15200, pct: 10, color: "#14b8a6" },
  { ticker: "AMZN", value: 12900, pct: 9, color: "#10b981" },
];

const HOLDINGS = [
  { ticker: "AAPL", name: "Apple Inc.", shares: 200, avgCost: 160.00, current: 211.50, value: 42300, pl: 10300, plPct: 32.1 },
  { ticker: "MSFT", name: "Microsoft Corp.", shares: 100, avgCost: 250.00, current: 311.00, value: 31100, pl: 6100, plPct: 24.4 },
  { ticker: "NVDA", name: "NVIDIA Corp.", shares: 50, avgCost: 400.00, current: 570.00, value: 28500, pl: 8500, plPct: 42.5 },
  { ticker: "GOOGL", name: "Alphabet Inc.", shares: 150, avgCost: 100.00, current: 132.00, value: 19800, pl: 4800, plPct: 32.0 },
  { ticker: "TSLA", name: "Tesla Inc.", shares: 100, avgCost: 230.00, current: 152.00, value: 15200, pl: -7800, plPct: -33.9 },
  { ticker: "AMZN", name: "Amazon.com Inc.", shares: 100, avgCost: 182.00, current: 129.00, value: 12900, pl: -5300, plPct: -29.1 },
];

function KpiCard({ title, value, trend, subtext, icon, trendDown }: any) {
  return (
    <div className="bg-white border border-slate-200 rounded-xl p-4 shadow-sm flex items-center justify-between">
      <div>
        <div className="text-sm font-medium text-slate-500 mb-1">{title}</div>
        <div className="flex items-baseline gap-2">
          <h2 className="text-2xl font-bold text-slate-900">{value}</h2>
          {trend && (
            <span className={`text-sm font-medium flex items-center ${trendDown ? 'text-rose-600' : 'text-emerald-600'}`}>
              {trendDown ? <ArrowDownRight className="h-4 w-4 mr-0.5" /> : <ArrowUpRight className="h-4 w-4 mr-0.5" />}
              {trend}
            </span>
          )}
          {subtext && (
            <span className="text-sm text-slate-400">{subtext}</span>
          )}
        </div>
      </div>
      <div className="h-10 w-10 rounded-full bg-slate-50 flex items-center justify-center text-slate-400 border border-slate-100">
        {icon}
      </div>
    </div>
  );
}

function DonutChart() {
  const radius = 40;
  const circum = 2 * Math.PI * radius; 
  let cumulative = 0;
  
  return (
    <div className="flex h-full w-full items-center px-2">
      <div className="relative h-28 w-28 shrink-0">
        <svg viewBox="0 0 100 100" className="h-full w-full -rotate-90">
          {DONUT_DATA.map((item) => {
            const strokeValue = (item.pct * circum) / 100;
            const strokeGap = circum - strokeValue;
            const offset = -(cumulative * circum) / 100;
            cumulative += item.pct;
            
            return (
              <circle
                key={item.ticker}
                cx="50"
                cy="50"
                r={radius}
                fill="transparent"
                stroke={item.color}
                strokeWidth="16"
                strokeDasharray={`${strokeValue} ${strokeGap}`}
                strokeDashoffset={offset}
                className="transition-all duration-500"
              />
            );
          })}
        </svg>
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span className="text-[10px] uppercase tracking-wider font-semibold text-slate-500">Holdings</span>
          <span className="text-sm font-bold text-slate-900">6 Assets</span>
        </div>
      </div>
      
      <div className="ml-8 grid grid-cols-3 gap-x-8 gap-y-2.5 flex-1">
        {DONUT_DATA.map(item => (
          <div key={item.ticker} className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <div className="h-2 w-2 rounded-sm" style={{ backgroundColor: item.color }} />
              <span className="text-sm font-medium text-slate-700">{item.ticker}</span>
            </div>
            <span className="text-sm font-semibold text-slate-900">{item.pct}%</span>
          </div>
        ))}
      </div>
    </div>
  );
}

function HoldingsTable() {
  return (
    <div className="w-full h-full flex flex-col">
      <div className="px-5 py-3 border-b border-slate-200 flex items-center justify-between shrink-0 bg-white">
        <h3 className="font-semibold text-slate-800">Position Details</h3>
        <button className="text-xs font-semibold text-indigo-600 hover:text-indigo-700 bg-indigo-50 px-2.5 py-1 rounded-md transition-colors">
          View Full History
        </button>
      </div>
      <div className="flex-1 overflow-auto bg-white">
        <table className="w-full text-left text-sm whitespace-nowrap">
          <thead className="bg-slate-50/80 sticky top-0 z-10 shadow-[0_1px_0_#e2e8f0] backdrop-blur-sm">
            <tr>
              <th className="px-5 py-2.5 font-semibold text-slate-500 text-xs uppercase tracking-wider">Asset</th>
              <th className="px-5 py-2.5 font-semibold text-slate-500 text-xs uppercase tracking-wider text-right">Shares</th>
              <th className="px-5 py-2.5 font-semibold text-slate-500 text-xs uppercase tracking-wider text-right">Avg Cost</th>
              <th className="px-5 py-2.5 font-semibold text-slate-500 text-xs uppercase tracking-wider text-right">Price</th>
              <th className="px-5 py-2.5 font-semibold text-slate-500 text-xs uppercase tracking-wider text-right">Total Value</th>
              <th className="px-5 py-2.5 font-semibold text-slate-500 text-xs uppercase tracking-wider text-right">Unrealized P&L</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {HOLDINGS.map(h => (
              <tr key={h.ticker} className="hover:bg-slate-50/80 transition-colors group">
                <td className="px-5 py-2">
                  <div className="flex items-center gap-3">
                    <div className="h-7 w-7 rounded bg-slate-100 flex items-center justify-center text-xs font-bold text-slate-700 group-hover:bg-white group-hover:shadow-sm transition-all border border-transparent group-hover:border-slate-200">
                      {h.ticker[0]}
                    </div>
                    <div>
                      <div className="font-semibold text-slate-900 leading-tight">{h.ticker}</div>
                      <div className="text-[11px] text-slate-500 leading-tight">{h.name}</div>
                    </div>
                  </div>
                </td>
                <td className="px-5 py-2 text-right font-medium text-slate-700">{h.shares}</td>
                <td className="px-5 py-2 text-right text-slate-600">${h.avgCost.toFixed(2)}</td>
                <td className="px-5 py-2 text-right font-medium text-slate-900">${h.current.toFixed(2)}</td>
                <td className="px-5 py-2 text-right font-semibold text-slate-900">${h.value.toLocaleString()}</td>
                <td className="px-5 py-2 text-right">
                  <div className={`inline-flex items-center gap-0.5 px-2 py-1 rounded-md text-xs font-semibold ${h.pl >= 0 ? 'bg-emerald-50 text-emerald-700' : 'bg-rose-50 text-rose-700'}`}>
                    {h.pl >= 0 ? <ArrowUpRight className="h-3 w-3" /> : <ArrowDownRight className="h-3 w-3" />}
                    ${Math.abs(h.pl).toLocaleString()} ({Math.abs(h.plPct)}%)
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function AiSummaryCard() {
  return (
    <div className="bg-gradient-to-br from-[#f8f9ff] via-white to-[#f0f4ff] h-full rounded-xl border border-indigo-100 p-5 flex flex-col relative overflow-hidden">
      {/* Decorative blurred blobs */}
      <div className="absolute top-0 right-0 -mr-16 -mt-16 w-64 h-64 bg-indigo-200/30 rounded-full blur-3xl pointer-events-none" />
      <div className="absolute bottom-0 left-0 -ml-16 -mb-16 w-64 h-64 bg-violet-200/30 rounded-full blur-3xl pointer-events-none" />
      
      <div className="relative z-10 flex items-center gap-3 mb-5">
        <div className="h-9 w-9 rounded-lg bg-indigo-600 flex items-center justify-center shadow-sm shadow-indigo-200">
          <Sparkles className="h-4 w-4 text-white" />
        </div>
        <div>
          <h3 className="font-semibold text-slate-900 leading-tight">AI Portfolio Health</h3>
          <p className="text-[11px] font-medium text-indigo-600 uppercase tracking-wider mt-0.5">Updated just now</p>
        </div>
      </div>
      
      <div className="relative z-10 space-y-3 flex-1 overflow-y-auto pr-1">
        <div className="bg-white/70 backdrop-blur-md border border-white/80 p-3.5 rounded-xl shadow-[0_4px_20px_-4px_rgba(79,70,229,0.05)]">
          <div className="flex items-center gap-2 mb-1.5">
            <BrainCircuit className="h-4 w-4 text-indigo-600" />
            <h4 className="font-semibold text-sm text-slate-800">Over-concentration Risk</h4>
          </div>
          <p className="text-sm text-slate-600 leading-relaxed">
            Your portfolio is highly concentrated in tech, with <strong className="text-slate-800">AAPL (28%)</strong> and <strong className="text-slate-800">MSFT (21%)</strong> making up nearly half of your assets. Consider diversifying into non-cyclical sectors.
          </p>
        </div>
        
        <div className="bg-white/70 backdrop-blur-md border border-white/80 p-3.5 rounded-xl shadow-[0_4px_20px_-4px_rgba(79,70,229,0.05)]">
          <div className="flex items-center gap-2 mb-1.5">
            <TrendingUp className="h-4 w-4 text-emerald-600" />
            <h4 className="font-semibold text-sm text-slate-800">Performance Insight</h4>
          </div>
          <p className="text-sm text-slate-600 leading-relaxed">
            <strong className="text-slate-800">NVDA</strong> is driving a disproportionate amount of unrealized gains (+42.5% ROI). 
            Meanwhile, <strong className="text-slate-800">TSLA</strong> and <strong className="text-slate-800">AMZN</strong> are dragging overall yield, contributing to $13k in paper losses.
          </p>
        </div>
      </div>
      
      <div className="relative z-10 mt-4 pt-4 border-t border-indigo-100/60 shrink-0">
        <div className="flex gap-2">
          <input 
            type="text" 
            placeholder="Ask AI about rebalancing..." 
            className="flex-1 bg-white/80 backdrop-blur-sm border border-indigo-100 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 transition-all placeholder:text-slate-400"
          />
          <button className="px-4 py-2 bg-indigo-600 text-white rounded-lg text-sm font-medium hover:bg-indigo-700 transition-colors shadow-sm flex items-center gap-1.5">
            Ask
            <ArrowUpRight className="h-3.5 w-3.5 opacity-70" />
          </button>
        </div>
      </div>
    </div>
  );
}

export default function TopNav() {
  return (
    <div className="h-screen w-full bg-slate-50/50 flex flex-col font-sans overflow-hidden">
      {/* Top Bar (48px) */}
      <header className="h-12 border-b border-slate-200 bg-white flex items-center justify-between px-4 shrink-0 shadow-sm z-20">
        <div className="flex items-center gap-8">
          <div className="flex items-center gap-2 text-indigo-600 font-bold text-lg tracking-tight">
            <LineChart className="h-5 w-5" />
            <span>Portfoli<span className="text-slate-800">AI</span></span>
          </div>
          <nav className="flex items-center gap-1.5">
            <button className="px-3 py-1.5 text-sm font-semibold bg-indigo-50 text-indigo-700 rounded-md flex items-center gap-1.5 transition-colors">
              <LayoutDashboard className="h-4 w-4" /> Overview
            </button>
            <button className="px-3 py-1.5 text-sm font-medium text-slate-600 hover:bg-slate-50 hover:text-slate-900 rounded-md flex items-center gap-1.5 transition-colors">
              <TrendingUp className="h-4 w-4" /> Performance
            </button>
            <button className="px-3 py-1.5 text-sm font-medium text-slate-600 hover:bg-slate-50 hover:text-slate-900 rounded-md flex items-center gap-1.5 transition-colors">
              <Upload className="h-4 w-4" /> Upload CSV
            </button>
            <button className="px-3 py-1.5 text-sm font-medium text-slate-600 hover:bg-slate-50 hover:text-slate-900 rounded-md flex items-center gap-1.5 transition-colors">
              <MessageSquare className="h-4 w-4" /> AI Chat
            </button>
          </nav>
        </div>
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-4 pr-5 border-r border-slate-200">
            <div className="text-right">
              <div className="text-[10px] text-slate-500 font-bold uppercase tracking-wider mb-0.5">Total Value</div>
              <div className="text-sm font-black text-slate-900 leading-none">$149,800</div>
            </div>
            <div className="flex items-center gap-0.5 text-emerald-700 bg-emerald-50 px-2 py-1 rounded-md text-xs font-bold border border-emerald-100">
              <ArrowUpRight className="h-3 w-3" />
              12.4%
            </div>
          </div>
          <button className="h-8 w-8 rounded-full bg-indigo-50 flex items-center justify-center text-indigo-600 border border-indigo-100 hover:bg-indigo-100 transition-colors">
            <User className="h-4 w-4" />
          </button>
        </div>
      </header>

      {/* Main Content Area */}
      <main className="flex-1 p-5 flex flex-col gap-5 overflow-hidden">
        {/* Top Row: KPIs */}
        <div className="grid grid-cols-3 gap-5 shrink-0">
          <KpiCard 
            title="Portfolio Value" 
            value="$149,800" 
            trend="+12.4%" 
            icon={<Wallet className="h-5 w-5" />} 
          />
          <KpiCard 
            title="Cost Basis" 
            value="$133,200" 
            subtext="All-time invested" 
            icon={<Activity className="h-5 w-5" />} 
          />
          <KpiCard 
            title="Unrealized P&L" 
            value="+$16,600" 
            trend="+12.4%" 
            icon={<TrendingUp className="h-5 w-5" />} 
          />
        </div>

        {/* Bottom Row: 60/40 Split */}
        <div className="flex gap-5 flex-1 min-h-0">
          {/* Left Column (60%) */}
          <div className="w-[60%] flex flex-col gap-5 min-w-0">
            {/* Allocation Chart */}
            <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-sm shrink-0 flex flex-col justify-center">
              <div className="flex items-center justify-between mb-2">
                <h3 className="font-semibold text-slate-800">Asset Allocation</h3>
                <span className="text-xs font-medium text-slate-500 bg-slate-100 px-2 py-1 rounded-md">By Current Value</span>
              </div>
              <div className="h-28">
                <DonutChart />
              </div>
            </div>
            
            {/* Holdings Table */}
            <div className="bg-white border border-slate-200 rounded-xl shadow-sm flex-1 min-h-0 flex flex-col overflow-hidden">
              <HoldingsTable />
            </div>
          </div>
          
          {/* Right Column (40%) */}
          <div className="w-[40%] min-w-0 h-full">
            <AiSummaryCard />
          </div>
        </div>
      </main>
    </div>
  );
}
