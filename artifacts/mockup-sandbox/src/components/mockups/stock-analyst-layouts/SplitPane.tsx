import React from 'react';
import { 
  MessageSquare, 
  TrendingUp, 
  Settings, 
  Upload, 
  Sparkles,
  ArrowUpRight,
  Activity
} from 'lucide-react';

export default function SplitPane() {
  return (
    <div className="w-[1519px] h-[738px] bg-slate-50 flex flex-col font-sans overflow-hidden text-slate-900">
       {/* Top Bar - 40px */}
       <header className="h-[40px] shrink-0 bg-slate-950 text-slate-300 flex items-center justify-between px-4 border-b border-slate-800 text-sm">
         <div className="flex items-center gap-2 font-medium text-white">
           <Activity className="w-4 h-4 text-indigo-400" />
           <span>Portfolio Analyst</span>
         </div>
         <div className="flex items-center gap-2 text-slate-400">
           <span>6 holdings</span>
           <span>·</span>
           <span className="text-white font-medium">$149,800.00</span>
           <span className="text-emerald-400 text-xs ml-1 flex items-center"><ArrowUpRight className="w-3 h-3 mr-0.5" /> 12.4%</span>
         </div>
         <div className="flex items-center gap-4">
           <button className="hover:text-white transition-colors flex items-center gap-1.5"><MessageSquare className="w-4 h-4" /> <span className="text-xs">AI Chat</span></button>
           <button className="hover:text-white transition-colors flex items-center gap-1.5"><TrendingUp className="w-4 h-4" /> <span className="text-xs">Performance</span></button>
           <div className="w-px h-4 bg-slate-800 mx-1"></div>
           <button className="hover:text-white transition-colors"><Settings className="w-4 h-4" /></button>
         </div>
       </header>

       {/* Main Split Content */}
       <div className="flex flex-1 min-h-0">
         
         {/* Left Sidebar - 280px */}
         <aside className="w-[280px] shrink-0 bg-slate-900 flex flex-col border-r border-slate-800 z-10">
           <div className="p-4 text-xs font-semibold text-slate-400 uppercase tracking-wider flex justify-between items-center border-b border-slate-800">
             Holdings
             <button className="text-slate-400 hover:text-white transition-colors" title="Upload CSV"><Upload className="w-4 h-4" /></button>
           </div>
           
           <div className="flex-1 overflow-y-auto p-2 space-y-1 custom-scrollbar">
             {/* Holding Items */}
             {holdings.map((h) => (
               <button 
                 key={h.ticker}
                 className={`w-full flex flex-col p-3 rounded-lg text-left transition-colors relative overflow-hidden group ${
                   h.selected 
                     ? 'bg-indigo-500/15 border border-indigo-500/30 text-white shadow-[inset_2px_0_0_0_#6366f1]' 
                     : 'hover:bg-slate-800/80 text-slate-300 border border-transparent'
                 }`}
               >
                 <div className="flex justify-between items-baseline w-full">
                   <span className={`font-semibold tracking-tight ${h.selected ? 'text-indigo-300' : 'text-slate-200 group-hover:text-white'}`}>{h.ticker}</span>
                   <span className={`text-sm ${h.selected ? 'text-white' : 'text-slate-300 group-hover:text-white'}`}>{h.value}</span>
                 </div>
                 <div className="flex justify-between items-center mt-2 w-full gap-3">
                   <div className="flex items-center gap-2 flex-1">
                     <div className="h-1.5 flex-1 bg-slate-800 rounded-full overflow-hidden">
                       <div className={`h-full ${h.selected ? 'bg-indigo-500' : 'bg-slate-600 group-hover:bg-slate-500'}`} style={{ width: h.alloc }} />
                     </div>
                     <span className="text-[10px] text-slate-500 font-medium w-6">{h.alloc}</span>
                   </div>
                   <span className={`text-[11px] font-medium flex items-center px-1.5 py-0.5 rounded ${
                     h.pl > 0 
                       ? (h.selected ? 'bg-emerald-500/20 text-emerald-400' : 'bg-emerald-500/10 text-emerald-400') 
                       : (h.selected ? 'bg-rose-500/20 text-rose-400' : 'bg-rose-500/10 text-rose-400')
                   }`}>
                     {h.pl > 0 ? '+' : ''}{h.pl}%
                   </span>
                 </div>
               </button>
             ))}
           </div>

           <div className="p-5 bg-slate-950 border-t border-slate-800 mt-auto">
             <div className="text-xs font-medium text-slate-500 mb-1.5">Portfolio Value</div>
             <div className="text-2xl font-bold text-white tracking-tight">$149,800.00</div>
             <div className="text-sm font-medium text-emerald-400 flex items-center mt-1">
               <ArrowUpRight className="w-3.5 h-3.5 mr-1" />
               +$16,532.40 (12.4%) All Time
             </div>
           </div>
         </aside>

         {/* Right Detail Panel */}
         <main className="flex-1 bg-slate-50 flex flex-col min-w-0">
           {/* Detail Header */}
           <div className="px-8 py-6 border-b border-slate-200 flex justify-between items-end bg-white shrink-0">
             <div>
               <div className="flex items-center gap-3 mb-2">
                 <h1 className="text-3xl font-bold text-slate-900 tracking-tight">AAPL</h1>
                 <span className="text-lg text-slate-500 font-medium">Apple Inc.</span>
               </div>
               <div className="flex items-baseline gap-3">
                 <span className="text-3xl font-bold text-slate-800 tracking-tight">$178.42</span>
                 <span className="text-emerald-700 font-semibold flex items-center bg-emerald-50 px-2.5 py-1 rounded-md text-sm border border-emerald-200/60 shadow-sm">
                   <ArrowUpRight className="w-4 h-4 mr-1 stroke-[2.5]" />
                   +2.3% today
                 </span>
               </div>
             </div>
             
             <div className="flex gap-3">
               <button className="px-4 py-2 text-sm font-semibold border border-slate-200 rounded-lg shadow-sm hover:bg-slate-50 text-slate-700 transition-colors">Trade</button>
               <button className="px-4 py-2 text-sm font-semibold bg-indigo-600 text-white rounded-lg shadow-sm hover:bg-indigo-700 transition-colors">Analyze</button>
             </div>
           </div>

           {/* Metrics Row */}
           <div className="grid grid-cols-4 border-b border-slate-200 divide-x divide-slate-200 bg-white shrink-0 shadow-[0_1px_2px_rgba(0,0,0,0.02)]">
             <div className="p-6">
               <div className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2">Shares Held</div>
               <div className="text-2xl font-bold text-slate-900 tracking-tight">237.08</div>
             </div>
             <div className="p-6">
               <div className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2">Avg Cost</div>
               <div className="text-2xl font-bold text-slate-900 tracking-tight">$124.50</div>
             </div>
             <div className="p-6">
               <div className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2">Unrealized P&L</div>
               <div className="text-2xl font-bold text-emerald-600 tracking-tight">+$12,783.28</div>
             </div>
             <div className="p-6">
               <div className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2">Portfolio Weight</div>
               <div className="text-2xl font-bold text-slate-900 tracking-tight">28.2%</div>
             </div>
           </div>

           {/* Main Content Area: Charts & Data */}
           <div className="flex-1 p-8 flex gap-8 min-h-0 overflow-y-auto">
             {/* Left Column: Chart */}
             <div className="flex-1 flex flex-col min-w-0">
               <div className="flex items-center justify-between mb-4">
                 <h3 className="text-base font-semibold text-slate-900">60-Day Trend</h3>
                 <div className="flex bg-slate-100 p-0.5 rounded-md border border-slate-200">
                   {['1W', '1M', '3M', '1Y', 'ALL'].map((tf) => (
                     <button key={tf} className={`px-3 py-1 text-xs font-semibold rounded ${tf === '3M' ? 'bg-white text-indigo-700 shadow-sm border border-slate-200/50' : 'text-slate-500 hover:text-slate-700'}`}>
                       {tf}
                     </button>
                   ))}
                 </div>
               </div>
               
               <div className="flex-1 min-h-[200px] border border-slate-200 rounded-xl bg-white p-6 relative overflow-hidden group shadow-sm flex flex-col">
                 {/* Fake Grid */}
                 <div className="absolute inset-0 grid grid-cols-6 grid-rows-5 gap-0 opacity-[0.02] pointer-events-none">
                   {Array.from({length: 30}).map((_, i) => (
                     <div key={i} className="border-r border-b border-slate-900"></div>
                   ))}
                 </div>
                 
                 {/* Fake Sparkline Container */}
                 <div className="flex-1 relative mt-2 mb-4 w-full h-full">
                   <svg className="w-full h-full text-indigo-500 drop-shadow-md absolute inset-0" viewBox="0 0 600 200" preserveAspectRatio="none">
                     <defs>
                       <linearGradient id="chartGradient" x1="0%" y1="0%" x2="0%" y2="100%">
                         <stop offset="0%" stopColor="currentColor" stopOpacity="0.15" />
                         <stop offset="100%" stopColor="currentColor" stopOpacity="0" />
                       </linearGradient>
                     </defs>
                     <path d="M0,160 C30,140 60,180 90,170 C120,160 150,100 180,110 C210,120 240,60 270,80 C300,100 330,40 360,50 C390,60 420,20 450,30 C480,40 510,10 540,20 C570,30 600,0 600,0 L600,200 L0,200 Z" fill="url(#chartGradient)" />
                     <path d="M0,160 C30,140 60,180 90,170 C120,160 150,100 180,110 C210,120 240,60 270,80 C300,100 330,40 360,50 C390,60 420,20 450,30 C480,40 510,10 540,20 C570,30 600,0 600,0" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round" />
                     
                     {/* Current price indicator */}
                     <circle cx="600" cy="0" r="5" fill="white" stroke="currentColor" strokeWidth="3" className="text-indigo-600" />
                     <circle cx="600" cy="0" r="16" fill="currentColor" className="text-indigo-600 opacity-10 animate-ping" />
                   </svg>

                   {/* Y Axis Labels */}
                   <div className="absolute right-0 top-0 bottom-0 flex flex-col justify-between text-[11px] text-slate-400 font-mono text-right pointer-events-none translate-x-12">
                     <span>$185</span>
                     <span>$165</span>
                     <span>$145</span>
                     <span>$125</span>
                   </div>
                 </div>
               </div>
             </div>

             {/* Right Column: Allocation & Activity */}
             <div className="w-[340px] flex flex-col gap-6 shrink-0">
               <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-sm">
                 <h3 className="text-sm font-semibold text-slate-900 mb-5">Portfolio Allocation</h3>
                 <div className="flex items-center gap-6">
                   <div className="relative w-28 h-28 shrink-0">
                     {/* Fake Donut Chart SVG */}
                     <svg viewBox="0 0 100 100" className="w-full h-full -rotate-90">
                       {/* Others - 72% */}
                       <circle cx="50" cy="50" r="38" fill="transparent" stroke="#f1f5f9" strokeWidth="18" />
                       {/* AAPL - 28% */}
                       <circle cx="50" cy="50" r="38" fill="transparent" stroke="#6366f1" strokeWidth="22" strokeDasharray="175 251.2" className="drop-shadow-sm" strokeLinecap="round" />
                     </svg>
                     <div className="absolute inset-0 flex flex-col items-center justify-center">
                       <span className="text-2xl font-bold text-slate-900 tracking-tight">28%</span>
                       <span className="text-[11px] text-slate-500 font-semibold uppercase tracking-wider">AAPL</span>
                     </div>
                   </div>
                   <div className="flex flex-col gap-3 flex-1">
                     <div className="flex items-center justify-between text-sm">
                       <div className="flex items-center gap-2">
                         <div className="w-3 h-3 rounded bg-indigo-500 shadow-sm shadow-indigo-500/20"></div>
                         <span className="font-semibold text-slate-900">AAPL</span>
                       </div>
                       <span className="text-slate-600 font-medium">$42.3k</span>
                     </div>
                     <div className="flex items-center justify-between text-sm">
                       <div className="flex items-center gap-2">
                         <div className="w-3 h-3 rounded bg-slate-200"></div>
                         <span className="font-medium text-slate-600">Others</span>
                       </div>
                       <span className="text-slate-600 font-medium">$107.5k</span>
                     </div>
                   </div>
                 </div>
               </div>

               <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-sm flex-1">
                 <h3 className="text-sm font-semibold text-slate-900 mb-4">Recent Transactions</h3>
                 <div className="space-y-4">
                   <div className="flex justify-between items-center pb-4 border-b border-slate-100">
                     <div>
                       <div className="text-sm font-semibold text-slate-900">Buy AAPL</div>
                       <div className="text-xs text-slate-500 font-medium mt-0.5">Oct 12, 2023</div>
                     </div>
                     <div className="text-right">
                       <div className="text-sm font-bold text-slate-900">50 sh</div>
                       <div className="text-xs text-slate-500 font-medium mt-0.5">$173.20/sh</div>
                     </div>
                   </div>
                   <div className="flex justify-between items-center pb-4 border-b border-slate-100">
                     <div>
                       <div className="text-sm font-semibold text-slate-900">Dividend</div>
                       <div className="text-xs text-slate-500 font-medium mt-0.5">Aug 17, 2023</div>
                     </div>
                     <div className="text-right">
                       <div className="text-sm font-bold text-emerald-600">+$44.90</div>
                       <div className="text-xs text-slate-500 font-medium mt-0.5">Reinvested</div>
                     </div>
                   </div>
                   <div className="flex justify-between items-center">
                     <div>
                       <div className="text-sm font-semibold text-slate-900">Buy AAPL</div>
                       <div className="text-xs text-slate-500 font-medium mt-0.5">Jan 04, 2023</div>
                     </div>
                     <div className="text-right">
                       <div className="text-sm font-bold text-slate-900">187.08 sh</div>
                       <div className="text-xs text-slate-500 font-medium mt-0.5">$125.07/sh</div>
                     </div>
                   </div>
                 </div>
               </div>
             </div>
           </div>

           {/* AI Insight Strip */}
           <div className="mx-8 mb-8 mt-0 p-5 bg-amber-50/80 border border-amber-200/60 rounded-xl flex items-start gap-4 shadow-sm shrink-0">
             <div className="p-2 bg-amber-100/80 rounded-lg text-amber-600 shrink-0 mt-0.5 shadow-sm border border-amber-200/50">
               <Sparkles className="w-5 h-5" />
             </div>
             <div>
               <h4 className="text-sm font-bold text-amber-900 mb-1">AI Insight</h4>
               <p className="text-sm text-amber-800/90 leading-relaxed font-medium">
                 AAPL represents your largest single-stock exposure at 28.2%. Your cost basis of $124.50 is highly favorable compared to current levels. Given the upcoming earnings report in 2 weeks, you might consider writing covered calls against a portion of your position to generate yield while protecting unrealized gains.
               </p>
             </div>
           </div>
           
         </main>
       </div>
    </div>
  );
}

const holdings = [
  { ticker: 'AAPL', value: '$42,300', alloc: '28%', pl: 43.3, selected: true },
  { ticker: 'MSFT', value: '$31,100', alloc: '21%', pl: 12.8, selected: false },
  { ticker: 'NVDA', value: '$28,500', alloc: '19%', pl: 145.2, selected: false },
  { ticker: 'GOOGL', value: '$19,800', alloc: '13%', pl: -2.4, selected: false },
  { ticker: 'TSLA', value: '$15,200', alloc: '10%', pl: 5.1, selected: false },
  { ticker: 'AMZN', value: '$12,900', alloc: '9%', pl: 8.7, selected: false },
];
