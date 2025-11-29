/**
 * NutriScan Frontend Observability Setup
 * 
 * Configures PostHog for product analytics and Sentry for error tracking.
 * Both services are gated behind environment variables for cost control.
 */

import * as Sentry from '@sentry/react'
import posthog from 'posthog-js'

// Environment variables (set these in .env file)
const POSTHOG_KEY = import.meta.env.VITE_POSTHOG_KEY
const POSTHOG_HOST = import.meta.env.VITE_POSTHOG_HOST || 'https://us.i.posthog.com'
const SENTRY_DSN = import.meta.env.VITE_SENTRY_DSN
const ENVIRONMENT = import.meta.env.MODE || 'development'

/**
 * Initialize observability services based on environment configuration.
 * Only initializes in production to avoid tracking development noise.
 */
export function initializeObservability(): void {
  console.log('🔧 Initializing observability services...')
  
  // Initialize Sentry for error tracking
  if (SENTRY_DSN) {
    try {
      Sentry.init({
        dsn: SENTRY_DSN,
        environment: ENVIRONMENT,
        
        // Integrations
        integrations: [
          Sentry.browserTracingIntegration(),
          Sentry.replayIntegration({
            // Capture 10% of sessions in production for debugging
            sessionSampleRate: ENVIRONMENT === 'production' ? 0.1 : 1.0,
            // Capture 100% of sessions with errors
            errorSampleRate: 1.0,
          }),
        ],
        
        // Performance monitoring
        tracesSampleRate: ENVIRONMENT === 'production' ? 0.1 : 1.0,
        
        // Release tracking
        release: `nutriscan-frontend@${import.meta.env.VITE_APP_VERSION || '1.0.0'}`,
        
        // Filter out noisy errors
        beforeSend(event) {
          // Filter out development/extension errors
          if (event.exception) {
            const error = event.exception.values?.[0]
            if (error?.value?.includes('extension')) {
              return null // Don't send browser extension errors
            }
          }
          return event
        },
      })
      
      // Set user context for better debugging
      Sentry.setContext('app', {
        name: 'NutriScan Web Console',
        version: import.meta.env.VITE_APP_VERSION || '1.0.0',
        environment: ENVIRONMENT,
      })
      
      console.log('✅ Sentry initialized for error tracking')
    } catch (error) {
      console.warn('⚠️ Failed to initialize Sentry:', error)
    }
  } else {
    console.log('ℹ️ Sentry not configured (VITE_SENTRY_DSN missing)')
  }
  
  // Initialize PostHog for product analytics
  // Only in production to avoid dev noise and conserve quota
  if (POSTHOG_KEY && !import.meta.env.DEV) {
    try {
      posthog.init(POSTHOG_KEY, {
        api_host: POSTHOG_HOST,
        
        // Privacy settings
        capture_pageview: true,
        capture_pageleave: true,
        
        // Reduce data collection for cost control
        session_recording: {
          enabled: true,
          sample_rate: 0.05, // Only record 5% of sessions
        },
        
        // Feature flags
        bootstrap: {
          distinctID: 'anonymous',
        },
        
        // Debug mode in development
        loaded: (posthog) => {
          if (import.meta.env.DEV) {
            posthog.debug()
          }
        },
      })
      
      // Set initial context
      posthog.register({
        app_version: import.meta.env.VITE_APP_VERSION || '1.0.0',
        environment: ENVIRONMENT,
      })
      
      console.log('✅ PostHog initialized for analytics')
    } catch (error) {
      console.warn('⚠️ Failed to initialize PostHog:', error)
    }
  } else {
    if (!POSTHOG_KEY) {
      console.log('ℹ️ PostHog not configured (VITE_POSTHOG_KEY missing)')
    } else if (import.meta.env.DEV) {
      console.log('ℹ️ PostHog disabled in development mode to avoid tracking noise')
    }
  }
}

/**
 * Track custom events for product analytics.
 * Only sends events if PostHog is initialized.
 */
export function trackEvent(eventName: string, properties?: Record<string, any>): void {
  if (posthog.__loaded) {
    posthog.capture(eventName, {
      timestamp: new Date().toISOString(),
      ...properties,
    })
  }
}

/**
 * Track scan events with structured data for analytics.
 */
export function trackScanEvent(eventType: 'scan_started' | 'scan_completed' | 'scan_failed', data?: {
  scanId?: string
  status?: string
  verdict?: string
  processingTime?: number
  ocrConfidence?: number
  userAge?: number
  dietaryRestrictions?: string[]
}): void {
  trackEvent(`nutriscan_${eventType}`, {
    category: 'scan',
    ...data,
  })
}

/**
 * Track user interactions for UX optimization.
 */
export function trackInteraction(action: string, element?: string, context?: Record<string, any>): void {
  trackEvent('user_interaction', {
    action,
    element,
    category: 'ui',
    ...context,
  })
}

/**
 * Report errors to Sentry with additional context.
 */
export function reportError(error: Error, context?: Record<string, any>): void {
  if (SENTRY_DSN) {
    Sentry.withScope((scope) => {
      if (context) {
        Object.entries(context).forEach(([key, value]) => {
          scope.setContext(key, value)
        })
      }
      Sentry.captureException(error)
    })
  }
  
  // Also log to console for development
  console.error('NutriScan Error:', error, context)
}

/**
 * Set user context for better debugging and analytics.
 */
export function setUserContext(user: {
  id?: string
  ageMonths?: number
  region?: string
  dietaryRestrictions?: string[]
}): void {
  // Set Sentry user context
  if (SENTRY_DSN) {
    Sentry.setUser({
      id: user.id || 'anonymous',
      ...user,
    })
  }
  
  // Set PostHog user properties
  if (posthog.__loaded) {
    posthog.identify(user.id || 'anonymous', {
      age_months: user.ageMonths,
      region: user.region,
      dietary_restrictions: user.dietaryRestrictions,
    })
  }
}

/**
 * Performance monitoring utilities.
 */
export class PerformanceTracker {
  private static timers: Map<string, number> = new Map()
  
  static start(label: string): void {
    this.timers.set(label, performance.now())
  }
  
  static end(label: string, additionalData?: Record<string, any>): number {
    const startTime = this.timers.get(label)
    if (!startTime) {
      console.warn(`Performance timer '${label}' was not started`)
      return 0
    }
    
    const duration = performance.now() - startTime
    this.timers.delete(label)
    
    // Track performance metrics
    trackEvent('performance_measurement', {
      label,
      duration_ms: Math.round(duration),
      category: 'performance',
      ...additionalData,
    })
    
    return duration
  }
}

export default {
  initializeObservability,
  trackEvent,
  trackScanEvent,
  trackInteraction,
  reportError,
  setUserContext,
  PerformanceTracker,
}