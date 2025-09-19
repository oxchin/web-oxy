/**
 * Flag utilities using country-flag-icons package
 * Replaces flagscdn with local SVG flags for better performance
 */

// Import crypto utilities for unified currency icon handling
import { isCryptocurrency, getCurrencyIcon, updateCurrencyIcon as updateUniversalIcon } from './crypto-icons.js';

/**
 * Get flag SVG path for a country code
 * @param {string} countryCode - Two-letter country code (e.g., 'US', 'GB')
 * @returns {string} SVG import path
 */
export function getFlagSvgPath(countryCode) {
    if (!countryCode || countryCode.length !== 2) {
        return '/node_modules/country-flag-icons/3x2/UN.svg'; // Fallback to UN flag
    }
    
    const code = countryCode.toUpperCase();
    return `/node_modules/country-flag-icons/3x2/${code}.svg`;
}

/**
 * Create flag image element with SVG source
 * @param {string} countryCode - Two-letter country code
 * @param {string} altText - Alt text for accessibility
 * @param {string} className - CSS class name
 * @returns {HTMLImageElement} Flag image element
 */
export function createFlagImage(countryCode, altText = '', className = 'flag-indicator') {
    const img = document.createElement('img');
    img.src = getFlagSvgPath(countryCode);
    img.alt = altText || `${countryCode} flag`;
    img.className = className;
    img.loading = 'lazy';
    
    // Fallback to UN flag on error
    img.onerror = () => {
        if (img.src !== getFlagSvgPath('UN')) {
            img.src = getFlagSvgPath('UN');
        }
    };
    
    return img;
}

/**
 * Update existing flag image element
 * @param {HTMLImageElement} imgElement - Existing image element
 * @param {string} countryCode - Two-letter country code
 * @param {string} altText - Alt text for accessibility
 */
export function updateFlagImage(imgElement, countryCode, altText = '') {
    if (!imgElement) return;
    
    imgElement.src = getFlagSvgPath(countryCode);
    imgElement.alt = altText || `${countryCode} flag`;
    
    // Fallback to UN flag on error
    imgElement.onerror = () => {
        if (imgElement.src !== getFlagSvgPath('UN')) {
            imgElement.src = getFlagSvgPath('UN');
        }
    };
}

/**
 * Enhanced update function that handles both crypto and fiat currencies
 * @param {HTMLImageElement} imgElement - Existing image element
 * @param {string} currencyCode - Currency code (e.g., 'USD', 'BTC')
 * @param {string} countryCode - Country code for fiat currencies
 * @param {string} altText - Alt text for accessibility
 */
export function updateCurrencyIconSmart(imgElement, currencyCode, countryCode = null, altText = '') {
    if (!imgElement) return;
    
    if (isCryptocurrency(currencyCode)) {
        updateUniversalIcon(imgElement, currencyCode, null);
    } else {
        updateFlagImage(imgElement, countryCode, altText);
    }
}

/**
 * Get flag SVG as inline element for better performance
 * @param {string} countryCode - Two-letter country code
 * @returns {Promise<string>} SVG content as string
 */
export async function getFlagSvgInline(countryCode) {
    try {
        const svgPath = getFlagSvgPath(countryCode);
        const response = await fetch(svgPath);
        
        if (!response.ok) {
            throw new Error(`Failed to load flag: ${response.status}`);
        }
        
        return await response.text();
    } catch (error) {
        console.warn(`Failed to load flag for ${countryCode}:`, error);
        // Return UN flag as fallback
        try {
            const fallbackResponse = await fetch(getFlagSvgPath('UN'));
            return await fallbackResponse.text();
        } catch (fallbackError) {
            console.error('Failed to load fallback flag:', fallbackError);
            return '<svg></svg>'; // Empty SVG as last resort
        }
    }
}

/**
 * Preload flag images for better performance
 * @param {string[]} countryCodes - Array of country codes to preload
 */
export function preloadFlags(countryCodes) {
    countryCodes.forEach(code => {
        const link = document.createElement('link');
        link.rel = 'preload';
        link.as = 'image';
        link.href = getFlagSvgPath(code);
        document.head.appendChild(link);
    });
}

/**
 * Common country codes for major currencies
 */
export const MAJOR_CURRENCY_FLAGS = [
    'US', 'EU', 'GB', 'JP', 'SG', 'CA', 'AU', 'CH', 'CN', 'IN',
    'KR', 'MX', 'BR', 'ZA', 'RU', 'TR', 'AE', 'HK', 'NZ', 'SE'
];
