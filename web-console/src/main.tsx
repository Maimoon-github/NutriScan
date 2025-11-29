import React from 'react'
import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.tsx'
import { setupI18n } from './i18n'
import { initializeObservability } from './lib/observability'

// Initialize i18n and document direction before rendering
setupI18n()

// Initialize observability services (PostHog, Sentry)
initializeObservability()

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <App />
  </StrictMode>,
)
