import React, { useState, useEffect } from 'react';
import DashboardLayout from '../components/Layout/DashboardLayout';
import { useAuth } from '../context/AuthContext';
import api from '../utils/api';
import './Dashboard.css';

const Dashboard = () => {
  const { user, logout } = useAuth();
  const [profileCompletion, setProfileCompletion] = useState(0);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchProfileCompletion();
  }, []);

  const fetchProfileCompletion = async () => {
    try {
      const response = await api.get('/profile/completion');
      if (response.data.success) {
        setProfileCompletion(response.data.data.completionPercentage);
      }
    } catch (error) {
      console.error('Error fetching profile completion:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <DashboardLayout>
      <div className="dashboard-header">
        <div>
          <h1>Dashboard</h1>
          <p>Welcome back, {user?.email}</p>
        </div>
        <button onClick={logout} className="btn btn-danger">
          Logout
        </button>
      </div>

      <div className="dashboard-content">
        {/* Profile Completion Card */}
        <div className="card">
          <h2>Profile Completion</h2>
          <div className="completion-section">
            <div 
              className="completion-circle"
              style={{ '--percentage': `${profileCompletion}%` }}
            >
              <div className="completion-percentage">{profileCompletion}%</div>
            </div>
            <p className="completion-text">
              {profileCompletion < 50 
                ? 'Complete your profile to get started with job applications'
                : profileCompletion < 100
                ? 'You\'re making good progress! Complete your profile for better results.'
                : 'Your profile is complete! You\'re ready to start applying.'}
            </p>
            <a href="/profile" className="btn btn-primary">
              {profileCompletion < 100 ? 'Complete Profile' : 'Update Profile'}
            </a>
          </div>
        </div>

        {/* Placeholder Cards for Future Features */}
        <div className="dashboard-grid">
          <div className="card">
            <h3>📋 Job Applications</h3>
            <p className="placeholder-text">
              {/* TODO: Integrate with n8n workflow to show applied jobs */}
              Your job applications will appear here once automation is set up.
            </p>
            <div className="stat-number">0</div>
            <div className="stat-label">Applied Jobs</div>
          </div>

          <div className="card">
            <h3>🤖 Automation Status</h3>
            <p className="placeholder-text">
              {/* TODO: Connect to n8n workflow status */}
              Automation status will be displayed here after n8n integration.
            </p>
            <div className="status-badge inactive">Inactive</div>
          </div>

          <div className="card">
            <h3>📊 Statistics</h3>
            <p className="placeholder-text">
              {/* TODO: Add job application statistics */}
              Detailed statistics will be available after automation setup.
            </p>
            <div className="stats-grid">
              <div className="stat-item">
                <div className="stat-number">0</div>
                <div className="stat-label">This Week</div>
              </div>
              <div className="stat-item">
                <div className="stat-number">0</div>
                <div className="stat-label">This Month</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </DashboardLayout>
  );
};

export default Dashboard;
