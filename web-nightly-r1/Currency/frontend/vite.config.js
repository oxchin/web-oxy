/*
 * Kconvert - Vite Build Configuration
 * 
 * Copyright (c) 2025 Team 6
 * All rights reserved.
 */

import { defineConfig, loadEnv } from 'vite'
import { visualizer } from 'rollup-plugin-visualizer'
import replace from '@rollup/plugin-replace'
import { resolve } from 'path'
import swc from '@vitejs/plugin-react-swc'

// https://vitejs.dev/config/
export default defineConfig(({ command, mode }) => {
  const env = loadEnv(mode, process.cwd(), '')
  const isProduction = mode === 'production'
  const isAnalyze = mode === 'analyze'
  
  return {
    root: '.',
    base: './',
    
    // Server configuration for development
    server: {
      port: 3000,
      strictPort: false, // Allow fallback ports
      host: '0.0.0.0',
      open: false,
      cors: true,
      hmr: {
        overlay: true,
        port: 24678 // Dedicated HMR port
      },
      fs: {
        strict: false // Allow serving files outside root
      },
      // Warm up frequently used files
      warmup: {
        clientFiles: ['./main.js', './style.css', './utils/*.js']
      }
    },
    
    // Preview configuration
    preview: {
      port: 4173,
      strictPort: true,
      host: '0.0.0.0',
      open: false
    },
    
    // Plugin configuration
    plugins: [
      // SWC plugin for turbo mode
      ...(process.env.VITE_USE_SWC === 'true' ? [
        swc({
          // SWC options for maximum performance
          swcOptions: {
            jsc: {
              target: 'es2022',
              parser: {
                syntax: 'ecmascript',
                jsx: false,
                dynamicImport: true,
                privateMethod: true,
                functionBind: false,
                exportDefaultFrom: true,
                exportNamespaceFrom: true,
                decorators: false,
                decoratorsBeforeExport: true,
                topLevelAwait: true,
                importMeta: true
              },
              transform: {
                react: {
                  runtime: 'automatic',
                  development: !isProduction,
                  refresh: !isProduction
                }
              },
              minify: {
                compress: isProduction,
                mangle: isProduction
              }
            },
            minify: isProduction
          }
        })
      ] : []),
      
      // Environment variable replacement
      replace({
        __MODE__: JSON.stringify(mode),
        __BUILD_TIME__: JSON.stringify(new Date().toISOString()),
        preventAssignment: true
      }),
      
      // Bundle analyzer (only in analyze mode)
      ...(isAnalyze ? [
        visualizer({
          filename: 'dist/stats.html',
          open: true,
          gzipSize: true,
          brotliSize: true
        })
      ] : [])
    ],
    
    // Build configuration optimized for ultimate performance
    build: {
      outDir: 'dist',
      assetsDir: 'assets',
      sourcemap: isProduction ? 'hidden' : true, // Hidden sourcemaps for production
      minify: isProduction ? 'terser' : false, // Use esbuild for dev builds
      
      // Enable experimental features for better performance
      reportCompressedSize: false, // Faster builds
      cssMinify: isProduction ? 'lightningcss' : false,
      
      // Advanced Terser options for ultimate optimization
      terserOptions: isProduction ? {
        compress: {
          drop_console: true,
          drop_debugger: true,
          pure_funcs: ['console.log', 'console.info', 'console.debug', 'console.warn'],
          passes: 3, // More aggressive optimization
          unsafe_arrows: true,
          unsafe_methods: true,
          unsafe_proto: true,
          keep_fargs: false,
          toplevel: true
        },
        mangle: {
          safari10: true,
          toplevel: true,
          properties: {
            regex: /^_/
          }
        },
        format: {
          safari10: true,
          comments: false
        }
      } : {},
      
      // Rollup options for chunking strategy
      rollupOptions: {
        input: 'index.html',
        output: {
          // Optimized chunking strategy
          chunkFileNames: isProduction 
            ? 'assets/js/[name]-[hash:8].js'
            : 'assets/js/[name].js',
          entryFileNames: isProduction
            ? 'assets/js/[name]-[hash:8].js' 
            : 'assets/js/[name].js',
          assetFileNames: isProduction
            ? 'assets/[ext]/[name]-[hash:8].[ext]'
            : 'assets/[ext]/[name].[ext]',
          
          // Manual chunk splitting for better caching
          manualChunks: isProduction ? {
            vendor: ['chart.js', '@fontsource/inter', '@fortawesome/fontawesome-free'],
            utils: ['./utils/crypto-icons.js', './utils/flags.js', './utils/time.js']
          } : undefined,
          
          // Compact output
          compact: isProduction,
          
          // Optimize imports
          hoistTransitiveImports: false
        }
      },
      
      // Ultra-modern target for better optimization
      target: 'es2022',
      
      // Optimized chunk size warnings
      chunkSizeWarningLimit: 800,
      
      // Smart CSS code splitting
      cssCodeSplit: isProduction,
      
      // Optimized asset inlining
      assetsInlineLimit: 8192, // Inline more small assets
      
      // Enable module preload polyfill
      modulePreload: {
        polyfill: true
      },
      
      // Experimental: Use SWC for faster builds (if available)
      ...(process.env.VITE_USE_SWC === 'true' && {
        minify: 'swc'
      })
    },
    
    // Enhanced ESBuild configuration
    esbuild: {
      target: 'es2022',
      drop: isProduction ? ['console', 'debugger'] : [],
      legalComments: 'none',
      treeShaking: true,
      minifyIdentifiers: isProduction,
      minifySyntax: isProduction,
      minifyWhitespace: isProduction,
      // Use native ESBuild for faster builds
      platform: 'browser',
      format: 'esm'
    },
    
    // CSS configuration
    css: {
      devSourcemap: !isProduction,
      preprocessorOptions: {
        css: {
          charset: false
        }
      }
    },
    
    // Advanced dependency optimization
    optimizeDeps: {
      include: [
        '@fortawesome/fontawesome-free',
        'country-flag-icons'
      ],
      exclude: [
        'chart.js', // Keep as dynamic import for code splitting
        'lottie-web'
      ],
      // Force optimization of specific deps
      force: isProduction,
      // ESBuild options for deps
      esbuildOptions: {
        target: 'es2022',
        supported: {
          'top-level-await': true
        }
      }
    },
    
    // Define global constants
    define: {
      __APP_VERSION__: JSON.stringify(process.env.npm_package_version || '2.0.0'),
      __BUILD_MODE__: JSON.stringify(mode)
    },
    
    // Enhanced resolve configuration
    resolve: {
      alias: {
        '@': resolve(__dirname, './'),
        '@utils': resolve(__dirname, './utils'),
        '@assets': resolve(__dirname, './assets')
      },
      // Optimize extension resolution
      extensions: ['.js', '.mjs', '.json', '.css']
    },
    
    // Worker configuration for better performance
    worker: {
      format: 'es',
      plugins: () => []
    },
    
    // Experimental features for ultimate performance
    experimental: {
      renderBuiltUrl(filename, { hostType }) {
        if (hostType === 'js') {
          return { js: `'${filename}'` }
        } else {
          return { relative: true }
        }
      }
    }
  }
})
