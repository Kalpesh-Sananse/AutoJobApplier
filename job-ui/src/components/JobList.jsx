import JobListItem from "./JobListItem";

export default function JobList({ jobs, selectedJob, setSelectedJob }) {
  return (
    <div className="space-y-3 overflow-y-auto h-[70vh] pr-2">
      {jobs.map((job, index) => (
        <JobListItem
          key={index}
          job={job}
          isSelected={selectedJob === job}
          onClick={() => setSelectedJob(job)}
        />
      ))}
    </div>
  );
}
