export default function JobListItem({ job, isSelected, onClick }) {
    return (
      <div
        onClick={onClick}
        className={`cursor-pointer rounded-xl p-4 border transition-all ${
          isSelected
            ? "border-indigo-500 bg-indigo-50/50 shadow-md transform scale-[1.02]"
            : "border-transparent border-b-gray-100 hover:border-gray-200 hover:bg-gray-50 hover:shadow-sm"
        }`}
      >
        <div className="flex justify-between items-start gap-3">
            <h3 className="font-bold text-gray-900 truncate flex-1 leading-tight">
            {job.title}
            </h3>
            {job.matchScore && (
                <div className={`px-2 py-1 rounded text-xs font-black shadow-sm ${job.matchScore >= 90 ? 'bg-emerald-100 text-emerald-700 border border-emerald-200' : 'bg-blue-100 text-blue-700 border border-blue-200'}`}>
                    {job.matchScore}%
                </div>
            )}
        </div>
  
        <p className="text-sm text-gray-600 mt-1.5 font-medium">{job.company}</p>
  
        <div className="flex gap-3 text-xs text-gray-500 mt-3 pt-3 border-t border-gray-100 border-dashed">
          <span className="bg-white border border-gray-200 px-2 py-1 rounded shadow-sm">{job.site}</span>
          <span className="bg-white border border-gray-200 px-2 py-1 rounded shadow-sm flex items-center gap-1">
            <span className={`w-1.5 h-1.5 rounded-full ${job.is_remote ? 'bg-purple-400' : 'bg-orange-400'}`}></span>
            {job.is_remote ? "Remote" : "Onsite"}
          </span>
        </div>
      </div>
    );
  }