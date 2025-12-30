import { useState } from "react";
import { countries } from "./data/countries";
import HeroSearch from "./components/HeroSearch";
import JobList from "./components/JobList";
import JobDetails from "./components/JobDetails";

const API_BASE = "http://127.0.0.1:8000";

export default function App() {
  const [role, setRole] = useState("");
  const [country, setCountry] = useState("India");
  const [limit, setLimit] = useState(20);
  const [jobs, setJobs] = useState([]);
  const [selectedJob, setSelectedJob] = useState(null);
  const [loading, setLoading] = useState(false);

  const fetchJobs = async () => {
    if (!role) return alert("Enter job title");

    setLoading(true);
    setJobs([]);
    setSelectedJob(null);

    const res = await fetch(
      `${API_BASE}/jobs?role=${encodeURIComponent(role)}&country=${country}&limit=${limit}`
    );

    const data = await res.json();
    setJobs(data.results || []);
    setLoading(false);
  };

  return (
    <div className="min-h-screen bg-gray-100 px-6 py-10">
      <HeroSearch
        role={role}
        setRole={setRole}
        country={country}
        setCountry={setCountry}
        limit={limit}
        setLimit={setLimit}
        countries={countries}
        onSearch={fetchJobs}
        loading={loading}
      />

      <div className="max-w-7xl mx-auto grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="md:col-span-1">
          <JobList
            jobs={jobs}
            selectedJob={selectedJob}
            setSelectedJob={setSelectedJob}
          />
        </div>

        <div className="md:col-span-2">
          <JobDetails job={selectedJob} />
        </div>
      </div>
    </div>
  );
}
