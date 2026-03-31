import JobListItem from "./JobListItem";

export default function JobList({ jobs, selectedJob, setSelectedJob }) {
  return (
    <div className="glass-card p-4">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-sm font-semibold text-slate-300 uppercase tracking-wider">
          Job Listings
        </h2>
        {jobs.length > 0 && (
          <span className="badge badge-site">{jobs.length} found</span>
        )}
      </div>

      <div className="space-y-2.5 overflow-y-auto max-h-[65vh] pr-1">
        {jobs.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-16 text-center">
            <div className="text-4xl mb-3 animate-float">🔍</div>
            <p className="text-sm text-slate-500">Search for jobs to get started</p>
            <p className="text-xs text-slate-600 mt-1">Try "Software Engineer" in India</p>
          </div>
        ) : (
          jobs.map((job, index) => (
            <div
              key={index}
              className="animate-fadeInUp"
              style={{ animationDelay: `${index * 0.05}s` }}
            >
              <JobListItem
                job={job}
                isSelected={selectedJob === job}
                onClick={() => setSelectedJob(job)}
              />
            </div>
          ))
        )}
      </div>
    </div>
  );
}
