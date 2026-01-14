import React from 'react';
import DashboardLayout from '../components/Layout/DashboardLayout';
import { Link } from 'react-router-dom';

const JobPreferences = () => {
  return (
    <DashboardLayout>
      <div>
        <h1>Job Preferences</h1>
        <p>This page will be used to configure job application preferences.</p>
        <p>For now, please update your job preferences in the <Link to="/profile">Profile</Link> section.</p>
        {/* TODO: Create dedicated job preferences page with advanced filtering options */}
        {/* TODO: Integrate with n8n workflow to use these preferences */}
      </div>
    </DashboardLayout>
  );
};

export default JobPreferences;
