import React, { useState, useEffect } from 'react';
import DashboardLayout from '../components/Layout/DashboardLayout';
import api from '../utils/api';
import './Profile.css';

const Profile = () => {
  const [activeTab, setActiveTab] = useState('personal');
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState({ type: '', text: '' });
  
  const [profile, setProfile] = useState({
    personalInfo: {
      fullName: '',
      phoneNumber: '',
      location: '',
      linkedInUrl: '',
      githubUrl: '',
      portfolioUrl: ''
    },
    professionalSummary: '',
    skills: [],
    education: [],
    workExperience: [],
    projects: [],
    certifications: [],
    resumePreferences: {
      jobRole: '',
      location: '',
      jobType: ''
    }
  });

  const [newSkill, setNewSkill] = useState('');
  const [newEducation, setNewEducation] = useState({ degree: '', college: '', year: '' });
  const [newExperience, setNewExperience] = useState({ company: '', role: '', duration: '', description: '' });
  const [newProject, setNewProject] = useState({ title: '', techStack: '', description: '' });
  const [newCertification, setNewCertification] = useState({ name: '', issuer: '', date: '', url: '' });

  useEffect(() => {
    fetchProfile();
  }, []);

  const fetchProfile = async () => {
    try {
      const response = await api.get('/profile');
      if (response.data.success) {
        setProfile(response.data.data.profile);
      }
    } catch (error) {
      console.error('Error fetching profile:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (section, field, value) => {
    if (section === 'personalInfo' || section === 'resumePreferences') {
      setProfile({
        ...profile,
        [section]: {
          ...profile[section],
          [field]: value
        }
      });
    } else {
      setProfile({
        ...profile,
        [field]: value
      });
    }
  };

  const handleSave = async () => {
    setSaving(true);
    setMessage({ type: '', text: '' });
    
    try {
      const response = await api.put('/profile', profile);
      if (response.data.success) {
        setMessage({ type: 'success', text: 'Profile saved successfully!' });
        setTimeout(() => setMessage({ type: '', text: '' }), 3000);
      }
    } catch (error) {
      setMessage({ type: 'error', text: error.response?.data?.message || 'Error saving profile' });
    } finally {
      setSaving(false);
    }
  };

  const addSkill = () => {
    if (newSkill.trim()) {
      setProfile({
        ...profile,
        skills: [...profile.skills, newSkill.trim()]
      });
      setNewSkill('');
    }
  };

  const removeSkill = (index) => {
    setProfile({
      ...profile,
      skills: profile.skills.filter((_, i) => i !== index)
    });
  };

  const addEducation = () => {
    if (newEducation.degree && newEducation.college && newEducation.year) {
      setProfile({
        ...profile,
        education: [...profile.education, { ...newEducation }]
      });
      setNewEducation({ degree: '', college: '', year: '' });
    }
  };

  const removeEducation = (index) => {
    setProfile({
      ...profile,
      education: profile.education.filter((_, i) => i !== index)
    });
  };

  const addExperience = () => {
    if (newExperience.company && newExperience.role && newExperience.duration) {
      setProfile({
        ...profile,
        workExperience: [...profile.workExperience, { ...newExperience }]
      });
      setNewExperience({ company: '', role: '', duration: '', description: '' });
    }
  };

  const removeExperience = (index) => {
    setProfile({
      ...profile,
      workExperience: profile.workExperience.filter((_, i) => i !== index)
    });
  };

  const addProject = () => {
    if (newProject.title && newProject.description) {
      const techStackArray = newProject.techStack.split(',').map(tech => tech.trim()).filter(tech => tech);
      setProfile({
        ...profile,
        projects: [...profile.projects, { ...newProject, techStack: techStackArray }]
      });
      setNewProject({ title: '', techStack: '', description: '' });
    }
  };

  const removeProject = (index) => {
    setProfile({
      ...profile,
      projects: profile.projects.filter((_, i) => i !== index)
    });
  };

  const addCertification = () => {
    if (newCertification.name && newCertification.issuer) {
      setProfile({
        ...profile,
        certifications: [...profile.certifications, { ...newCertification }]
      });
      setNewCertification({ name: '', issuer: '', date: '', url: '' });
    }
  };

  const removeCertification = (index) => {
    setProfile({
      ...profile,
      certifications: profile.certifications.filter((_, i) => i !== index)
    });
  };

  if (loading) {
    return (
      <DashboardLayout>
        <div>Loading...</div>
      </DashboardLayout>
    );
  }

  const tabs = [
    { id: 'personal', label: 'Personal Info' },
    { id: 'summary', label: 'Summary' },
    { id: 'skills', label: 'Skills' },
    { id: 'education', label: 'Education' },
    { id: 'experience', label: 'Experience' },
    { id: 'projects', label: 'Projects' },
    { id: 'certifications', label: 'Certifications' },
    { id: 'preferences', label: 'Job Preferences' }
  ];

  return (
    <DashboardLayout>
      <div className="profile-page">
        <div className="profile-header">
          <h1>Profile</h1>
          <button onClick={handleSave} className="btn btn-primary" disabled={saving}>
            {saving ? 'Saving...' : 'Save Profile'}
          </button>
        </div>

        {message.text && (
          <div className={`message ${message.type}`}>
            {message.text}
          </div>
        )}

        <div className="profile-tabs">
          {tabs.map(tab => (
            <button
              key={tab.id}
              className={`tab-button ${activeTab === tab.id ? 'active' : ''}`}
              onClick={() => setActiveTab(tab.id)}
            >
              {tab.label}
            </button>
          ))}
        </div>

        <div className="profile-content">
          {/* Personal Information Tab */}
          {activeTab === 'personal' && (
            <div className="profile-section">
              <h2>Personal Information</h2>
              <div className="form-grid">
                <div className="form-group">
                  <label>Full Name</label>
                  <input
                    type="text"
                    value={profile.personalInfo.fullName}
                    onChange={(e) => handleInputChange('personalInfo', 'fullName', e.target.value)}
                    placeholder="John Doe"
                  />
                </div>
                <div className="form-group">
                  <label>Phone Number</label>
                  <input
                    type="tel"
                    value={profile.personalInfo.phoneNumber}
                    onChange={(e) => handleInputChange('personalInfo', 'phoneNumber', e.target.value)}
                    placeholder="+1234567890"
                  />
                </div>
                <div className="form-group">
                  <label>Location</label>
                  <input
                    type="text"
                    value={profile.personalInfo.location}
                    onChange={(e) => handleInputChange('personalInfo', 'location', e.target.value)}
                    placeholder="City, Country"
                  />
                </div>
                <div className="form-group">
                  <label>LinkedIn URL</label>
                  <input
                    type="url"
                    value={profile.personalInfo.linkedInUrl}
                    onChange={(e) => handleInputChange('personalInfo', 'linkedInUrl', e.target.value)}
                    placeholder="https://linkedin.com/in/yourprofile"
                  />
                </div>
                <div className="form-group">
                  <label>GitHub URL</label>
                  <input
                    type="url"
                    value={profile.personalInfo.githubUrl}
                    onChange={(e) => handleInputChange('personalInfo', 'githubUrl', e.target.value)}
                    placeholder="https://github.com/yourusername"
                  />
                </div>
                <div className="form-group">
                  <label>Portfolio URL</label>
                  <input
                    type="url"
                    value={profile.personalInfo.portfolioUrl}
                    onChange={(e) => handleInputChange('personalInfo', 'portfolioUrl', e.target.value)}
                    placeholder="https://yourportfolio.com"
                  />
                </div>
              </div>
            </div>
          )}

          {/* Professional Summary Tab */}
          {activeTab === 'summary' && (
            <div className="profile-section">
              <h2>Professional Summary</h2>
              <div className="form-group">
                <label>Summary</label>
                <textarea
                  rows="8"
                  value={profile.professionalSummary}
                  onChange={(e) => handleInputChange(null, 'professionalSummary', e.target.value)}
                  placeholder="Write a brief professional summary about yourself..."
                />
              </div>
            </div>
          )}

          {/* Skills Tab */}
          {activeTab === 'skills' && (
            <div className="profile-section">
              <h2>Skills</h2>
              <div className="add-item-form">
                <input
                  type="text"
                  value={newSkill}
                  onChange={(e) => setNewSkill(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && addSkill()}
                  placeholder="Enter a skill (e.g., JavaScript, React, Node.js)"
                />
                <button type="button" onClick={addSkill} className="btn btn-primary">Add Skill</button>
              </div>
              <div className="items-list">
                {profile.skills.map((skill, index) => (
                  <div key={index} className="item-tag">
                    {skill}
                    <button type="button" onClick={() => removeSkill(index)} className="remove-btn">×</button>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Education Tab */}
          {activeTab === 'education' && (
            <div className="profile-section">
              <h2>Education</h2>
              <div className="add-item-form card">
                <div className="form-grid">
                  <div className="form-group">
                    <label>Degree</label>
                    <input
                      type="text"
                      value={newEducation.degree}
                      onChange={(e) => setNewEducation({ ...newEducation, degree: e.target.value })}
                      placeholder="Bachelor of Science"
                    />
                  </div>
                  <div className="form-group">
                    <label>College/University</label>
                    <input
                      type="text"
                      value={newEducation.college}
                      onChange={(e) => setNewEducation({ ...newEducation, college: e.target.value })}
                      placeholder="University Name"
                    />
                  </div>
                  <div className="form-group">
                    <label>Year</label>
                    <input
                      type="text"
                      value={newEducation.year}
                      onChange={(e) => setNewEducation({ ...newEducation, year: e.target.value })}
                      placeholder="2020-2024"
                    />
                  </div>
                </div>
                <button type="button" onClick={addEducation} className="btn btn-primary">Add Education</button>
              </div>
              <div className="items-list">
                {profile.education.map((edu, index) => (
                  <div key={index} className="item-card">
                    <h4>{edu.degree}</h4>
                    <p>{edu.college}</p>
                    <p className="text-muted">{edu.year}</p>
                    <button type="button" onClick={() => removeEducation(index)} className="remove-btn">Remove</button>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Work Experience Tab */}
          {activeTab === 'experience' && (
            <div className="profile-section">
              <h2>Work Experience</h2>
              <div className="add-item-form card">
                <div className="form-grid">
                  <div className="form-group">
                    <label>Company</label>
                    <input
                      type="text"
                      value={newExperience.company}
                      onChange={(e) => setNewExperience({ ...newExperience, company: e.target.value })}
                      placeholder="Company Name"
                    />
                  </div>
                  <div className="form-group">
                    <label>Role</label>
                    <input
                      type="text"
                      value={newExperience.role}
                      onChange={(e) => setNewExperience({ ...newExperience, role: e.target.value })}
                      placeholder="Software Engineer"
                    />
                  </div>
                  <div className="form-group">
                    <label>Duration</label>
                    <input
                      type="text"
                      value={newExperience.duration}
                      onChange={(e) => setNewExperience({ ...newExperience, duration: e.target.value })}
                      placeholder="Jan 2020 - Dec 2022"
                    />
                  </div>
                  <div className="form-group full-width">
                    <label>Description</label>
                    <textarea
                      rows="4"
                      value={newExperience.description}
                      onChange={(e) => setNewExperience({ ...newExperience, description: e.target.value })}
                      placeholder="Describe your responsibilities and achievements..."
                    />
                  </div>
                </div>
                <button type="button" onClick={addExperience} className="btn btn-primary">Add Experience</button>
              </div>
              <div className="items-list">
                {profile.workExperience.map((exp, index) => (
                  <div key={index} className="item-card">
                    <h4>{exp.role} at {exp.company}</h4>
                    <p className="text-muted">{exp.duration}</p>
                    <p>{exp.description}</p>
                    <button type="button" onClick={() => removeExperience(index)} className="remove-btn">Remove</button>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Projects Tab */}
          {activeTab === 'projects' && (
            <div className="profile-section">
              <h2>Projects</h2>
              <div className="add-item-form card">
                <div className="form-grid">
                  <div className="form-group">
                    <label>Project Title</label>
                    <input
                      type="text"
                      value={newProject.title}
                      onChange={(e) => setNewProject({ ...newProject, title: e.target.value })}
                      placeholder="Project Name"
                    />
                  </div>
                  <div className="form-group">
                    <label>Tech Stack (comma-separated)</label>
                    <input
                      type="text"
                      value={newProject.techStack}
                      onChange={(e) => setNewProject({ ...newProject, techStack: e.target.value })}
                      placeholder="React, Node.js, MongoDB"
                    />
                  </div>
                  <div className="form-group full-width">
                    <label>Description</label>
                    <textarea
                      rows="4"
                      value={newProject.description}
                      onChange={(e) => setNewProject({ ...newProject, description: e.target.value })}
                      placeholder="Describe your project..."
                    />
                  </div>
                </div>
                <button type="button" onClick={addProject} className="btn btn-primary">Add Project</button>
              </div>
              <div className="items-list">
                {profile.projects.map((project, index) => (
                  <div key={index} className="item-card">
                    <h4>{project.title}</h4>
                    {project.techStack.length > 0 && (
                      <div className="tech-stack">
                        {project.techStack.map((tech, i) => (
                          <span key={i} className="tech-tag">{tech}</span>
                        ))}
                      </div>
                    )}
                    <p>{project.description}</p>
                    <button type="button" onClick={() => removeProject(index)} className="remove-btn">Remove</button>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Certifications Tab */}
          {activeTab === 'certifications' && (
            <div className="profile-section">
              <h2>Certifications</h2>
              <div className="add-item-form card">
                <div className="form-grid">
                  <div className="form-group">
                    <label>Certification Name</label>
                    <input
                      type="text"
                      value={newCertification.name}
                      onChange={(e) => setNewCertification({ ...newCertification, name: e.target.value })}
                      placeholder="AWS Certified Developer"
                    />
                  </div>
                  <div className="form-group">
                    <label>Issuer</label>
                    <input
                      type="text"
                      value={newCertification.issuer}
                      onChange={(e) => setNewCertification({ ...newCertification, issuer: e.target.value })}
                      placeholder="Amazon Web Services"
                    />
                  </div>
                  <div className="form-group">
                    <label>Date</label>
                    <input
                      type="text"
                      value={newCertification.date}
                      onChange={(e) => setNewCertification({ ...newCertification, date: e.target.value })}
                      placeholder="Jan 2023"
                    />
                  </div>
                  <div className="form-group">
                    <label>URL (Optional)</label>
                    <input
                      type="url"
                      value={newCertification.url}
                      onChange={(e) => setNewCertification({ ...newCertification, url: e.target.value })}
                      placeholder="https://..."
                    />
                  </div>
                </div>
                <button type="button" onClick={addCertification} className="btn btn-primary">Add Certification</button>
              </div>
              <div className="items-list">
                {profile.certifications.map((cert, index) => (
                  <div key={index} className="item-card">
                    <h4>{cert.name}</h4>
                    <p>{cert.issuer}</p>
                    {cert.date && <p className="text-muted">{cert.date}</p>}
                    {cert.url && <a href={cert.url} target="_blank" rel="noopener noreferrer">View Certificate</a>}
                    <button type="button" onClick={() => removeCertification(index)} className="remove-btn">Remove</button>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Job Preferences Tab */}
          {activeTab === 'preferences' && (
            <div className="profile-section">
              <h2>Job Preferences</h2>
              <div className="form-grid">
                <div className="form-group">
                  <label>Desired Job Role</label>
                  <input
                    type="text"
                    value={profile.resumePreferences.jobRole}
                    onChange={(e) => handleInputChange('resumePreferences', 'jobRole', e.target.value)}
                    placeholder="Software Engineer, Full Stack Developer, etc."
                  />
                </div>
                <div className="form-group">
                  <label>Preferred Location</label>
                  <input
                    type="text"
                    value={profile.resumePreferences.location}
                    onChange={(e) => handleInputChange('resumePreferences', 'location', e.target.value)}
                    placeholder="Remote, New York, San Francisco, etc."
                  />
                </div>
                <div className="form-group">
                  <label>Job Type</label>
                  <select
                    value={profile.resumePreferences.jobType}
                    onChange={(e) => handleInputChange('resumePreferences', 'jobType', e.target.value)}
                  >
                    <option value="">Select job type</option>
                    <option value="Full-time">Full-time</option>
                    <option value="Part-time">Part-time</option>
                    <option value="Contract">Contract</option>
                    <option value="Internship">Internship</option>
                  </select>
                </div>
              </div>
              <div className="info-box">
                <p><strong>Note:</strong> These preferences will be used when setting up job application automation in the future.</p>
                {/* TODO: Integrate with n8n workflow to use these preferences for job filtering */}
              </div>
            </div>
          )}
        </div>
      </div>
    </DashboardLayout>
  );
};

export default Profile;
