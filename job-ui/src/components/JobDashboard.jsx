import React from 'react';

export default function JobDashboard() {
  const stats = [
    { label: 'Total Scraped', value: '1,245', change: '+12%', color: 'text-blue-600' },
    { label: 'Filtered Matches', value: '432', change: '+5%', color: 'text-indigo-600' },
    { label: 'Auto-Applied', value: '156', change: '+22%', color: 'text-green-600' },
    { label: 'Success Rate', value: '92%', change: '+1.5%', color: 'text-emerald-600' }
  ];

  const recentApplications = [
    { company: 'Google', role: 'Frontend Engineer', time: '10 mins ago', status: 'Success', match: 94 },
    { company: 'Meta', role: 'React Developer', time: '1 hour ago', status: 'Success', match: 88 },
    { company: 'Netflix', role: 'UI Engineer', time: '2 hours ago', status: 'Failed (Captcha)', match: 91 },
    { company: 'Amazon', role: 'Software Dev II', time: 'Yesterday', status: 'Success', match: 86 },
    { company: 'Apple', role: 'Frontend Architect', time: 'Yesterday', status: 'Success', match: 95 }
  ];

  return (
    <div className="max-w-7xl mx-auto space-y-8 p-6">
      <div className="mb-8">
        <h2 className="text-3xl font-extrabold text-gray-900 tracking-tight">Analytics Dashboard</h2>
        <p className="text-gray-500 mt-2">Real-time automation tracking and reporting metrics</p>
      </div>

      {/* Metrics Row */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        {stats.map((stat, i) => (
          <div key={i} className="bg-white rounded-2xl p-6 shadow-sm border border-gray-100 flex flex-col items-center justify-center text-center hover:shadow-md transition-shadow">
            <h3 className="text-gray-500 text-sm font-medium mb-1">{stat.label}</h3>
            <div className={`text-4xl font-extrabold ${stat.color} mb-2`}>{stat.value}</div>
            <div className="text-xs font-semibold text-emerald-500 bg-emerald-50 px-2 py-1 rounded-full">
              {stat.change} this week
            </div>
          </div>
        ))}
      </div>

      {/* Charts & Visuals Placeholder */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <div className="bg-white p-6 rounded-2xl shadow-sm border border-gray-100">
          <h3 className="text-lg font-bold text-gray-800 mb-4">Application Velocity (Last 7 Days)</h3>
          <div className="h-64 flex items-end justify-between space-x-2 pb-4 border-b border-gray-100 relative">
            {/* Fake Bar Chart */}
            {[40, 65, 45, 80, 55, 90, 75].map((height, i) => (
              <div key={i} className="w-full bg-indigo-100 rounded-t-sm relative group cursor-pointer transition-all hover:bg-indigo-600" style={{ height: `${height}%` }}>
                <div className="absolute -top-8 left-1/2 -translate-x-1/2 opacity-0 group-hover:opacity-100 bg-gray-800 text-white text-xs py-1 px-2 rounded tracking-widest transition-opacity">
                  {height}
                </div>
              </div>
            ))}
          </div>
          <div className="flex justify-between mt-3 text-xs text-gray-400 font-medium">
            <span>Mon</span><span>Tue</span><span>Wed</span><span>Thu</span><span>Fri</span><span>Sat</span><span>Sun</span>
          </div>
        </div>

        {/* Tracking List */}
        <div className="bg-white p-6 rounded-2xl shadow-sm border border-gray-100 overflow-hidden flex flex-col relative">
          <div className="flex justify-between items-center mb-4">
            <h3 className="text-lg font-bold text-gray-800">Live Application Tracking</h3>
            <span className="flex items-center gap-2 text-xs font-semibold text-indigo-600 bg-indigo-50 px-3 py-1 rounded-full">
              <span className="w-2 h-2 rounded-full bg-indigo-600 animate-pulse"></span>
              Agent Running
            </span>
          </div>
          
          <div className="space-y-4 overflow-y-auto flex-1 pr-2">
            {recentApplications.map((app, i) => (
              <div key={i} className="flex items-center justify-between p-4 rounded-xl border border-gray-100 hover:bg-gray-50 transition-colors">
                <div className="flex items-center gap-4">
                  <div className={`w-10 h-10 rounded-full flex items-center justify-center font-bold text-white ${app.status.includes('Success') ? 'bg-emerald-500' : 'bg-red-400'}`}>
                    {app.company[0]}
                  </div>
                  <div>
                    <h4 className="font-semibold text-gray-900">{app.company}</h4>
                    <p className="text-xs text-gray-500">{app.role} • {app.time}</p>
                  </div>
                </div>
                <div className="text-right">
                  <div className={`text-sm font-bold ${app.status.includes('Success') ? 'text-emerald-500' : 'text-red-500'}`}>
                    {app.status}
                  </div>
                  <div className="text-xs text-gray-400 mt-1">Match: {app.match}%</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
