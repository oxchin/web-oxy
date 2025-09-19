/*
 * Kconvert - Bun.js Optimization Configuration
 * Ultimate performance configuration for development and production
 * 
 * Copyright (c) 2025 Team 6
 * All rights reserved.
 */

export default {
  // Preload configuration for faster startup
  preload: [
    "./main.js",
    "./style.css"
  ],
  
  // Install configuration
  install: {
    // Use faster registry
    registry: "https://registry.npmjs.org/",
    
    // Optimize dependency resolution
    cache: {
      dir: ".bun-cache",
      disable: false
    },
    
    // Faster lockfile operations
    lockfile: {
      save: true,
      print: "yarn"
    },
    
    // Production optimizations
    production: process.env.NODE_ENV === "production",
    
    // Peer dependency handling
    peer: true,
    
    // Optional dependency handling
    optional: true,
    
    // Frozen lockfile for CI/CD
    frozenLockfile: process.env.CI === "true"
  },
  
  // Runtime optimizations
  run: {
    // Use Bun's native runtime
    bun: true,
    
    // Hot reload configuration
    hot: process.env.NODE_ENV !== "production",
    
    // Memory optimizations
    smol: false, // Use full performance mode
    
    // Enable experimental features
    experimental: {
      macros: true,
      jsx: true
    }
  },
  
  // Build optimizations
  build: {
    // Target modern browsers
    target: "browser",
    
    // Output format
    format: "esm",
    
    // Minification
    minify: process.env.NODE_ENV === "production",
    
    // Source maps
    sourcemap: process.env.NODE_ENV !== "production" ? "external" : false,
    
    // Splitting
    splitting: true,
    
    // Tree shaking
    treeShaking: true,
    
    // External dependencies (let Vite handle bundling)
    external: [
      "vite",
      "rollup"
    ]
  },
  
  // Test configuration
  test: {
    // Use Bun's built-in test runner
    preload: ["./test-setup.js"],
    
    // Coverage
    coverage: {
      enabled: false // Disable for faster builds
    }
  },
  
  // Development server optimizations
  serve: {
    // Static file serving
    static: "./dist",
    
    // Compression
    compression: true,
    
    // CORS
    cors: true,
    
    // Hot reload
    hot: true
  }
}
