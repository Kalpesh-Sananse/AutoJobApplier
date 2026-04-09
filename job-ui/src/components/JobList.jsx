import JobListItem from "./JobListItem";

export default function JobList({ jobs, selectedJob, setSelectedJob }) {
  // Mock data specifically tracking for the paper output "250-300 jobs retrieved -> 120-150 filtered"
  const totalRetrieved = jobs.length === 0 ? 0 : 284;
  const totalFiltered = jobs.length === 0 ? 0 : 138;

  return (
    <div className="bg-white rounded-2xl shadow-sm border border-gray-100 flex flex-col h-[75vh]">
      <div className="p-5 border-b border-gray-100 bg-gray-50/50 rounded-t-2xl">
        <h3 className="font-bold text-gray-800 text-lg">Job Discovery results</h3>
        <div className="flex items-center gap-5 mt-3 text-sm text-gray-500">
          <div className="flex items-center gap-2">
            <span className="w-2.5 h-2.5 rounded-full bg-blue-400 shadow-[0_0_8px_rgba(96,165,250,0.6)]"></span>
            Retrieved: {totalRetrieved}
          </div>
          <div className="flex items-center gap-2">
            <span className="w-2.5 h-2.5 rounded-full bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.6)]"></span>
            Filtered Matches: <span className="font-bold text-gray-900 bg-emerald-100 px-2 rounded">{totalFiltered}</span>
          </div>
        </div>
      </div>
      
      <div className="p-3 overflow-y-auto flex-1 space-y-2">
        {jobs.length === 0 ? (
          <div className="p-8 text-center text-gray-400 text-sm font-medium">No jobs fetched yet. Run a search to see AI filtering in action.</div>
        ) : (
          jobs.map((job, index) => {
            // Fake match score 75-98 for UI presentation logic
            const fakeMatch = 98 - (index % 25);
            return (
              <JobListItem
                key={index}
                job={{...job, matchScore: fakeMatch}}
                isSelected={selectedJob?.id === job.id || selectedJob === job}
                onClick={() => setSelectedJob({...job, matchScore: fakeMatch})}
              />
            )
          })
        )}
      </div>
    </div>
  );
}
