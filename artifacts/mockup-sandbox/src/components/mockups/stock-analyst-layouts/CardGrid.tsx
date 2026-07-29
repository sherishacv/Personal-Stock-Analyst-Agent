import React from "react";
import { 
  Upload, 
  TrendingUp, 
  TrendingDown, 
  RefreshCcw, 
  Bot,
  PieChart,
  BarChart3,
  DollarSign,
  Activity,
  Briefcase
} from "lucide-react";

export default function CardGrid() {
  return (
    <div className="min-h-screen bg-[#F9F8F6] text-slate-900 font-sans p-6 overflow-y-auto">
      <div className="max-w-[1400px] mx-auto space-y-6 pb-12">
        
        {/* Row 1: Top bar */}
        <div className="flex items-center justify-between bg-white rounded-xl shadow-sm border border-slate-200/60 p-4 px-6">
          <div className="flex items-center gap-3">
            <div className="bg-slate-900 text-white p-2 rounded-lg">
              <Briefcase className="w-5 h-5" />
            </div>
            <div>
              <h1 className="font-semibold text-lg leading-tight tracking-tight">Portfolio Analyst</h1>
              <p className="text-sm text-slate-500 leading-tight">Portfolio loaded · 6 tickers · 38 transactions</p>
            </div>
          </div>
          <button className="flex items-center gap-2 bg-slate-900 hover:bg-slate-800 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors">
            <Upload className="w-4 h-4" />
            Upload New
          </button>
        </div>

        {/* Row 2: 4 KPI Cards */}
        <div className="grid grid-cols-4 gap-6">
          <div className="bg-white rounded-xl shadow-sm border border-slate-200/60 p-6 flex flex-col justify-between">
            <div className="flex items-center gap-2 text-slate-500 mb-2">
              <DollarSign className="w-4 h-4" />
              <h2 className="text-sm font-medium">Portfolio Value</h2>
            </div>
            <div className="text-3xl font-semibold tracking-tight">$149,800</div>
          </div>
          
          <div className="bg-white rounded-xl shadow-sm border border-slate-200/60 p-6 flex flex-col justify-between">
            <div className="flex items-center gap-2 text-slate-500 mb-2">
              <Activity className="w-4 h-4" />
              <h2 className="text-sm font-medium">Cost Basis</h2>
            </div>
            <div className="text-3xl font-semibold tracking-tight">$95,000</div>
          </div>
          
          <div className="bg-white rounded-xl shadow-sm border border-slate-200/60 p-6 flex flex-col justify-between">
            <div className="flex items-center gap-2 text-slate-500 mb-2">
              <TrendingUp className="w-4 h-4 text-emerald-600" />
              <h2 className="text-sm font-medium">Unrealized P&L</h2>
            </div>
            <div className="text-3xl font-semibold tracking-tight text-emerald-600">+$54,800</div>
            <p className="text-sm text-emerald-600 mt-1 font-medium">+57.6%</p>
          </div>

          <div className="bg-white rounded-xl shadow-sm border border-slate-200/60 p-6 flex flex-col justify-between">
            <div className="flex items-center gap-2 text-slate-500 mb-2">
              <BarChart3 className="w-4 h-4 text-emerald-600" />
              <h2 className="text-sm font-medium">XIRR (Annualized)</h2>
            </div>
            <div className="text-3xl font-semibold tracking-tight text-emerald-600">+24.5%</div>
            <p className="text-sm text-slate-500 mt-1">Since Jan 2022</p>
          </div>
        </div>

        {/* Row 3: Donut (45%) + Holdings Table (55%) */}
        <div className="grid grid-cols-12 gap-6">
          
          {/* Donut Chart Card */}
          <div className="col-span-5 bg-white rounded-xl shadow-sm border border-slate-200/60 p-6 flex flex-col">
            <div className="flex items-center gap-2 text-slate-800 mb-6">
              <PieChart className="w-5 h-5 text-slate-400" />
              <h2 className="text-base font-semibold">Allocation</h2>
            </div>
            <div className="flex-1 flex items-center justify-center relative min-h-[220px]">
              {/* Fake Donut Chart SVG */}
              <svg viewBox="0 0 100 100" className="w-48 h-48 transform -rotate-90">
                {/* AMZN 9% */}
                <circle cx="50" cy="50" r="40" fill="transparent" stroke="#f1f5f9" strokeWidth="20" />
                <circle cx="50" cy="50" r="40" fill="transparent" stroke="#f43f5e" strokeWidth="20" strokeDasharray="56.5 251.2" strokeDashoffset="0" />
                {/* TSLA 10% */}
                <circle cx="50" cy="50" r="40" fill="transparent" stroke="#d946ef" strokeWidth="20" strokeDasharray="62.8 251.2" strokeDashoffset="-56.5" />
                {/* GOOGL 13% */}
                <circle cx="50" cy="50" r="40" fill="transparent" stroke="#8b5cf6" strokeWidth="20" strokeDasharray="81.6 251.2" strokeDashoffset="-119.3" />
                {/* NVDA 19% */}
                <circle cx="50" cy="50" r="40" fill="transparent" stroke="#3b82f6" strokeWidth="20" strokeDasharray="119.3 251.2" strokeDashoffset="-200.9" />
                {/* MSFT 21% */}
                <circle cx="50" cy="50" r="40" fill="transparent" stroke="#0ea5e9" strokeWidth="20" strokeDasharray="131.9 251.2" strokeDashoffset="-320.2" />
                {/* AAPL 28% */}
                <circle cx="50" cy="50" r="40" fill="transparent" stroke="#10b981" strokeWidth="20" strokeDasharray="175.8 251.2" strokeDashoffset="-452.1" />
              </svg>
              {/* Center Text */}
              <div className="absolute inset-0 flex flex-col items-center justify-center">
                <span className="text-2xl font-semibold tracking-tight text-slate-800">6</span>
                <span className="text-xs font-medium text-slate-500 uppercase tracking-wider">Tickers</span>
              </div>
            </div>
            
            <div className="flex flex-wrap gap-x-4 gap-y-2 justify-center mt-6 text-sm">
              <div className="flex items-center gap-1.5"><div className="w-2.5 h-2.5 rounded-full bg-[#10b981]"></div><span className="font-medium">AAPL</span><span className="text-slate-500">28%</span></div>
              <div className="flex items-center gap-1.5"><div className="w-2.5 h-2.5 rounded-full bg-[#0ea5e9]"></div><span className="font-medium">MSFT</span><span className="text-slate-500">21%</span></div>
              <div className="flex items-center gap-1.5"><div className="w-2.5 h-2.5 rounded-full bg-[#3b82f6]"></div><span className="font-medium">NVDA</span><span className="text-slate-500">19%</span></div>
              <div className="flex items-center gap-1.5"><div className="w-2.5 h-2.5 rounded-full bg-[#8b5cf6]"></div><span className="font-medium">GOOGL</span><span className="text-slate-500">13%</span></div>
              <div className="flex items-center gap-1.5"><div className="w-2.5 h-2.5 rounded-full bg-[#d946ef]"></div><span className="font-medium">TSLA</span><span className="text-slate-500">10%</span></div>
              <div className="flex items-center gap-1.5"><div className="w-2.5 h-2.5 rounded-full bg-[#f43f5e]"></div><span className="font-medium">AMZN</span><span className="text-slate-500">9%</span></div>
            </div>
          </div>

          {/* Holdings Table */}
          <div className="col-span-7 bg-white rounded-xl shadow-sm border border-slate-200/60 p-6 flex flex-col">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-2 text-slate-800">
                <Briefcase className="w-5 h-5 text-slate-400" />
                <h2 className="text-base font-semibold">Holdings</h2>
              </div>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full text-left text-sm whitespace-nowrap">
                <thead>
                  <tr className="border-b border-slate-100 text-slate-500">
                    <th className="pb-3 font-medium">Ticker</th>
                    <th className="pb-3 font-medium text-right">Shares</th>
                    <th className="pb-3 font-medium text-right">Avg Cost</th>
                    <th className="pb-3 font-medium text-right">Market Value</th>
                    <th className="pb-3 font-medium text-right">Unrealized P&L</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-50">
                  <tr className="hover:bg-slate-50/50 transition-colors">
                    <td className="py-3 font-medium text-slate-900">AAPL</td>
                    <td className="py-3 text-right">245.5</td>
                    <td className="py-3 text-right text-slate-600">$120.40</td>
                    <td className="py-3 text-right font-medium">$42,300</td>
                    <td className="py-3 text-right text-emerald-600 font-medium">+$12,740 (+43%)</td>
                  </tr>
                  <tr className="hover:bg-slate-50/50 transition-colors">
                    <td className="py-3 font-medium text-slate-900">MSFT</td>
                    <td className="py-3 text-right">82.3</td>
                    <td className="py-3 text-right text-slate-600">$215.50</td>
                    <td className="py-3 text-right font-medium">$31,100</td>
                    <td className="py-3 text-right text-emerald-600 font-medium">+$13,363 (+75%)</td>
                  </tr>
                  <tr className="hover:bg-slate-50/50 transition-colors">
                    <td className="py-3 font-medium text-slate-900">NVDA</td>
                    <td className="py-3 text-right">31.2</td>
                    <td className="py-3 text-right text-slate-600">$185.00</td>
                    <td className="py-3 text-right font-medium">$28,500</td>
                    <td className="py-3 text-right text-emerald-600 font-medium">+$22,728 (+393%)</td>
                  </tr>
                  <tr className="hover:bg-slate-50/50 transition-colors">
                    <td className="py-3 font-medium text-slate-900">GOOGL</td>
                    <td className="py-3 text-right">135.0</td>
                    <td className="py-3 text-right text-slate-600">$105.20</td>
                    <td className="py-3 text-right font-medium">$19,800</td>
                    <td className="py-3 text-right text-emerald-600 font-medium">+$5,598 (+39%)</td>
                  </tr>
                  <tr className="hover:bg-slate-50/50 transition-colors">
                    <td className="py-3 font-medium text-slate-900">TSLA</td>
                    <td className="py-3 text-right">85.0</td>
                    <td className="py-3 text-right text-slate-600">$210.00</td>
                    <td className="py-3 text-right font-medium">$15,200</td>
                    <td className="py-3 text-right text-rose-600 font-medium">-$2,650 (-15%)</td>
                  </tr>
                  <tr className="hover:bg-slate-50/50 transition-colors">
                    <td className="py-3 font-medium text-slate-900">AMZN</td>
                    <td className="py-3 text-right">72.0</td>
                    <td className="py-3 text-right text-slate-600">$138.50</td>
                    <td className="py-3 text-right font-medium">$12,900</td>
                    <td className="py-3 text-right text-emerald-600 font-medium">+$2,928 (+29%)</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>

        {/* Row 4: Bar Chart (60%) + AI Summary (40%) */}
        <div className="grid grid-cols-12 gap-6">
          
          {/* Bar Chart */}
          <div className="col-span-7 bg-white rounded-xl shadow-sm border border-slate-200/60 p-6">
            <div className="flex items-center justify-between mb-6">
              <div className="flex items-center gap-2 text-slate-800">
                <BarChart3 className="w-5 h-5 text-slate-400" />
                <h2 className="text-base font-semibold">P&L by Asset</h2>
              </div>
              <span className="text-xs font-medium text-slate-500 bg-slate-100 px-2 py-1 rounded">Unrealized $</span>
            </div>
            
            <div className="space-y-4">
              {/* NVDA */}
              <div>
                <div className="flex justify-between text-sm mb-1.5">
                  <span className="font-medium">NVDA</span>
                  <span className="text-emerald-600 font-medium">+$22,728</span>
                </div>
                <div className="w-full bg-slate-100 h-2.5 rounded-full overflow-hidden flex">
                  <div className="bg-slate-100 w-1/4"></div>
                  <div className="bg-emerald-500 h-full w-[60%] rounded-full"></div>
                </div>
              </div>
              {/* MSFT */}
              <div>
                <div className="flex justify-between text-sm mb-1.5">
                  <span className="font-medium">MSFT</span>
                  <span className="text-emerald-600 font-medium">+$13,363</span>
                </div>
                <div className="w-full bg-slate-100 h-2.5 rounded-full overflow-hidden flex">
                  <div className="bg-slate-100 w-1/4"></div>
                  <div className="bg-emerald-500 h-full w-[35%] rounded-full"></div>
                </div>
              </div>
              {/* AAPL */}
              <div>
                <div className="flex justify-between text-sm mb-1.5">
                  <span className="font-medium">AAPL</span>
                  <span className="text-emerald-600 font-medium">+$12,740</span>
                </div>
                <div className="w-full bg-slate-100 h-2.5 rounded-full overflow-hidden flex">
                  <div className="bg-slate-100 w-1/4"></div>
                  <div className="bg-emerald-500 h-full w-[33%] rounded-full"></div>
                </div>
              </div>
              {/* GOOGL */}
              <div>
                <div className="flex justify-between text-sm mb-1.5">
                  <span className="font-medium">GOOGL</span>
                  <span className="text-emerald-600 font-medium">+$5,598</span>
                </div>
                <div className="w-full bg-slate-100 h-2.5 rounded-full overflow-hidden flex">
                  <div className="bg-slate-100 w-1/4"></div>
                  <div className="bg-emerald-500 h-full w-[15%] rounded-full"></div>
                </div>
              </div>
              {/* AMZN */}
              <div>
                <div className="flex justify-between text-sm mb-1.5">
                  <span className="font-medium">AMZN</span>
                  <span className="text-emerald-600 font-medium">+$2,928</span>
                </div>
                <div className="w-full bg-slate-100 h-2.5 rounded-full overflow-hidden flex">
                  <div className="bg-slate-100 w-1/4"></div>
                  <div className="bg-emerald-500 h-full w-[8%] rounded-full"></div>
                </div>
              </div>
              {/* TSLA */}
              <div>
                <div className="flex justify-between text-sm mb-1.5">
                  <span className="font-medium">TSLA</span>
                  <span className="text-rose-600 font-medium">-$2,650</span>
                </div>
                <div className="w-full bg-slate-100 h-2.5 rounded-full overflow-hidden flex relative">
                  <div className="bg-rose-500 h-full w-[7%] absolute right-[75%] rounded-full"></div>
                  <div className="w-1/4 border-r-2 border-white/50 h-full absolute left-0 z-10"></div>
                </div>
              </div>
            </div>
          </div>

          {/* AI Summary */}
          <div className="col-span-5 bg-gradient-to-b from-orange-50 to-white rounded-xl shadow-sm border border-orange-100 p-6 flex flex-col">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-2">
                <div className="bg-orange-500 text-white p-1.5 rounded-md">
                  <Bot className="w-4 h-4" />
                </div>
                <h2 className="text-base font-semibold text-orange-950">AI Analysis</h2>
                <span className="text-[10px] font-bold text-orange-600 bg-orange-100 px-1.5 py-0.5 rounded tracking-wide uppercase ml-1">Groq</span>
              </div>
              <button className="text-slate-400 hover:text-slate-600 transition-colors p-1">
                <RefreshCcw className="w-4 h-4" />
              </button>
            </div>
            
            <div className="flex-1 flex flex-col gap-4 text-sm text-slate-700 leading-relaxed">
              <p>
                Your portfolio is heavily concentrated in <strong>Tech (85%)</strong>, with <span className="font-semibold text-emerald-700">NVDA</span> driving the majority of your outsized returns (+393%). 
              </p>
              <p>
                While your 24.5% XIRR outperforms the S&P 500, your high allocation to <span className="font-semibold text-slate-900">AAPL</span> and <span className="font-semibold text-slate-900">MSFT</span> (49% combined) reduces diversification. <span className="font-semibold text-rose-700">TSLA</span> is your only lagging position.
              </p>
              <p>
                <strong>Recommendation:</strong> Consider rebalancing by trimming NVDA to lock in gains and adding non-tech dividend players to reduce volatility.
              </p>
            </div>
          </div>

        </div>
      </div>
    </div>
  );
}
