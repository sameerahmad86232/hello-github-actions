const express = require('express');
const router = express.Router();
const { authenticateJWT, authorize } = require('../middleware/auth');
const { asyncHandler, AppError } = require('../middleware/errorHandler');
const Workflow = require('../models/Workflow');
const Execution = require('../models/Execution');

// Get all workflows for user
router.get('/', authenticateJWT, asyncHandler(async (req, res) => {
  const { status, page = 1, limit = 20 } = req.query;
  
  const query = { user: req.user.userId };
  if (status) query['stats.lastRunStatus'] = status;
  
  const workflows = await Workflow.find(query)
    .sort({ createdAt: -1 })
    .limit(limit * 1)
    .skip((page - 1) * limit);
  
  const count = await Workflow.countDocuments(query);
  
  res.json({
    workflows,
    totalPages: Math.ceil(count / limit),
    currentPage: page,
    total: count
  });
}));

// Create new workflow
router.post('/', authenticateJWT, asyncHandler(async (req, res) => {
  const { name, description, steps, variables, settings } = req.body;
  
  if (!name || !steps || !Array.isArray(steps)) {
    throw new AppError('Name and steps are required', 400, 'VALIDATION_ERROR');
  }
  
  const workflow = new Workflow({
    name,
    description,
    steps,
    variables: variables || [],
    settings: settings || {},
    user: req.user.userId
  });
  
  await workflow.save();
  
  res.status(201).json({
    message: 'Workflow created successfully',
    workflow
  });
}));

// Get single workflow
router.get('/:id', authenticateJWT, asyncHandler(async (req, res) => {
  const workflow = await Workflow.findOne({
    _id: req.params.id,
    user: req.user.userId
  });
  
  if (!workflow) {
    throw new AppError('Workflow not found', 404, 'NOT_FOUND');
  }
  
  res.json({ workflow });
}));

// Update workflow
router.put('/:id', authenticateJWT, asyncHandler(async (req, res) => {
  const { name, description, steps, variables, settings, schedule } = req.body;
  
  const workflow = await Workflow.findOne({
    _id: req.params.id,
    user: req.user.userId
  });
  
  if (!workflow) {
    throw new AppError('Workflow not found', 404, 'NOT_FOUND');
  }
  
  // Update fields
  if (name) workflow.name = name;
  if (description !== undefined) workflow.description = description;
  if (steps) workflow.steps = steps;
  if (variables) workflow.variables = variables;
  if (settings) workflow.settings = { ...workflow.settings, ...settings };
  if (schedule) workflow.schedule = { ...workflow.schedule, ...schedule };
  
  workflow.version += 1;
  await workflow.save();
  
  res.json({
    message: 'Workflow updated successfully',
    workflow
  });
}));

// Delete workflow
router.delete('/:id', authenticateJWT, asyncHandler(async (req, res) => {
  const workflow = await Workflow.findOneAndDelete({
    _id: req.params.id,
    user: req.user.userId
  });
  
  if (!workflow) {
    throw new AppError('Workflow not found', 404, 'NOT_FOUND');
  }
  
  // Also delete associated executions
  await Execution.deleteMany({ workflow: req.params.id });
  
  res.json({ message: 'Workflow deleted successfully' });
}));

// Run workflow immediately
router.post('/:id/run', authenticateJWT, asyncHandler(async (req, res) => {
  const workflow = await Workflow.findOne({
    _id: req.params.id,
    user: req.user.userId
  });
  
  if (!workflow) {
    throw new AppError('Workflow not found', 404, 'NOT_FOUND');
  }
  
  // Create execution record
  const execution = new Execution({
    workflow: workflow._id,
    user: req.user.userId,
    status: 'pending',
    trigger: 'manual'
  });
  
  await execution.save();
  
  // Here you would add the execution to the BullMQ queue
  // const job = await executionQueue.add('run-workflow', {
  //   executionId: execution._id,
  //   workflowId: workflow._id
  // });
  
  res.json({
    message: 'Workflow execution started',
    executionId: execution._id,
    status: 'pending'
  });
}));

// Get workflow execution history
router.get('/:id/executions', authenticateJWT, asyncHandler(async (req, res) => {
  const { page = 1, limit = 20, status } = req.query;
  
  const query = { workflow: req.params.id, user: req.user.userId };
  if (status) query.status = status;
  
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

module.exports = router;
