export default function JobListItem({ job, isSelected, onClick }) {
    return (
      <div
        onClick={onClick}
        className={`cursor-pointer rounded-xl p-4 border transition ${
          isSelected
            ? "border-blue-600 bg-blue-50"
            : "border-gray-200 hover:bg-gray-50"
        }`}
      >
        <h3 className="font-semibold text-gray-900 truncate">
          {job.title}
        </h3>
  
        <p className="text-sm text-gray-600">{job.company}</p>
  
        <div className="flex gap-3 text-xs text-gray-500 mt-1">
          <span>{job.site}</span>
          <span>{job.is_remote ? "Remote" : "Onsite"}</span>
        </div>
      </div>
    );
  }
  