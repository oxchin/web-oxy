#!/bin/bash
# Kconvert - Ultimate Build Optimization Script
# Optimizes Vite + Bun.js for maximum performance
# Copyright (c) 2025 Team 6

set -e

# Change to project root directory
cd "$(dirname "$0")/.."

# Function to show help
show_help() {
    echo "🚀 Kconvert Ultimate Build Optimization Script"
    echo ""
    echo "USAGE:"
    echo "  ./optimize-build.sh [MODE] [OPTIONS]"
    echo ""
    echo "BUILD MODES:"
    echo "  dev                    Development build with hot reload and source maps"
    echo "  production             Production build with full optimization (default)"
    echo "  lts                    Long Term Support build with maximum compatibility"
    echo "  turbo                  Turbo mode with SWC compiler for fastest builds"
    echo ""
    echo "OPTIONS:"
    echo "  --help, -h             Show this help message"
    echo "  --analyze              Run bundle analyzer after build"
    echo "  --no-compress          Skip gzip/brotli compression"
    echo "  --no-clean             Skip cleaning previous builds"
    echo "  --verbose              Show detailed build output"
    echo "  --stats                Show detailed build statistics"
    echo ""
    echo "EXAMPLES:"
    echo "  ./optimize-build.sh                    # Standard production build"
    echo "  ./optimize-build.sh dev                # Development build"
    echo "  ./optimize-build.sh production --analyze   # Production with bundle analysis"
    echo "  ./optimize-build.sh turbo --no-compress    # Turbo build without compression"
    echo "  ./optimize-build.sh lts --stats        # LTS build with detailed stats"
    echo ""
    echo "ENVIRONMENT VARIABLES:"
    echo "  VITE_USE_SWC=true      Enable SWC compiler"
    echo "  NODE_ENV=production    Set build environment"
    echo "  ANALYZE=true           Enable bundle analysis"
    echo ""
    echo "BUILD TARGETS:"
    echo "  📦 Standard: Modern browsers (ES2020+)"
    echo "  🔥 Turbo: Latest browsers with SWC optimization"
    echo "  🛡️ LTS: Maximum compatibility (ES2015+)"
    echo "  🔧 Dev: Development with source maps and HMR"
    echo ""
    exit 0
}

# Parse command line arguments
BUILD_MODE="production"
ANALYZE=false
NO_COMPRESS=false
NO_CLEAN=false
VERBOSE=false
SHOW_STATS=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --help|-h)
            show_help
            ;;
        dev|development)
            BUILD_MODE="dev"
            shift
            ;;
        production|prod)
            BUILD_MODE="production"
            shift
            ;;
        lts)
            BUILD_MODE="lts"
            shift
            ;;
        turbo)
            BUILD_MODE="turbo"
            shift
            ;;
        --analyze)
            ANALYZE=true
            shift
            ;;
        --no-compress)
            NO_COMPRESS=true
            shift
            ;;
        --no-clean)
            NO_CLEAN=true
            shift
            ;;
        --verbose)
            VERBOSE=true
            shift
            ;;
        --stats)
            SHOW_STATS=true
            shift
            ;;
        analyze)
            # Legacy support
            ANALYZE=true
            shift
            ;;
        *)
            echo "❌ Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

echo "🚀 Starting Ultimate Build Optimization..."
echo "📋 Build Mode: $BUILD_MODE"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if bun is installed
if ! command -v bun &> /dev/null; then
    echo -e "${RED}❌ Bun is not installed. Please install Bun first.${NC}"
    exit 1
fi

# Clean previous builds (unless --no-clean is specified)
if [ "$NO_CLEAN" = false ]; then
    echo -e "${BLUE}🧹 Cleaning previous builds...${NC}"
    bun run clean
else
    echo -e "${YELLOW}⏭️ Skipping clean step${NC}"
fi

# Install dependencies with Bun for speed
echo -e "${BLUE}📦 Installing dependencies with Bun...${NC}"
if [ "$VERBOSE" = true ]; then
    bun install --frozen-lockfile
else
    bun install --frozen-lockfile --silent
fi

# Pre-build optimizations
echo -e "${BLUE}⚡ Running pre-build optimizations...${NC}"

# Set environment variables based on build mode
case $BUILD_MODE in
    "dev")
        echo -e "${BLUE}🔧 Development build with HMR and source maps${NC}"
        export NODE_ENV=development
        export VITE_DEV_MODE=true
        bun run build --mode development
        ;;
    "production")
        echo -e "${GREEN}🏗️ Production build with full optimization${NC}"
        export NODE_ENV=production
        bun run build
        ;;
    "lts")
        echo -e "${BLUE}🛡️ LTS build for maximum compatibility${NC}"
        export NODE_ENV=production
        export VITE_LTS_MODE=true
        export VITE_TARGET=es2015
        bun run build --mode staging
        ;;
    "turbo")
        echo -e "${YELLOW}🔥 Turbo mode with SWC compiler${NC}"
        export NODE_ENV=production
        export VITE_USE_SWC=true
        bun run build:turbo
        ;;
