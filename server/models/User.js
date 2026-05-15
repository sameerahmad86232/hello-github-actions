const mongoose = require('mongoose');
const bcrypt = require('bcryptjs');

const userSchema = new mongoose.Schema({
  email: {
    type: String,
    required: true,
    unique: true,
    lowercase: true,
    trim: true
  },
  password: {
    type: String,
    required: function() {
      return !this.googleId; // Password not required if using Google OAuth
    }
  },
  googleId: {
    type: String,
    sparse: true
  },
  name: {
    type: String,
    required: true
  },
  avatar: String,
  role: {
    type: String,
    enum: ['user', 'admin', 'viewer'],
    default: 'user'
  },
  workspace: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'Workspace'
  },
  credits: {
    type: Number,
    default: 100 // Free tier credits
  },
  subscription: {
    plan: {
      type: String,
      enum: ['free', 'pro', 'enterprise'],
      default: 'free'
    },
    status: {
      type: String,
      enum: ['active', 'cancelled', 'past_due'],
      default: 'active'
    },
    currentPeriodEnd: Date
  },
  settings: {
    emailNotifications: { type: Boolean, default: true },
    slackWebhook: String,
    timezone: { type: String, default: 'UTC' }
  },
  createdAt: {
    type: Date,
    default: Date.now
  },
  lastLogin: Date
});

// Hash password before saving
userSchema.pre('save', async function(next) {
  if (!this.isModified('password')) return next();
  
  try {
    const salt = await bcrypt.genSalt(12);
    this.password = await bcrypt.hash(this.password, salt);
    next();
  } catch (error) {
    next(error);
  }
});

// Compare password method
userSchema.methods.comparePassword = async function(candidatePassword) {
  return await bcrypt.compare(candidatePassword, this.password);
};

module.exports = mongoose.model('User', userSchema);
