import React from 'react';
import DashboardLayout from '../components/Layout/DashboardLayout';
import { useAuth } from '../context/AuthContext';

const Settings = () => {
  const { user, logout } = useAuth();

  return (
    <DashboardLayout>
      <div>
        <h1>Settings</h1>
        <div className="card">
          <h2>Account Settings</h2>
          <p><strong>Email:</strong> {user?.email}</p>
          <p><strong>Role:</strong> {user?.role}</p>
          {/* TODO: Add email change, password change, account deletion options */}
        </div>
        
        <div className="card">
          <h2>Automation Settings</h2>
          <p>Automation settings will be available after n8n integration.</p>
          {/* TODO: Add n8n workflow configuration options */}
          {/* TODO: Add webhook endpoints for job status updates */}
        </div>
        
        <div className="card">
          <h2>Danger Zone</h2>
          <button onClick={logout} className="btn btn-danger">
            Logout
          </button>
          {/* TODO: Add account deletion option */}
        </div>
      </div>
    </DashboardLayout>
  );
};

export default Settings;