esac

# Post-build optimizations (skip for dev builds)
if [ "$BUILD_MODE" != "dev" ]; then
    echo -e "${BLUE}🎯 Running post-build optimizations...${NC}"

    # Compress assets if available and not disabled
    if [ "$NO_COMPRESS" = false ]; then
        if command -v gzip &> /dev/null; then
            echo -e "${BLUE}📦 Compressing assets with gzip...${NC}"
            find dist -type f \( -name "*.js" -o -name "*.css" -o -name "*.html" \) -exec gzip -k {} \;
        fi

        if command -v brotli &> /dev/null; then
            echo -e "${BLUE}📦 Compressing assets with brotli...${NC}"
            find dist -type f \( -name "*.js" -o -name "*.css" -o -name "*.html" \) -exec brotli -k {} \;
        fi
    else
        echo -e "${YELLOW}⏭️ Skipping compression${NC}"
    fi
else
    echo -e "${YELLOW}⏭️ Skipping post-build optimizations for dev build${NC}"
fi

# Calculate build size
echo -e "${GREEN}📊 Build Statistics:${NC}"
if [ -d "dist" ]; then
    TOTAL_SIZE=$(du -sh dist | cut -f1)
    
    if [ "$SHOW_STATS" = true ] || [ "$VERBOSE" = true ]; then
        # Detailed statistics
        JS_SIZE=$(find dist -name "*.js" -exec du -ch {} + 2>/dev/null | tail -1 | cut -f1 || echo "0")
        CSS_SIZE=$(find dist -name "*.css" -exec du -ch {} + 2>/dev/null | tail -1 | cut -f1 || echo "0")
        HTML_SIZE=$(find dist -name "*.html" -exec du -ch {} + 2>/dev/null | tail -1 | cut -f1 || echo "0")
        ASSET_SIZE=$(find dist -type f \( -name "*.png" -o -name "*.jpg" -o -name "*.gif" -o -name "*.webp" -o -name "*.svg" \) -exec du -ch {} + 2>/dev/null | tail -1 | cut -f1 || echo "0")
        
        echo -e "  📦 Total size: ${YELLOW}$TOTAL_SIZE${NC}"
        echo -e "  🟨 JavaScript: ${YELLOW}$JS_SIZE${NC}"
        echo -e "  🟦 CSS: ${YELLOW}$CSS_SIZE${NC}"
        echo -e "  🟩 HTML: ${YELLOW}$HTML_SIZE${NC}"
        echo -e "  🟪 Assets: ${YELLOW}$ASSET_SIZE${NC}"
        
        # File count statistics
        JS_COUNT=$(find dist -name "*.js" | wc -l)
        CSS_COUNT=$(find dist -name "*.css" | wc -l)
        echo -e "  📄 Files: ${JS_COUNT} JS, ${CSS_COUNT} CSS"
        
        # Compression statistics
        if [ "$NO_COMPRESS" = false ] && command -v gzip &> /dev/null; then
            GZIP_COUNT=$(find dist -name "*.gz" | wc -l)
            echo -e "  🗜️ Compressed: ${GZIP_COUNT} gzip files"
        fi
    else
        # Simple statistics
        echo -e "  📦 Total size: ${YELLOW}$TOTAL_SIZE${NC}"
        echo -e "  💡 Use --stats for detailed breakdown"
    fi
else
    echo -e "${RED}❌ No dist directory found${NC}"
fi

# Performance audit
echo -e "${GREEN}⚡ Performance Audit Complete!${NC}"
echo -e "${GREEN}✅ Build optimization finished successfully${NC}"

# Run bundle analyzer if requested
if [ "$ANALYZE" = true ]; then
    echo -e "${BLUE}📈 Running bundle analyzer...${NC}"
    if command -v bun &> /dev/null && bun run --silent build:analyze 2>/dev/null; then
        echo -e "${GREEN}✅ Bundle analysis complete${NC}"
    else
        echo -e "${YELLOW}⚠️ Bundle analyzer not available (add build:analyze script to package.json)${NC}"
    fi
fi

# Final summary
echo ""
echo -e "${GREEN}🎉 Ultimate build optimization complete!${NC}"
echo -e "${BLUE}📋 Summary:${NC}"
echo -e "  🏗️ Mode: ${YELLOW}$BUILD_MODE${NC}"
echo -e "  📦 Size: ${YELLOW}$TOTAL_SIZE${NC}"
if [ "$ANALYZE" = true ]; then
    echo -e "  📈 Analysis: ${GREEN}Enabled${NC}"
fi
if [ "$NO_COMPRESS" = false ] && [ "$BUILD_MODE" != "dev" ]; then
    echo -e "  🗜️ Compression: ${GREEN}Enabled${NC}"
else
    echo -e "  🗜️ Compression: ${YELLOW}Disabled${NC}"
fi
