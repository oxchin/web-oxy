/**
 * Flag utilities using country-flag-icons package
 * Replaces flagscdn with local SVG flags for better performance
 */

// Import crypto utilities for unified currency icon handling
import { isCryptocurrency, getCurrencyIcon, updateCurrencyIcon as updateUniversalIcon } from './crypto-icons.js';

// Import flags from local assets directory
import usFlag from '../assets/flags/US.svg?url';
import sgFlag from '../assets/flags/SG.svg?url';
import gbFlag from '../assets/flags/GB.svg?url';
import euFlag from '../assets/flags/EU.svg?url';
import jpFlag from '../assets/flags/JP.svg?url';
import auFlag from '../assets/flags/AU.svg?url';
import caFlag from '../assets/flags/CA.svg?url';
import chFlag from '../assets/flags/CH.svg?url';
import cnFlag from '../assets/flags/CN.svg?url';
import seFlag from '../assets/flags/SE.svg?url';
import nzFlag from '../assets/flags/NZ.svg?url';
import mxFlag from '../assets/flags/MX.svg?url';
import hkFlag from '../assets/flags/HK.svg?url';
import noFlag from '../assets/flags/NO.svg?url';
import krFlag from '../assets/flags/KR.svg?url';
import trFlag from '../assets/flags/TR.svg?url';
import ruFlag from '../assets/flags/RU.svg?url';
import inFlag from '../assets/flags/IN.svg?url';
import brFlag from '../assets/flags/BR.svg?url';
import zaFlag from '../assets/flags/ZA.svg?url';
import dkFlag from '../assets/flags/DK.svg?url';
import plFlag from '../assets/flags/PL.svg?url';
import twFlag from '../assets/flags/TW.svg?url';
import thFlag from '../assets/flags/TH.svg?url';
import idFlag from '../assets/flags/ID.svg?url';
import huFlag from '../assets/flags/HU.svg?url';
import czFlag from '../assets/flags/CZ.svg?url';
import ilFlag from '../assets/flags/IL.svg?url';
import clFlag from '../assets/flags/CL.svg?url';
import phFlag from '../assets/flags/PH.svg?url';
import aeFlag from '../assets/flags/AE.svg?url';
import coFlag from '../assets/flags/CO.svg?url';
import saFlag from '../assets/flags/SA.svg?url';
import myFlag from '../assets/flags/MY.svg?url';
import roFlag from '../assets/flags/RO.svg?url';
import unFlag from '../assets/flags/UN.svg?url';

// Manual mapping of flags we support
const FLAG_URLS = {
    'US': usFlag, 'SG': sgFlag, 'GB': gbFlag, 'EU': euFlag, 'JP': jpFlag,
    'AU': auFlag, 'CA': caFlag, 'CH': chFlag, 'CN': cnFlag, 'SE': seFlag,
    'NZ': nzFlag, 'MX': mxFlag, 'HK': hkFlag, 'NO': noFlag, 'KR': krFlag,
    'TR': trFlag, 'RU': ruFlag, 'IN': inFlag, 'BR': brFlag, 'ZA': zaFlag,
    'DK': dkFlag, 'PL': plFlag, 'TW': twFlag, 'TH': thFlag, 'ID': idFlag,
    'HU': huFlag, 'CZ': czFlag, 'IL': ilFlag, 'CL': clFlag, 'PH': phFlag,
    'AE': aeFlag, 'CO': coFlag, 'SA': saFlag, 'MY': myFlag, 'RO': roFlag,
    'UN': unFlag
};

/**
 * Get flag SVG path for a country code
 * @param {string} countryCode - Two-letter country code (e.g., 'US', 'GB')
 * @returns {string} SVG import path
 */
export function getFlagSvgPath(countryCode) {
    if (!countryCode || countryCode.length !== 2) {
        return FLAG_URLS['UN'] || '';
    }

    const code = countryCode.toUpperCase();
    return FLAG_URLS[code] || FLAG_URLS['UN'] || '';
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
        const svgUrl = getFlagSvgPath(countryCode);
        const response = await fetch(svgUrl);
        
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
