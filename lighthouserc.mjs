// Lighthouse CI Configuration - SISMOBI v3.2.0
export default {
  ci: {
    // Build configuration
    collect: {
      url: [
        'http://localhost:5174',
        'http://localhost:5174/properties',
        'http://localhost:5174/tenants',
        'http://localhost:5174/transactions',
        'http://localhost:5174/reports'
      ],
      startServerCommand: 'cd frontend && npm run preview',
      startServerReadyPattern: 'Local:',
      startServerReadyTimeout: 30000,
      numberOfRuns: 3,
      settings: {
        chromeFlags: '--no-sandbox --headless',
        preset: 'desktop'
      }
    },
    
    // Upload results to temporary server (for development)
    upload: {
      target: 'temporary-public-storage',
    },
    
    // Performance budgets and assertions
    assert: {
      assertions: {
        // Performance thresholds
        'categories:performance': ['warn', { minScore: 0.8 }],
        'categories:accessibility': ['error', { minScore: 0.9 }],
        'categories:best-practices': ['warn', { minScore: 0.8 }],
        'categories:seo': ['warn', { minScore: 0.8 }],
        
        // Core Web Vitals
        'first-contentful-paint': ['warn', { maxNumericValue: 2000 }],
        'largest-contentful-paint': ['warn', { maxNumericValue: 3000 }],
        'cumulative-layout-shift': ['warn', { maxNumericValue: 0.1 }],
        'total-blocking-time': ['warn', { maxNumericValue: 300 }],
        
        // Network and resource optimization
        'unused-javascript': ['warn', { maxNumericValue: 40000 }],
        'unused-css-rules': ['warn', { maxNumericValue: 20000 }],
        'render-blocking-resources': ['warn', { maxNumericValue: 500 }]
      }
    },
    
    // Server configuration for CI
    server: {
      port: 9001,
      storage: {
        storageMethod: 'sql',
        sqlDialect: 'sqlite',
        sqlDatabasePath: './lhci.db'
      }
    }
  }
};