const mongoose = require('mongoose');

const executionSchema = new mongoose.Schema({
  workflow: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'Workflow',
    required: true
  },
  user: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'User',
    required: true
  },
  status: {
    type: String,
    enum: ['pending', 'running', 'completed', 'failed', 'cancelled'],
    default: 'pending'
  },
  trigger: {
    type: String,
    enum: ['manual', 'schedule', 'api', 'webhook'],
    default: 'manual'
  },
  startedAt: Date,
  completedAt: Date,
  duration: Number, // in milliseconds
  steps: [{
    stepId: String,
    stepType: String,
    status: {
      type: String,
      enum: ['pending', 'running', 'completed', 'failed', 'skipped']
    },
    startedAt: Date,
    completedAt: Date,
    error: String,
    errorMessage: String,
    screenshot: String, // S3 URL if captured
    output: Object, // Extracted data or result
    retryCount: { type: Number, default: 0 },
    selfHealingApplied: { type: Boolean, default: false },
    selfHealingDetails: {
      originalSelector: String,
      newSelector: String,
      confidence: Number
    }
  }],
  extractedData: {
    type: Object,
    default: {}
  },
  exports: [{
    type: { type: String, enum: ['csv', 'json', 'google_sheets', 'airtable', 'notion', 'webhook'] },
    destination: String,
    status: { type: String, enum: ['pending', 'success', 'failed'] },
    url: String,
    error: String
  }],
  errors: [{
    stepId: String,
    message: String,
    stack: String,
    timestamp: Date,
    resolved: { type: Boolean, default: false }
  }],
  logs: [{
    level: { type: String, enum: ['info', 'warn', 'error', 'debug'] },
    message: String,
    timestamp: { type: Date, default: Date.now },
    metadata: Object
  }],
  metrics: {
    pagesVisited: { type: Number, default: 0 },
    clicksPerformed: { type: Number, default: 0 },
    dataPointsExtracted: { type: Number, default: 0 },
    screenshotsTaken: { type: Number, default: 0 }
  },
  browserInfo: {
    userAgent: String,
    viewport: { width: Number, height: Number },
    proxyUsed: String
  },
  videoRecording: String, // S3 URL
  creditsUsed: { type: Number, default: 1 }
});

// Calculate duration before saving
executionSchema.pre('save', function(next) {
  if (this.startedAt && this.completedAt) {
    this.duration = this.completedAt - this.startedAt;
  }
  next();
});

// Indexes for efficient queries
executionSchema.index({ workflow: 1, createdAt: -1 });
executionSchema.index({ user: 1, status: 1, createdAt: -1 });
executionSchema.index({ status: 1, createdAt: -1 }); // For monitoring queue

module.exports = mongoose.model('Execution', executionSchema);
