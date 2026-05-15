const { chromium } = require('playwright');
const { addExtra } = require('playwright-extra');
const stealth = require('puppeteer-extra-plugin-stealth');
const winston = require('winston');
const Execution = require('../models/Execution');
const Workflow = require('../models/Workflow');

// Configure logger
const logger = winston.createLogger({
  level: 'info',
  format: winston.format.combine(
    winston.format.timestamp(),
    winston.format.json()
  ),
  transports: [
    new winston.transports.File({ filename: 'logs/automation.log' })
  ]
});

class BrowserAutomationService {
  constructor() {
    this.browser = null;
    this.page = null;
    this.context = null;
  }

  // Initialize browser with anti-detection
  async launchBrowser(options = {}) {
    const {
      headless = true,
      proxy = null,
      viewport = { width: 1920, height: 1080 }
    } = options;

    try {
      // Add stealth plugin to Chromium
      const chromiumExtra = addExtra(chromium);
      chromiumExtra.use(stealth());

      const launchOptions = {
        headless: headless ? 'new' : false,
        args: [
          '--no-sandbox',
          '--disable-setuid-sandbox',
          '--disable-dev-shm-usage',
          '--disable-accelerated-2d-canvas',
          '--no-first-run',
          '--no-zygote',
          '--disable-gpu'
        ]
      };

      if (proxy) {
        launchOptions.proxy = proxy;
      }

      this.browser = await chromiumExtra.launch(launchOptions);
      
      this.context = await this.browser.newContext({
        viewport,
        userAgent: this.getRandomUserAgent(),
        locale: 'en-US',
        timezoneId: 'America/New_York'
      });

      this.page = await this.context.newPage();

      // Block unnecessary resources for faster loading
      await this.page.route('**/*', (route) => {
        if (['image', 'stylesheet', 'font'].includes(route.request().resourceType())) {
          // Optionally block based on settings
          route.continue();
        } else {
          route.continue();
        }
      });

      logger.info('Browser launched successfully');
      return true;
    } catch (error) {
      logger.error('Failed to launch browser:', error);
      throw error;
    }
  }

  // Get random user agent for fingerprint randomization
  getRandomUserAgent() {
    const userAgents = [
      'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
      'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
      'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/119.0',
      'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15'
    ];
    return userAgents[Math.floor(Math.random() * userAgents.length)];
  }

  // Smart selector finding with self-healing
  async findElement(selector, fingerprints = [], timeout = 5000) {
    try {
      // Try primary selector first
      const element = await this.page.waitForSelector(selector, { timeout, state: 'visible' });
      return { element, selector, selfHealingApplied: false };
    } catch (primaryError) {
      logger.warn(`Primary selector failed: ${selector}, attempting self-healing...`);

      // Try alternative fingerprints
      for (const fingerprint of fingerprints) {
        try {
          if (fingerprint.css) {
            const element = await this.page.waitForSelector(fingerprint.css, { timeout: 2000, state: 'visible' });
            logger.info(`Self-healing successful with CSS: ${fingerprint.css}`);
            return { 
              element, 
              selector: fingerprint.css, 
              selfHealingApplied: true,
              selfHealingDetails: {
                originalSelector: selector,
                newSelector: fingerprint.css,
                confidence: 0.9
              }
            };
          }
          
          if (fingerprint.xpath) {
            const element = await this.page.waitForSelector(`xpath=${fingerprint.xpath}`, { timeout: 2000, state: 'visible' });
            logger.info(`Self-healing successful with XPath: ${fingerprint.xpath}`);
            return { 
              element, 
              selector: `xpath=${fingerprint.xpath}`, 
              selfHealingApplied: true,
              selfHealingDetails: {
                originalSelector: selector,
                newSelector: `xpath=${fingerprint.xpath}`,
                confidence: 0.85
              }
            };
          }

          if (fingerprint.text) {
            const element = await this.page.getByText(fingerprint.text).first();
            if (element) {
              logger.info(`Self-healing successful with text: ${fingerprint.text}`);
              return { 
                element, 
                selector: `text=${fingerprint.text}`, 
                selfHealingApplied: true,
                selfHealingDetails: {
                  originalSelector: selector,
                  newSelector: `text=${fingerprint.text}`,
                  confidence: 0.8
                }
              };
            }
          }
        } catch (fpError) {
          continue; // Try next fingerprint
        }
      }

      // If all fingerprints fail, try AI-powered similarity search
      const aiSelector = await this.findWithAI(selector, fingerprints);
      if (aiSelector) {
        return aiSelector;
      }

      throw new Error(`Element not found: ${selector}`);
    }
  }

  // AI-powered element finding (fallback)
  async findWithAI(originalSelector, fingerprints) {
    try {
      // Get all clickable elements and find similar ones
      const candidates = await this.page.evaluate(() => {
        const elements = Array.from(document.querySelectorAll('button, a, input, [role="button"]'));
        return elements.map(el => ({
          text: el.textContent?.trim().substring(0, 100),
          ariaLabel: el.getAttribute('aria-label'),
          id: el.id,
          className: el.className,
          tagName: el.tagName
        })).filter(e => e.text || e.ariaLabel);
      });

      // Simple heuristic matching (in production, use LLM)
      const originalText = fingerprints.find(f => f.text)?.text || '';
      const match = candidates.find(c => 
        c.text?.toLowerCase().includes(originalText.toLowerCase()) ||
        c.ariaLabel?.toLowerCase().includes(originalText.toLowerCase())
      );

      if (match) {
        logger.info(`AI fallback found match: ${match.text || match.ariaLabel}`);
        const element = await this.page.getByText(match.text || match.ariaLabel).first();
        return {
          element,
          selector: `text=${match.text || match.ariaLabel}`,
          selfHealingApplied: true,
          selfHealingDetails: {
            originalSelector: originalSelector,
            newSelector: `text=${match.text || match.ariaLabel}`,
            confidence: 0.7
          }
        };
      }
    } catch (error) {
      logger.error('AI fallback failed:', error);
    }
    return null;
  }

