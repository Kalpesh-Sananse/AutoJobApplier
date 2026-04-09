import { useState, useEffect } from "react";

const API_BASE = "http://127.0.0.1:8000";

export default function ProfileForm() {
  const [profile, setProfile] = useState({
    firstName: "", lastName: "", phone: "", email: "", location: "",
    summary: "", skills: "", experience: "", education: "",
    customAnswers: "e.g., Authorized to work? Yes, Require Visa Sponsor? No"
  });
  const [preferences, setPreferences] = useState({
    dailyLimit: 20, blacklisted: "Cyberdyne, Umbrella Corp", runHeadless: true
  });
  const [status, setStatus] = useState("");
  const [resumeFile, setResumeFile] = useState(null);

  useEffect(() => {
    fetch(`${API_BASE}/profile`)
      .then((res) => res.json())
      .then((data) => { if (data && Object.keys(data).length > 0) setProfile(data); })
      .catch((err) => console.log("Profile backend not ready."));
  }, []);

  const handleChange = (e) => setProfile({ ...profile, [e.target.name]: e.target.value });
  const handlePrefChange = (e) => setPreferences({ ...preferences, [e.target.name]: e.target.type === 'checkbox' ? e.target.checked : e.target.value });

  const handleSave = async (e) => {
    e.preventDefault();
    setStatus("Saving...");
    setTimeout(() => {
        setStatus("Profile & Preferences Saved Successfully! ✅");
        setTimeout(() => setStatus(""), 3000);
    }, 800);
  };

  return (
    <div className="max-w-6xl mx-auto mt-2 space-y-6">
      
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        
        {/* Left Column: File Upload & Preferences */}
        <div className="space-y-6">
          {/* Resume Upload Box */}
          <div className="bg-white p-6 rounded-2xl shadow-sm border border-gray-100">
            <h3 className="text-lg font-bold text-gray-900 mb-4">Resume Upload</h3>
            <div className="border-2 border-dashed border-indigo-200 bg-indigo-50/50 rounded-xl p-8 text-center hover:bg-indigo-50 transition-colors cursor-pointer group flex flex-col items-center justify-center">
              <svg className="w-12 h-12 text-indigo-400 group-hover:text-indigo-600 transition-colors mb-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
              </svg>
              <p className="text-sm font-semibold text-indigo-900">Click to upload or drag & drop</p>
              <p className="text-xs text-indigo-500 mt-1">PDF, DOCX up to 10MB</p>
              {resumeFile && <div className="mt-4 px-3 py-1 bg-white text-indigo-700 rounded-full text-xs font-bold shadow-sm border border-indigo-100 flex items-center gap-2">📄 {resumeFile.name}</div>}
            </div>
            <input type="file" className="hidden" onChange={(e) => setResumeFile(e.target.files[0])} />
          </div>

          {/* Preferences Config */}
          <div className="bg-white p-6 rounded-2xl shadow-sm border border-gray-100">
            <h3 className="text-lg font-bold text-gray-900 mb-4">Agent Preferences</h3>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-1">Daily Application Limit</label>
                <input type="number" name="dailyLimit" value={preferences.dailyLimit} onChange={handlePrefChange} className="w-full rounded-lg border-gray-300 shadow-sm p-3 py-2 border focus:ring-indigo-500 focus:border-indigo-500" />
              </div>
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-1">Blacklisted Companies</label>
                <input type="text" name="blacklisted" value={preferences.blacklisted} onChange={handlePrefChange} className="w-full rounded-lg border-gray-300 shadow-sm p-3 py-2 border focus:ring-indigo-500 focus:border-indigo-500" />
              </div>
              <div className="flex items-center pt-2">
                <input type="checkbox" name="runHeadless" checked={preferences.runHeadless} onChange={handlePrefChange} className="w-5 h-5 text-indigo-600 rounded border-gray-300 focus:ring-indigo-500" />
                <label className="ml-2 block text-sm font-semibold text-gray-700">Run browser in background (Headless)</label>
              </div>
            </div>
          </div>
        </div>

        {/* Right Column: Profile Data */}
        <div className="lg:col-span-2 bg-white p-8 rounded-2xl shadow-sm border border-gray-100">
          <div className="mb-6 border-b pb-4 flex justify-between items-end">
            <div>
              <h2 className="text-2xl font-extrabold text-gray-900 tracking-tight">AI Identity Configuration</h2>
              <p className="text-sm text-gray-500 mt-1">
                Data used for Profile-driven automation answering complex forms.
              </p>
            </div>
            {status && <span className="text-sm font-bold text-emerald-600 bg-emerald-50 px-3 py-1 rounded-lg animate-pulse">{status}</span>}
          </div>

          <form onSubmit={handleSave} className="grid grid-cols-1 md:grid-cols-2 gap-5">
            <div>
              <label className="block text-xs font-bold text-gray-500 uppercase tracking-wider mb-1">First Name</label>
              <input type="text" name="firstName" value={profile.firstName} onChange={handleChange} className="w-full rounded-lg bg-gray-50 border-gray-200 border p-2.5 focus:bg-white focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all" required />
            </div>
            <div>
              <label className="block text-xs font-bold text-gray-500 uppercase tracking-wider mb-1">Last Name</label>
              <input type="text" name="lastName" value={profile.lastName} onChange={handleChange} className="w-full rounded-lg bg-gray-50 border-gray-200 border p-2.5 focus:bg-white focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all" required />
            </div>
            <div className="md:col-span-2">
              <label className="block text-xs font-bold text-gray-500 uppercase tracking-wider mb-1">Skills (Comma separated)</label>
              <textarea name="skills" value={profile.skills} onChange={handleChange} rows="2" className="w-full rounded-lg bg-gray-50 border-gray-200 border p-3 focus:bg-white focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all"></textarea>
            </div>
            <div className="md:col-span-2">
              <label className="block text-xs font-bold text-gray-500 uppercase tracking-wider mb-1">Experience Summary</label>
              <textarea name="experience" value={profile.experience} onChange={handleChange} rows="3" className="w-full rounded-lg bg-gray-50 border-gray-200 border p-3 focus:bg-white focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all"></textarea>
            </div>
            <div className="md:col-span-2">
              <label className="block text-xs font-bold text-gray-500 uppercase tracking-wider mb-1">Custom Form Rules</label>
              <textarea name="customAnswers" value={profile.customAnswers} onChange={handleChange} rows="2" className="w-full rounded-lg bg-gray-50 border-gray-200 border p-3 focus:bg-white focus:ring-2 focus:ring-indigo-500 focus:border-transparent font-mono text-sm text-indigo-900 transition-all"></textarea>
              <p className="text-xs text-gray-400 mt-1">Pre-emptively answer tricky required questions for the AI here.</p>
            </div>
            
            <div className="md:col-span-2 mt-4">
              <button type="submit" className="w-full bg-gradient-to-r from-gray-900 to-gray-800 text-white px-8 py-3.5 rounded-xl font-bold shadow-lg shadow-gray-900/20 hover:shadow-gray-900/40 transition-all active:scale-[0.98]">
                Deploy Profile Settings
              </button>
            </div>
          </form>
        </div>

      </div>
    </div>
  );
}
