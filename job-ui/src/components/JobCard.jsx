export default function JobCard({ job }) {
    return (
      <div className="bg-white rounded-2xl border border-gray-200 p-6 hover:shadow-xl transition">
  
        <div className="flex justify-between items-start gap-4">
          <h3 className="text-lg font-semibold text-gray-900">
            {job.title}
          </h3>
  
          <span className="text-xs bg-blue-100 text-blue-700 px-3 py-1 rounded-full font-medium">
            {job.site}
          </span>
        </div>
  
        <p className="text-gray-700 mt-2 font-medium">
          {job.company}
        </p>
  
        <div className="flex items-center gap-4 text-sm text-gray-500 mt-3">
          <span>{job.is_remote ? "🌍 Remote" : "🏢 Onsite"}</span>
          <span>{job.date_posted}</span>
        </div>
  
        <a
          href={job.job_url}
          target="_blank"
          rel="noreferrer"
          className="inline-block mt-5 text-blue-600 font-semibold hover:underline"
        >
          Apply →
        </a>
      </div>
    );
  }
  