  // Execute workflow steps
  async executeWorkflow(workflowId, executionId) {
    const workflow = await Workflow.findById(workflowId);
    const execution = await Execution.findById(executionId);

    if (!workflow || !execution) {
      throw new Error('Workflow or execution not found');
    }

    try {
      await execution.updateOne({ status: 'running', startedAt: new Date() });
      
      // Launch browser
      await this.launchBrowser({
        headless: workflow.settings.headless,
        proxy: workflow.settings.proxy.enabled ? workflow.settings.proxy.config : null
      });

      const results = [];
      let extractedData = {};

      for (const step of workflow.steps) {
        const stepResult = await this.executeStep(step, workflow.variables);
        results.push(stepResult);

        if (stepResult.status === 'failed' && !step.condition) {
          throw new Error(`Step ${step.id} failed: ${stepResult.errorMessage}`);
        }

        if (step.type === 'extract') {
          extractedData = { ...extractedData, ...stepResult.output };
        }
      }

      // Update execution with results
      await execution.updateOne({
        status: 'completed',
        completedAt: new Date(),
        steps: results,
        extractedData,
        metrics: {
          pagesVisited: results.filter(r => r.stepType === 'navigate').length,
          clicksPerformed: results.filter(r => r.stepType === 'click').length,
          dataPointsExtracted: Object.keys(extractedData).length
        }
      });

      logger.info(`Workflow ${workflowId} executed successfully`);
      return { success: true, data: extractedData };
    } catch (error) {
      logger.error(`Workflow execution failed: ${error.message}`);
      
      await execution.updateOne({
        status: 'failed',
        completedAt: new Date(),
        errors: [{
          message: error.message,
          stack: error.stack,
          timestamp: new Date()
        }]
      });

      if (workflow.settings.screenshotOnFailure && this.page) {
        const screenshotPath = `screenshots/${executionId}_error.png`;
        await this.page.screenshot({ path: screenshotPath, fullPage: true });
        // Upload to S3 in production
      }

      throw error;
    } finally {
      await this.closeBrowser();
    }
  }

  // Execute individual step
  async executeStep(step, variables = []) {
    const startTime = Date.now();
    let result = {
      stepId: step.id,
      stepType: step.type,
      status: 'pending',
      startedAt: new Date()
    };

    try {
      switch (step.type) {
        case 'navigate':
          await this.page.goto(step.url, { waitUntil: 'networkidle', timeout: step.timeout });
          result.status = 'completed';
          break;

        case 'click':
          const clickElement = await this.findElement(step.selector, step.selector?.fingerprints, step.timeout);
          await clickElement.element.click();
          result.status = 'completed';
          if (clickElement.selfHealingApplied) {
            result.selfHealingApplied = true;
            result.selfHealingDetails = clickElement.selfHealingDetails;
          }
          break;

        case 'type':
          const typeElement = await this.findElement(step.selector, step.selector?.fingerprints, step.timeout);
          const value = this.replaceVariables(step.value, variables);
          await typeElement.element.fill(value);
          result.status = 'completed';
          break;

        case 'wait':
          await this.page.waitForTimeout(step.timeout || 1000);
          result.status = 'completed';
          break;

        case 'extract':
          const extracted = {};
          for (const field of step.extract.fields) {
            const extractElement = await this.findElement(field.selector, [], step.timeout);
            if (field.type === 'text') {
              extracted[field.name] = await extractElement.element.textContent();
            } else if (field.type === 'html') {
              extracted[field.name] = await extractElement.element.innerHTML();
            } else if (field.type === 'attribute') {
              extracted[field.name] = await extractElement.element.getAttribute(field.attribute);
            }
          }
          result.status = 'completed';
          result.output = extracted;
          break;

        case 'screenshot':
          const screenshotBuffer = await this.page.screenshot({ fullPage: true });
          result.status = 'completed';
          result.output = { screenshot: screenshotBuffer.toString('base64') };
          break;

        default:
          result.status = 'skipped';
          result.errorMessage = `Unknown step type: ${step.type}`;
      }

      result.completedAt = new Date();
      return result;
    } catch (error) {
      result.status = 'failed';
      result.errorMessage = error.message;
      result.completedAt = new Date();
      
      // Retry logic
      if (step.retryCount < step.maxRetries) {
        step.retryCount++;
        logger.info(`Retrying step ${step.id} (${step.retryCount}/${step.maxRetries})`);
        await this.page.waitForTimeout(1000);
        return this.executeStep(step, variables);
      }
      
      return result;
    }
  }

  // Replace variables in strings
  replaceVariables(text, variables) {
    if (!text || !variables) return text;
    
    let result = text;
    for (const variable of variables) {
      const regex = new RegExp(`\\{\\{${variable.name}\\}\\}`, 'g');
      result = result.replace(regex, variable.value);
    }
    return result;
  }

  // Close browser
  async closeBrowser() {
    try {
      if (this.browser) {
        await this.browser.close();
        this.browser = null;
        this.page = null;
        this.context = null;
        logger.info('Browser closed');
      }
    } catch (error) {
      logger.error('Error closing browser:', error);
    }
  }
}

module.exports = new BrowserAutomationService();
