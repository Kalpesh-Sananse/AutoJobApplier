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
    try {
      const res = await fetch(
        `${API_BASE}/jobs?role=${encodeURIComponent(role)}&country=${country}&limit=${limit}`
      );
      const data = await res.json();
      setJobs(data.results || []);
    } catch (e) {
      console.error(e);
    }
    setLoading(false);
  };

  return (
    <div className="min-h-screen px-4 md:px-8 py-6">
      {/* Header */}
      <header className="max-w-7xl mx-auto mb-8 animate-fadeInUp">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl flex items-center justify-center text-lg" style={{ background: 'var(--gradient-brand)' }}>
              ⚡
            </div>
            <div>
              <h1 className="text-xl font-bold tracking-tight">
                <span className="gradient-text">Workly</span>
                <span className="text-slate-400 font-medium ml-1">AI</span>
              </h1>
              <p className="text-xs text-slate-500 -mt-0.5">Intelligent Job Automation</p>
            </div>
          </div>

          <div className="flex items-center gap-4">
            <div className="glass-card px-4 py-2 flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
              <span className="text-xs text-slate-400">Agent Online</span>
            </div>
          </div>
        </div>
      </header>

      {/* Stats Bar */}
      <div className="max-w-7xl mx-auto mb-6 animate-fadeInUp" style={{ animationDelay: '0.1s' }}>
        <div className="glass-card grid grid-cols-2 md:grid-cols-4 divide-x divide-white/5">
          <div className="stat-card">
            <div className="stat-number gradient-text">41</div>
            <div className="stat-label">Applied</div>
          </div>
          <div className="stat-card">
            <div className="stat-number text-emerald-400">91%</div>
            <div className="stat-label">Success Rate</div>
          </div>
          <div className="stat-card">
            <div className="stat-number text-cyan-400">102</div>
            <div className="stat-label">Fields Filled</div>
          </div>
          <div className="stat-card">
            <div className="stat-number text-violet-400">17</div>
            <div className="stat-label">Sessions</div>
          </div>
        </div>
      </div>

      {/* Search */}
      <div className="max-w-7xl mx-auto mb-6 animate-fadeInUp" style={{ animationDelay: '0.2s' }}>
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
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto grid grid-cols-1 lg:grid-cols-3 gap-6 animate-fadeInUp" style={{ animationDelay: '0.3s' }}>
        <div className="lg:col-span-1">
          <JobList
            jobs={jobs}
            selectedJob={selectedJob}
            setSelectedJob={setSelectedJob}
          />
        </div>
        <div className="lg:col-span-2">
          <JobDetails job={selectedJob} />
        </div>
      </div>

      {/* Footer */}
      <footer className="max-w-7xl mx-auto mt-12 pb-6 text-center">
        <p className="text-xs text-slate-600">
          Powered by <span className="gradient-text font-semibold">Ollama LLM</span> &amp; <span className="text-slate-400">Playwright Automation</span>
        </p>
      </footer>
    </div>
  );
}
