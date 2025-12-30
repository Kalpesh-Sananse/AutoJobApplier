export default function SearchBar({
    role,
    setRole,
    country,
    setCountry,
    limit,
    setLimit,
    countries,
    onSearch,
    loading
  }) {
    return (
      <div className="bg-white rounded-2xl shadow-lg p-6 sticky top-6 z-20">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
  
          <input
            className="border border-gray-300 rounded-lg px-4 py-3 focus:ring-2 focus:ring-blue-500 outline-none"
            placeholder="Job title (e.g. Junior Developer)"
            value={role}
            onChange={(e) => setRole(e.target.value)}
          />
  
          <select
            className="border border-gray-300 rounded-lg px-4 py-3"
            value={country}
            onChange={(e) => setCountry(e.target.value)}
          >
            {countries.map((c) => (
              <option key={c}>{c}</option>
            ))}
          </select>
  
          <select
            className="border border-gray-300 rounded-lg px-4 py-3"
            value={limit}
            onChange={(e) => setLimit(parseInt(e.target.value))}
          >
            <option value="20">20 jobs</option>
            <option value="30">30 jobs</option>
            <option value="50">50 jobs</option>
            <option value="100">100 jobs</option>
          </select>
  
          <button
            disabled={loading}
            onClick={onSearch}
            className="bg-blue-600 hover:bg-blue-700 transition text-white font-semibold rounded-lg px-6 py-3 disabled:opacity-50"
          >
            {loading ? "Searching..." : "Search Jobs"}
          </button>
  
        </div>
      </div>
    );
  }
  