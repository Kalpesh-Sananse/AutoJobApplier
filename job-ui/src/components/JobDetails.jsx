export default function JobDetails({ job }) {
    if (!job) {
      return (
        <div className="h-full flex items-center justify-center text-gray-400">
          Select a job to view details
        </div>
      );
    }
  
    return (
      <div className="bg-white rounded-2xl p-8 shadow">
        <h2 className="text-2xl font-bold mb-2">{job.title}</h2>
        <p className="text-gray-600 mb-4">{job.company}</p>
  
        <div className="flex gap-4 text-sm text-gray-500 mb-6">
          <span>{job.site}</span>
          <span>{job.is_remote ? "Remote" : "Onsite"}</span>
          <span>{job.date_posted}</span>
        </div>
  
        <div className="flex gap-4 mb-6">
          <a
            href={job.job_url}
            target="_blank"
            rel="noreferrer"
            className="bg-green-600 hover:bg-green-700 text-white px-6 py-3 rounded-xl font-semibold"
          >
            Apply Now
          </a>
  
          <button className="border px-6 py-3 rounded-xl font-semibold">
            Save Job
          </button>
        </div>
  
        {job.description && (
          <div className="text-gray-700 text-sm leading-relaxed max-h-[300px] overflow-y-auto">
            {job.description}
          </div>
        )}
      </div>
    );
  }
  