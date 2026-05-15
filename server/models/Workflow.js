const mongoose = require('mongoose');

const workflowSchema = new mongoose.Schema({
  name: {
    type: String,
    required: true,
    trim: true
  },
  description: String,
  user: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'User',
    required: true
  },
  workspace: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'Workspace'
  },
  steps: [{
    id: String,
    type: {
      type: String,
      enum: ['click', 'type', 'navigate', 'wait', 'extract', 'condition', 'loop', 'screenshot', 'custom'],
      required: true
    },
    selector: {
      type: String,
      fingerprints: [{
        css: String,
        xpath: String,
        text: String,
        ariaLabel: String,
        position: { x: Number, y: Number }
      }]
    },
    value: String, // For type inputs
    url: String, // For navigate
    timeout: { type: Number, default: 5000 },
    options: Object, // Additional options
    condition: {
      type: String, // JavaScript expression for conditions
      then: [String], // Step IDs to execute if true
      else: [String] // Step IDs to execute if false
    },
    loop: {
      type: String, // 'foreach', 'while', 'until'
      selector: String,
      maxIterations: { type: Number, default: 100 }
    },
    extract: {
      fields: [{
        name: String,
        selector: String,
        type: { type: String, enum: ['text', 'html', 'attribute', 'image'] },
        attribute: String // For attribute type
      }]
    },
    retryCount: { type: Number, default: 0 },
    maxRetries: { type: Number, default: 3 }
  }],
  variables: [{
    name: String,
    value: String,
    type: { type: String, enum: ['string', 'number', 'boolean', 'array', 'object'] }
  }],
  schedule: {
    enabled: { type: Boolean, default: false },
    cron: String, // Cron expression
    timezone: { type: String, default: 'UTC' },
    lastRun: Date,
    nextRun: Date
  },
  settings: {
    headless: { type: Boolean, default: true },
    proxy: {
      enabled: Boolean,
      provider: String,
      config: Object
    },
    antiDetection: { type: Boolean, default: true },
    screenshotOnFailure: { type: Boolean, default: true },
    videoRecording: { type: Boolean, default: false },
    timeout: { type: Number, default: 300000 } // 5 minutes
  },
  stats: {
    totalRuns: { type: Number, default: 0 },
    successfulRuns: { type: Number, default: 0 },
    failedRuns: { type: Number, default: 0 },
    averageDuration: Number,
    lastRunAt: Date,
    lastRunStatus: String
  },
  isTemplate: { type: Boolean, default: false },
  templateCategory: String,
  templateTags: [String],
  version: { type: Number, default: 1 },
  createdAt: { type: Date, default: Date.now },
  updatedAt: { type: Date, default: Date.now }
});

// Update timestamp on save
workflowSchema.pre('save', function(next) {
  this.updatedAt = Date.now();
  next();
});

// Index for efficient queries
workflowSchema.index({ user: 1, createdAt: -1 });
workflowSchema.index({ isTemplate: 1, templateCategory: 1 });

module.exports = mongoose.model('Workflow', workflowSchema);
