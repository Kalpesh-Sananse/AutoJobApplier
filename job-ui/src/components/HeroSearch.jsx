export default function HeroSearch({
  role, setRole, country, setCountry, limit, setLimit, countries, onSearch, loading
}) {
  return (
    <div className="glass-card gradient-border p-5">
      <div className="grid grid-cols-1 md:grid-cols-12 gap-3 items-end">
        {/* Job Title */}
        <div className="md:col-span-5">
          <label className="text-xs text-slate-500 font-medium uppercase tracking-wider mb-1.5 block">Job Title</label>
          <input
            className="input-glass"
            placeholder="e.g. Software Engineer, Data Scientist"
            value={role}
            onChange={(e) => setRole(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && onSearch()}
          />
        </div>

        {/* Country */}
        <div className="md:col-span-3">
          <label className="text-xs text-slate-500 font-medium uppercase tracking-wider mb-1.5 block">Location</label>
          <select
            className="select-glass w-full"
            value={country}
            onChange={(e) => setCountry(e.target.value)}
          >
            {countries.map((c) => (
              <option key={c}>{c}</option>
            ))}
          </select>
        </div>

        {/* Limit */}
        <div className="md:col-span-2">
          <label className="text-xs text-slate-500 font-medium uppercase tracking-wider mb-1.5 block">Results</label>
          <select
            className="select-glass w-full"
            value={limit}
            onChange={(e) => setLimit(parseInt(e.target.value))}
          >
            <option value="20">20 jobs</option>
            <option value="30">30 jobs</option>
            <option value="50">50 jobs</option>
            <option value="100">100 jobs</option>
          </select>
        </div>

        {/* Search Button */}
        <div className="md:col-span-2">
          <button
            disabled={loading}
            onClick={onSearch}
            className="btn-primary w-full flex items-center justify-center gap-2"
          >
            {loading ? (
              <>
                <span className="loader"></span>
                <span>Searching</span>
              </>
            ) : (
              <>
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                  <circle cx="11" cy="11" r="8" />
                  <line x1="21" y1="21" x2="16.65" y2="16.65" />
                </svg>
                <span>Search</span>
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
}