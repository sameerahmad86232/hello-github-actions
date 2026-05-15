const express = require('express');
const router = express.Router();
const { authenticateJWT } = require('../middleware/auth');
const { asyncHandler, AppError } = require('../middleware/errorHandler');
const Execution = require('../models/Execution');
const browserAutomationService = require('../services/browserAutomation');

// Get all executions
router.get('/', authenticateJWT, asyncHandler(async (req, res) => {
  const { status, workflow, page = 1, limit = 20 } = req.query;
  
  const query = { user: req.user.userId };
  if (status) query.status = status;
  if (workflow) query.workflow = workflow;
  
  const executions = await Execution.find(query)
    .sort({ createdAt: -1 })
    .limit(limit * 1)
    .skip((page - 1) * limit);
  
  const count = await Execution.countDocuments(query);
  
  res.json({
    executions,
    totalPages: Math.ceil(count / limit),
    currentPage: page,
    total: count
  });
}));

// Get single execution details
router.get('/:id', authenticateJWT, asyncHandler(async (req, res) => {
  const execution = await Execution.findOne({
    _id: req.params.id,
    user: req.user.userId
  }).populate('workflow');
  
  if (!execution) {
    throw new AppError('Execution not found', 404, 'NOT_FOUND');
  }
  
  res.json({ execution });
}));

// Cancel running execution
router.post('/:id/cancel', authenticateJWT, asyncHandler(async (req, res) => {
  const execution = await Execution.findOne({
    _id: req.params.id,
    user: req.user.userId
  });
  
  if (!execution) {
    throw new AppError('Execution not found', 404, 'NOT_FOUND');
  }
  
  if (execution.status !== 'running' && execution.status !== 'pending') {
    throw new AppError('Can only cancel running or pending executions', 400, 'INVALID_STATUS');
  }
  
  await execution.updateOne({ status: 'cancelled', completedAt: new Date() });
  
  // In production, remove from BullMQ queue here
  
  res.json({ message: 'Execution cancelled successfully' });
}));

// Retry failed execution
router.post('/:id/retry', authenticateJWT, asyncHandler(async (req, res) => {
  const execution = await Execution.findOne({
    _id: req.params.id,
    user: req.user.userId
  });
  
  if (!execution) {
    throw new AppError('Execution not found', 404, 'NOT_FOUND');
  }
  
  if (execution.status !== 'failed') {
    throw new AppError('Can only retry failed executions', 400, 'INVALID_STATUS');
  }
  
  // Create new execution record
  const newExecution = new Execution({
    workflow: execution.workflow,
    user: req.user.userId,
    status: 'pending',
    trigger: 'manual'
  });
  
  await newExecution.save();
  
  // Queue for execution
  // const job = await executionQueue.add('run-workflow', {
  //   executionId: newExecution._id,
  //   workflowId: execution.workflow
  // });
  
  res.json({
    message: 'Execution retry started',
    executionId: newExecution._id
  });
}));

// Export execution data
router.get('/:id/export/:format', authenticateJWT, asyncHandler(async (req, res) => {
  const { format } = req.params;
  const execution = await Execution.findOne({
    _id: req.params.id,
    user: req.user.userId
  });
  
  if (!execution) {
    throw new AppError('Execution not found', 404, 'NOT_FOUND');
  }
  
  if (!execution.extractedData || Object.keys(execution.extractedData).length === 0) {
    throw new AppError('No data to export', 400, 'NO_DATA');
  }
  
  let content, contentType, extension;
  
  switch (format.toLowerCase()) {
    case 'json':
      content = JSON.stringify(execution.extractedData, null, 2);
      contentType = 'application/json';
      extension = 'json';
      break;
    
    case 'csv':
      const rows = [];
      const headers = Object.keys(execution.extractedData);
      rows.push(headers.join(','));
      
      // Handle both single object and array of objects
      const dataArray = Array.isArray(execution.extractedData) 
        ? execution.extractedData 
        : [execution.extractedData];
      
      for (const item of dataArray) {
        const row = headers.map(h => {
          const value = item[h] || '';
          return `"${String(value).replace(/"/g, '""')}"`;
        });
        rows.push(row.join(','));
      }
      
      content = rows.join('\n');
      contentType = 'text/csv';
      extension = 'csv';
      break;
    
    default:
      throw new AppError('Unsupported format. Use json or csv', 400, 'UNSUPPORTED_FORMAT');
  }
  
  res.setHeader('Content-Type', contentType);
  res.setHeader('Content-Disposition', `attachment; filename="export_${execution._id}.${extension}"`);
  res.send(content);
}));

module.exports = router;
