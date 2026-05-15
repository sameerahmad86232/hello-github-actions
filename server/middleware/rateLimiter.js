const rateLimit = require('express-rate-limit');

// General API rate limiter
const apiLimiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 100, // Limit each IP to 100 requests per windowMs
  message: {
    error: 'Too many requests from this IP, please try again after 15 minutes'
  },
  standardHeaders: true,
  legacyHeaders: false,
});

// Auth endpoints rate limiter (stricter)
const authLimiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 5, // Limit each IP to 5 login/register attempts per windowMs
  message: {
    error: 'Too many authentication attempts, please try again after 15 minutes'
  },
  skipSuccessfulRequests: true,
});

// Workflow execution rate limiter (based on subscription)
const executionLimiter = rateLimit({
  windowMs: 60 * 60 * 1000, // 1 hour
  max: (req) => {
    // Different limits based on subscription tier
    const user = req.user;
    if (!user) return 5; // Unauthenticated
    
    // These would be fetched from user's subscription
    const limits = {
      free: 10,
      pro: 100,
      enterprise: 1000
    };
    
    return limits[user.subscription?.plan] || limits.free;
  },
  keyGenerator: (req) => req.user?.userId || req.ip,
  message: {
    error: 'Execution limit reached. Please upgrade your plan or wait until the next hour.'
  },
});

// Export middleware
const rateLimiter = apiLimiter;

module.exports = {
  rateLimiter,
  apiLimiter,
  authLimiter,
  executionLimiter
};
