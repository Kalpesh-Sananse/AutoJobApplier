export default function JobListItem({ job, isSelected, onClick }) {
  return (
    <div
      onClick={onClick}
      className={`glass-card glass-card-hover cursor-pointer p-4 transition-all duration-300 ${isSelected
          ? "!border-blue-500/40 !bg-blue-500/10 shadow-lg shadow-blue-500/5"
          : ""
        }`}
    >
      <div className="flex items-start justify-between gap-2">
        <div className="min-w-0 flex-1">
          <h3 className="font-semibold text-sm text-slate-100 truncate leading-snug">
            {job.title}
          </h3>
          <p className="text-xs text-slate-400 mt-0.5 truncate">{job.company}</p>
        </div>

        {/* Site icon */}
        <div className="flex-shrink-0 mt-0.5">
          {job.site === "linkedin" && (
            <div className="w-6 h-6 rounded-md bg-blue-600/20 flex items-center justify-center">
              <span className="text-blue-400 text-xs font-bold">in</span>
            </div>
          )}
          {job.site === "indeed" && (
            <div className="w-6 h-6 rounded-md bg-violet-600/20 flex items-center justify-center">
              <span className="text-violet-400 text-xs font-bold">iD</span>
            </div>
          )}
          {job.site === "google" && (
            <div className="w-6 h-6 rounded-md bg-emerald-600/20 flex items-center justify-center">
              <span className="text-emerald-400 text-xs font-bold">G</span>
            </div>
          )}
        </div>
      </div>

      <div className="flex items-center gap-2 mt-2.5">
        <span className={`badge ${job.is_remote ? 'badge-remote' : 'badge-onsite'}`}>
          {job.is_remote ? "🌍 Remote" : "📍 Onsite"}
        </span>
        <span className="badge badge-site">{job.site}</span>
        {job.date_posted && (
          <span className="text-[0.65rem] text-slate-500 ml-auto">{job.date_posted}</span>
        )}
      </div>
    </div>
  );
}