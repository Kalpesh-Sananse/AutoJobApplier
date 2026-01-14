const express = require('express');
const Profile = require('../models/Profile');
const authenticate = require('../middleware/auth');

const router = express.Router();

/**
 * GET /api/profile
 * Get current user's profile
 * Protected route
 */
router.get('/', authenticate, async (req, res) => {
  try {
    let profile = await Profile.findOne({ user: req.user._id }).populate('user', 'email');
    
    // If profile doesn't exist, create an empty one
    if (!profile) {
      profile = new Profile({ user: req.user._id });
      await profile.save();
    }

    res.json({
      success: true,
      data: { profile }
    });
  } catch (error) {
    console.error('Get profile error:', error);
    res.status(500).json({
      success: false,
      message: 'Error fetching profile',
      error: error.message
    });
  }
});

/**
 * PUT /api/profile
 * Create or update current user's profile
 * Protected route
 */
router.put('/', authenticate, async (req, res) => {
  try {
    const updateData = req.body;

    // Find or create profile
    let profile = await Profile.findOne({ user: req.user._id });

    if (!profile) {
      // Create new profile
      profile = new Profile({
        user: req.user._id,
        ...updateData
      });
      await profile.save();
    } else {
      // Update existing profile
      // Merge the update data with existing profile
      Object.keys(updateData).forEach(key => {
        if (updateData[key] !== undefined) {
          if (typeof updateData[key] === 'object' && !Array.isArray(updateData[key])) {
            // For nested objects like personalInfo, merge them
            profile[key] = { ...profile[key], ...updateData[key] };
          } else {
            profile[key] = updateData[key];
          }
        }
      });
      await profile.save();
    }

    // Populate user field
    await profile.populate('user', 'email');

    res.json({
      success: true,
      message: 'Profile updated successfully',
      data: { profile }
    });
  } catch (error) {
    console.error('Update profile error:', error);
    res.status(500).json({
      success: false,
      message: 'Error updating profile',
      error: error.message
    });
  }
});

/**
 * GET /api/profile/completion
 * Get profile completion percentage
 * Protected route
 */
router.get('/completion', authenticate, async (req, res) => {
  try {
    const profile = await Profile.findOne({ user: req.user._id });
    
    if (!profile) {
      return res.json({
        success: true,
        data: { completionPercentage: 0 }
      });
    }

    // Calculate completion based on filled fields
    const fields = [
      profile.personalInfo?.fullName,
      profile.personalInfo?.phoneNumber,
      profile.personalInfo?.location,
      profile.professionalSummary,
      profile.skills?.length > 0,
      profile.education?.length > 0,
      profile.workExperience?.length > 0,
      profile.projects?.length > 0,
      profile.resumePreferences?.jobRole,
      profile.resumePreferences?.location
    ];

    const filledFields = fields.filter(field => field && field !== '').length;
    const completionPercentage = Math.round((filledFields / fields.length) * 100);

    res.json({
      success: true,
      data: { completionPercentage }
    });
  } catch (error) {
    console.error('Get completion error:', error);
    res.status(500).json({
      success: false,
      message: 'Error calculating completion',
      error: error.message
    });
  }
});

module.exports = router;
