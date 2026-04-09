import { useState } from "react";
import { countries } from "./data/countries";
import HeroSearch from "./components/HeroSearch";
import JobList from "./components/JobList";
import JobDetails from "./components/JobDetails";
import ProfileForm from "./components/ProfileForm";
import LoginUI from "./components/LoginUI";
import JobDashboard from "./components/JobDashboard";
import ScrapingTerminal from "./components/ScrapingTerminal";

const API_BASE = "http://127.0.0.1:8000";

export default function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [activeTab, setActiveTab] = useState("search");
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

  if (!isAuthenticated) {
    return <LoginUI onLogin={() => setIsAuthenticated(true)} />;
  }

  return (
    <div className="min-h-screen bg-gray-100 pb-10">
      <nav className="bg-white shadow-sm mb-6 sticky top-0 z-10 w-full border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16 items-center">
            <div className="flex items-center">
              <span className="text-xl font-extrabold text-blue-700 tracking-tight">AutoJobApplier AI</span>
            </div>
            <div className="flex items-center space-x-2">
              <button
                onClick={() => setActiveTab("dashboard")}
                className={`px-4 py-2 rounded-md font-medium transition-colors ${
                  activeTab === "dashboard" ? "bg-emerald-600 text-white" : "text-gray-600 hover:bg-gray-100"
                }`}
              >
                📊 Dashboard
              </button>
              <button
                onClick={() => setActiveTab("search")}
                className={`px-4 py-2 rounded-md font-medium transition-colors ${
                  activeTab === "search" ? "bg-blue-600 text-white" : "text-gray-600 hover:bg-gray-100"
                }`}
              >
                🔎 Search
              </button>
              <button
                onClick={() => setActiveTab("profile")}
                className={`px-4 py-2 rounded-md font-medium transition-colors ${
                  activeTab === "profile" ? "bg-indigo-600 text-white" : "text-gray-600 hover:bg-gray-100"
                }`}
              >
                👤 Profile
              </button>
            </div>
          </div>
        </div>
      </nav>

      <div className="px-6">
        {activeTab === "search" && (
          <>
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

            {loading ? (
              <ScrapingTerminal />
            ) : (
              <div className="max-w-7xl mx-auto grid grid-cols-1 md:grid-cols-3 gap-6 mt-6">
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
            )}
          </>
        )}

        {activeTab === "profile" && <ProfileForm />}
        {activeTab === "dashboard" && <JobDashboard />}
      </div>
    </div>
  );
}
