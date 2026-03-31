export default function JobDetails({ job }) {
  if (!job) {
    return (
      <div className="glass-card h-full min-h-[65vh] flex flex-col items-center justify-center text-center p-8">
        <div className="text-6xl mb-4 animate-float">💼</div>
        <h3 className="text-lg font-semibold text-slate-300 mb-2">No Job Selected</h3>
        <p className="text-sm text-slate-500 max-w-xs">
          Click on a job listing from the panel to view its full details and apply.
        </p>
      </div>
    );
  }

  return (
    <div className="glass-card gradient-border p-6 md:p-8 animate-fadeInUp min-h-[65vh]">
      {/* Header */}
      <div className="mb-6">
        <div className="flex items-start justify-between gap-4 mb-3">
          <h2 className="text-2xl font-bold text-slate-100 leading-tight">{job.title}</h2>
          <span className="badge badge-easy-apply flex-shrink-0 mt-1">⚡ Easy Apply</span>
        </div>

        <p className="text-base text-slate-400 font-medium">{job.company}</p>

        <div className="flex flex-wrap items-center gap-2 mt-3">
          <span className={`badge ${job.is_remote ? 'badge-remote' : 'badge-onsite'}`}>
            {job.is_remote ? "🌍 Remote" : "📍 Onsite"}
          </span>
          <span className="badge badge-site">{job.site}</span>
          {job.date_posted && (
            <span className="text-xs text-slate-500">Posted: {job.date_posted}</span>
          )}
        </div>
      </div>

      {/* Action Buttons */}
      <div className="flex flex-wrap gap-3 mb-6">
        <a
          href={job.job_url}
          target="_blank"
          rel="noreferrer"
          className="btn-primary flex items-center gap-2"
        >
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M15 3h4a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2h-4" />
            <polyline points="10 17 15 12 10 7" />
            <line x1="15" y1="12" x2="3" y2="12" />
          </svg>
          Apply Now
        </a>

        <button className="glass-card glass-card-hover px-5 py-3 text-sm font-semibold text-slate-300 flex items-center gap-2">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M19 21l-7-5-7 5V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2z" />
          </svg>
          Save Job
        </button>

        <button className="glass-card glass-card-hover px-5 py-3 text-sm font-semibold text-emerald-400 flex items-center gap-2">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14" />
            <polyline points="22 4 12 14.01 9 11.01" />
          </svg>
          Auto Apply
        </button>
      </div>

      {/* Divider */}
      <div className="h-px bg-gradient-to-r from-transparent via-white/10 to-transparent mb-6"></div>

      {/* Description */}
      {job.description && (
        <div>
          <h3 className="text-sm font-semibold text-slate-400 uppercase tracking-wider mb-3">Job Description</h3>
          <div className="text-sm text-slate-300 leading-relaxed max-h-[350px] overflow-y-auto pr-2 whitespace-pre-line">
            {job.description}
          </div>
        </div>
      )}
    </div>
  );
}