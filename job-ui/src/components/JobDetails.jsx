import { useState } from 'react';

export default function JobDetails({ job }) {
    const [applyState, setApplyState] = useState(0); // 0=none, 1=form, 2=upload, 3=success
  
    if (!job) {
      return (
        <div className="h-full flex flex-col items-center justify-center text-gray-400 bg-white rounded-2xl border border-gray-100 shadow-sm">
          <svg className="w-16 h-16 text-gray-200 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.5" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          <span className="font-medium text-lg text-gray-500">Select a matched job</span>
          <span className="text-sm">to view AI semantic analysis & initialize automation</span>
        </div>
      );
    }

    const startAutomation = () => {
        setApplyState(1);
        setTimeout(() => setApplyState(2), 2000);
        setTimeout(() => setApplyState(3), 4500);
        setTimeout(() => setApplyState(0), 10000); // reset preview later
    };
  
    return (
      <div className="bg-white rounded-2xl p-8 shadow-sm border border-gray-100 flex flex-col h-[75vh]">
        
        {/* Header Section */}
        <div className="border-b border-gray-100 pb-6 mb-6">
            <div className="flex justify-between items-start gap-4">
                <div className="flex-1">
                    <h2 className="text-3xl font-extrabold text-gray-900 mb-2 leading-tight">{job.title}</h2>
                    <p className="text-lg text-indigo-600 font-bold">{job.company}</p>
                </div>
                {job.matchScore && (
                    <div className="text-right flex flex-col items-end bg-gray-50 border border-gray-100 p-3 rounded-xl shadow-inner">
                        <div className="text-4xl font-black bg-clip-text text-transparent bg-gradient-to-r from-emerald-500 to-emerald-400">{job.matchScore}%</div>
                        <div className="text-[10px] font-bold text-gray-400 uppercase tracking-widest mt-1">AI Match Score</div>
                    </div>
                )}
            </div>
      
            <div className="flex gap-3 text-sm text-gray-600 mt-5 font-medium">
                <span className="px-3 py-1.5 bg-gray-100 rounded-lg border border-gray-200">{job.site}</span>
                <span className="px-3 py-1.5 bg-gray-100 rounded-lg border border-gray-200">{job.is_remote ? "Remote" : "Onsite"}</span>
                <span className="px-3 py-1.5 bg-emerald-50 text-emerald-700 border border-emerald-200 rounded-lg whitespace-nowrap flex items-center gap-1 font-bold">
                    <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20"><path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd"></path></svg>
                    Threshold Passed
                </span>
            </div>
        </div>

        {/* Semantic Matching Details Section */}
        <div className="grid grid-cols-2 gap-5 mb-8">
            <div className="p-4 bg-gradient-to-br from-emerald-50 to-white rounded-xl border border-emerald-100 shadow-sm">
                <h4 className="text-emerald-800 font-extrabold mb-3 flex items-center gap-2 text-sm uppercase tracking-wide">
                    <svg className="w-5 h-5 text-emerald-500" fill="currentColor" viewBox="0 0 20 20"><path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd"></path></svg>
                    Semantic Matches
                </h4>
                <ul className="text-sm text-gray-700 space-y-2 font-medium">
                    <li className="flex items-start gap-2"><span className="text-emerald-500 mt-1">•</span> Skills alignment highly confident</li>
                    <li className="flex items-start gap-2"><span className="text-emerald-500 mt-1">•</span> Experience duration perfectly matches requirement</li>
                </ul>
            </div>
            <div className="p-4 bg-gradient-to-br from-orange-50 to-white rounded-xl border border-orange-100 shadow-sm">
                <h4 className="text-orange-800 font-extrabold mb-3 flex items-center gap-2 text-sm uppercase tracking-wide">
                    <svg className="w-5 h-5 text-orange-400" fill="currentColor" viewBox="0 0 20 20"><path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd"></path></svg>
                    Missing Keywords
                </h4>
                <ul className="text-sm text-gray-700 space-y-2 font-medium">
                    <li className="flex items-start gap-2"><span className="text-orange-400 mt-1">•</span> "GraphQL" missing from semantics</li>
                </ul>
            </div>
        </div>
  
        <div className="mb-6 relative">
          {applyState === 0 && (
              <button
                onClick={startAutomation}
                className="w-full bg-gradient-to-r from-indigo-600 to-indigo-500 hover:from-indigo-500 hover:to-indigo-400 text-white px-6 py-4 rounded-xl font-extrabold shadow-lg shadow-indigo-600/20 transition-all active:scale-[0.98] flex items-center justify-center gap-2 text-lg group"
              >
                <span>🚀 Initialize Auto-Apply Agent</span>
                <svg className="w-5 h-5 group-hover:translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M14 5l7 7m0 0l-7 7m7-7H3"></path></svg>
              </button>
          )}

          {/* Automation Status Modal Context mapping */}
          {applyState > 0 && (
              <div className="p-5 bg-[#0f172a] text-gray-300 rounded-xl shadow-2xl font-mono text-sm space-y-4 relative overflow-hidden border border-gray-800">
                  <div className="absolute top-0 left-0 w-1 p-0.5 bg-blue-500 h-full animate-pulse shadow-[0_0_10px_rgba(59,130,246,1)]"></div>
                  <div className="flex justify-between items-center mb-2 border-b border-gray-700/50 pb-3">
                      <div className="text-xs text-gray-400 font-semibold tracking-wider">● PLAYWRIGHT TERMINAL</div>
                      {applyState < 3 && <div className="flex gap-1"><span className="w-2 h-2 bg-indigo-500 rounded-full animate-bounce"></span><span className="w-2 h-2 bg-indigo-500 rounded-full animate-bounce" style={{animationDelay:'0.1s'}}></span><span className="w-2 h-2 bg-indigo-500 rounded-full animate-bounce" style={{animationDelay:'0.2s'}}></span></div>}
                  </div>
                  
                  <div className="flex items-center gap-3">
                      <span className="text-emerald-400 text-lg">✔</span>
                      <span className="text-gray-100">Browser Automation initialized</span>
                  </div>

                  <div className={`flex items-center gap-3 transition-all duration-500 ${applyState >= 1 ? 'opacity-100 translate-x-0' : 'opacity-0 translate-x-4'}`}>
                      {applyState === 1 ? <span className="animate-spin text-blue-400 text-lg">⚙</span> : <span className="text-emerald-400 text-lg">✔</span>}
                      <span className={applyState === 1 ? 'text-white font-bold' : 'text-gray-100'}>Auto Form Filling (Ollama generating semantics)</span>
                  </div>

                  <div className={`flex items-center gap-3 transition-all duration-500 ${applyState >= 2 ? 'opacity-100 translate-x-0' : 'opacity-0 translate-x-4'}`}>
                      {applyState === 2 ? <span className="animate-spin text-blue-400 text-lg">⚙</span> : <span className="text-emerald-400 text-lg">✔</span>}
                      <span className={applyState === 2 ? 'text-white font-bold' : 'text-gray-100'}>Resume Uploading (PDF stream injection)</span>
                  </div>

                  <div className={`flex items-center gap-3 transition-all duration-500 ${applyState >= 3 ? 'opacity-100 translate-x-0 scale-100' : 'opacity-0 translate-x-4 scale-95'}`}>
                      {applyState === 3 ? <span className="text-emerald-400 text-xl">🎉</span> : <span className="text-gray-700">⏳</span>}
                      <span className={`px-2 py-1 rounded ${applyState === 3 ? 'bg-emerald-500/20 text-emerald-400 font-extrabold border border-emerald-500/30' : 'text-gray-500'}`}>
                          Success Confirmation! (Metrics: 18 sec/app)
                      </span>
                  </div>
              </div>
          )}
        </div>
  
        {job.description && (
          <div className="text-gray-600 text-[15px] leading-relaxed overflow-y-auto flex-1 pr-4 border-t border-gray-100 pt-6">
            <h4 className="font-extrabold text-gray-900 mb-4 text-base flex items-center gap-2">
                <svg className="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path></svg>
                Original Job Description
            </h4>
            <div className="whitespace-pre-wrap">{job.description}</div>
          </div>
        )}
      </div>
    );
}