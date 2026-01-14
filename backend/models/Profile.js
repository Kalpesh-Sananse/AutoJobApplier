const mongoose = require('mongoose');

const educationSchema = new mongoose.Schema({
  degree: { type: String, required: true },
  college: { type: String, required: true },
  year: { type: String, required: true }
}, { _id: true });

const workExperienceSchema = new mongoose.Schema({
  company: { type: String, required: true },
  role: { type: String, required: true },
  duration: { type: String, required: true }, // e.g., "Jan 2020 - Dec 2022"
  description: { type: String, required: true }
}, { _id: true });

const projectSchema = new mongoose.Schema({
  title: { type: String, required: true },
  techStack: { type: [String], default: [] },
  description: { type: String, required: true }
}, { _id: true });

const certificationSchema = new mongoose.Schema({
  name: { type: String, required: true },
  issuer: { type: String, required: true },
  date: { type: String },
  url: { type: String }
}, { _id: true });

const profileSchema = new mongoose.Schema({
  user: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'User',
    required: true,
    unique: true
  },
  // Personal Information
  personalInfo: {
    fullName: { type: String, default: '' },
    phoneNumber: { type: String, default: '' },
    location: { type: String, default: '' },
    linkedInUrl: { type: String, default: '' },
    githubUrl: { type: String, default: '' },
    portfolioUrl: { type: String, default: '' }
  },
  // Professional Summary
  professionalSummary: { type: String, default: '' },
  // Skills array
  skills: { type: [String], default: [] },
  // Education array
  education: { type: [educationSchema], default: [] },
  // Work Experience array
  workExperience: { type: [workExperienceSchema], default: [] },
  // Projects array
  projects: { type: [projectSchema], default: [] },
  // Certifications array (optional)
  certifications: { type: [certificationSchema], default: [] },
  // Resume Preferences
  resumePreferences: {
    jobRole: { type: String, default: '' },
    location: { type: String, default: '' },
    jobType: { type: String, enum: ['Full-time', 'Part-time', 'Contract', 'Internship', ''], default: '' }
  }
}, {
  timestamps: true
});

// Index for faster queries
profileSchema.index({ user: 1 });

module.exports = mongoose.model('Profile', profileSchema);
