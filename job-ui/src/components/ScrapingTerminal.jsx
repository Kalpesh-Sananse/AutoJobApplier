import React, { useState, useEffect } from 'react';

export default function ScrapingTerminal() {
  const [logs, setLogs] = useState([]);

  useEffect(() => {
    // Simulated sequence of events during a slow backend scraping process
    const sequence = [
      { text: "Initializing JobSpy distributed scraping engine workers...", delay: 200 },
      { text: "Bypassing anti-bot protections and solving CAPTCHAs...", delay: 1000 },
      { text: "Establishing connection to LinkedIn Jobs API...", delay: 1800 },
      { text: "Connecting to Indeed regional geo-proxies...", delay: 2500 },
      { text: "Scraping page 1 (Batch: 25 jobs captured)...", delay: 3500 },
      { text: "Scraping page 2 (Batch: 50 jobs captured)...", delay: 4800 },
      { text: "Warning: Rotating IP address to avoid rate-limits...", delay: 5800 },
      { text: "Scraping page 3 (Batch: 85 jobs captured)...", delay: 7200 },
      { text: "Aggregating job arrays and deduplicating entries...", delay: 8500 },
      { text: "Applying local LLM Threshold Filtering Models (Llama 3.2)...", delay: 9500 },
      { text: "Semantic analysis complete. Finalizing return payload...", delay: 11000 }
    ];

    const timeouts = sequence.map((s) => 
      setTimeout(() => setLogs(prev => [...prev, s.text]), s.delay)
    );

    return () => timeouts.forEach(clearTimeout);
  }, []);

  return (
    <div className="w-full max-w-5xl mx-auto bg-[#0a0f1c] p-6 rounded-2xl shadow-2xl border border-gray-800 font-mono text-sm relative mt-8 h-[400px] flex flex-col">
      <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-blue-500 via-emerald-500 to-purple-500 animate-pulse shadow-[0_0_15px_rgba(16,185,129,0.5)]"></div>
      
      {/* Mac window dots */}
      <div className="absolute top-4 left-4 flex gap-2">
         <div className="w-3 h-3 rounded-full bg-red-500/80 border border-red-600"></div>
         <div className="w-3 h-3 rounded-full bg-yellow-500/80 border border-yellow-600"></div>
         <div className="w-3 h-3 rounded-full bg-green-500/80 border border-green-600"></div>
      </div>
      
      <div className="text-gray-500 text-xs text-center border-b border-gray-800/80 pb-3 mt-1 tracking-[0.2em] font-bold uppercase drop-shadow-md">
        Backend Scraper Terminal
      </div>
      
      <div className="flex-1 overflow-y-auto space-y-3 mt-4 flex flex-col justify-end">
        {logs.map((log, i) => (
          <div key={i} className="flex gap-3 text-gray-300">
            <span className="text-emerald-500 font-bold shrink-0">➜</span>
            <span className="text-blue-400 font-bold shrink-0">[JobSpy_Worker]</span>
            <span className={log.includes("Warning") ? "text-orange-400 font-bold" : "text-gray-200"}>{log}</span>
          </div>
        ))}
        <div className="flex gap-3 text-gray-300 mt-2">
          <span className="text-emerald-500 font-bold">➜</span>
          <span className="text-green-400 font-bold animate-pulse text-xl leading-none">█</span>
        </div>
      </div>
    </div>
  );
}
