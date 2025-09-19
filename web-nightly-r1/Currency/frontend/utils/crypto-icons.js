/**
 * Cryptocurrency icon utilities using cryptocurrency-icons package
 * Provides local SVG crypto icons for better performance
 */

// Import crypto icons from local assets directory
import btcIcon from '../assets/crypto/btc.svg?url';
import ethIcon from '../assets/crypto/eth.svg?url';
import adaIcon from '../assets/crypto/ada.svg?url';
import xrpIcon from '../assets/crypto/xrp.svg?url';
import ltcIcon from '../assets/crypto/ltc.svg?url';
import bchIcon from '../assets/crypto/bch.svg?url';
import dotIcon from '../assets/crypto/dot.svg?url';
import linkIcon from '../assets/crypto/link.svg?url';
import bnbIcon from '../assets/crypto/bnb.svg?url';
import solIcon from '../assets/crypto/sol.svg?url';
import maticIcon from '../assets/crypto/matic.svg?url';
import avaxIcon from '../assets/crypto/avax.svg?url';
import uniIcon from '../assets/crypto/uni.svg?url';
import atomIcon from '../assets/crypto/atom.svg?url';
import dogeIcon from '../assets/crypto/doge.svg?url';
import shibIcon from '../assets/crypto/shib.svg?url';
import genericIcon from '../assets/crypto/generic.svg?url';

// Manual mapping of crypto icons we support
const CRYPTO_URLS = {
    'btc': btcIcon, 'eth': ethIcon, 'ada': adaIcon, 'xrp': xrpIcon,
    'ltc': ltcIcon, 'bch': bchIcon, 'dot': dotIcon, 'link': linkIcon,
    'bnb': bnbIcon, 'sol': solIcon, 'matic': maticIcon, 'avax': avaxIcon,
    'uni': uniIcon, 'atom': atomIcon, 'doge': dogeIcon, 'shib': shibIcon,
    'generic': genericIcon
};

// Import flag URLs from flags.js to avoid circular dependency
import { getFlagSvgPath } from './flags.js';

/**
 * Get crypto icon SVG path for a cryptocurrency symbol
 * @param {string} cryptoSymbol - Crypto symbol (e.g., 'BTC', 'ETH', 'ADA')
 * @returns {string} SVG import path
 */
export function getCryptoIconPath(cryptoSymbol) {
    const symbol = (cryptoSymbol || 'generic').toLowerCase();
    return CRYPTO_URLS[symbol] || CRYPTO_URLS['generic'] || '';
}

/**
 * Create crypto icon image element with SVG source
 * @param {string} cryptoSymbol - Crypto symbol
 * @param {string} altText - Alt text for accessibility
 * @param {string} className - CSS class name
 * @returns {HTMLImageElement} Crypto icon image element
 */
export function createCryptoIcon(cryptoSymbol, altText = '', className = 'crypto-icon') {
    const img = document.createElement('img');
    img.src = getCryptoIconPath(cryptoSymbol);
    img.alt = altText || `${cryptoSymbol} icon`;
    img.className = className;
    img.loading = 'lazy';
    
    // Fallback to generic crypto icon on error
    img.onerror = () => {
        const fallback = getCryptoIconPath('generic');
        if (fallback && img.src !== fallback) img.src = fallback;
    };
    
    return img;
}

/**
 * Update existing crypto icon image element
 * @param {HTMLImageElement} imgElement - Existing image element
 * @param {string} cryptoSymbol - Crypto symbol
 * @param {string} altText - Alt text for accessibility
 */
export function updateCryptoIcon(imgElement, cryptoSymbol, altText = '') {
    if (!imgElement) return;
    
    imgElement.src = getCryptoIconPath(cryptoSymbol);
    imgElement.alt = altText || `${cryptoSymbol} icon`;
    
    // Fallback to generic crypto icon on error
    imgElement.onerror = () => {
        if (imgElement.src !== getCryptoIconPath('generic')) {
            imgElement.src = getCryptoIconPath('generic');
        }
    };
}

/**
 * Check if a currency is a cryptocurrency
 * @param {string} currencyCode - Currency code to check
 * @returns {boolean} True if it's a cryptocurrency
 */
export function isCryptocurrency(currencyCode) {
    const cryptoCurrencies = [
        'BTC', 'ETH', 'ADA', 'XRP', 'LTC', 'BCH', 'DOT', 'LINK', 'BNB', 'SOL',
        'MATIC', 'AVAX', 'UNI', 'ATOM', 'XLM', 'VET', 'FIL', 'TRX', 'ETC',
        'THETA', 'XMR', 'ALGO', 'AAVE', 'MKR', 'COMP', 'SUSHI', 'YFI', 'SNX',
        'CRV', 'BAL', 'REN', 'KNC', 'ZRX', 'OMG', 'LRC', 'ANT', 'REP', 'GNT',
        'DOGE', 'SHIB', 'PEPE', 'FLOKI', 'SAFEMOON'
    ];
    
    return cryptoCurrencies.includes(currencyCode.toUpperCase());
}

/**
 * Get appropriate icon (flag or crypto) based on currency type
 * @param {string} currencyCode - Currency code
 * @param {string} countryCode - Country code (for fiat currencies)
 * @returns {Object} Icon information with type and path
 */
export function getCurrencyIcon(currencyCode, countryCode = null) {
    if (isCryptocurrency(currencyCode)) {
        return {
            type: 'crypto',
            path: getCryptoIconPath(currencyCode),
            alt: `${currencyCode} cryptocurrency`
        };
    } else {
        // Use flag icon for fiat currencies via flags.js
        const flagPath = getFlagSvgPath(countryCode || 'UN');
        
        return {
            type: 'flag',
            path: flagPath,
            alt: `${currencyCode} currency flag`
        };
    }
}

/**
 * Create universal currency icon (crypto or flag)
 * @param {string} currencyCode - Currency code
 * @param {string} countryCode - Country code (for fiat currencies)
 * @param {string} className - CSS class name
 * @returns {HTMLImageElement} Currency icon element
 */
export function createCurrencyIcon(currencyCode, countryCode = null, className = 'currency-icon') {
    const iconInfo = getCurrencyIcon(currencyCode, countryCode);
    
    const img = document.createElement('img');
    img.src = iconInfo.path;
    img.alt = iconInfo.alt;
    img.className = `${className} ${iconInfo.type}-icon`;
    img.loading = 'lazy';
    
    // Fallback handling
    img.onerror = () => {
        if (iconInfo.type === 'crypto') {
            img.src = getCryptoIconPath('generic');
        } else {
            img.src = getFlagSvgPath('UN');
        }
    };
    
    return img;
}

/**
 * Update universal currency icon
 * @param {HTMLImageElement} imgElement - Existing image element
 * @param {string} currencyCode - Currency code
 * @param {string} countryCode - Country code (for fiat currencies)
 */
export function updateCurrencyIcon(imgElement, currencyCode, countryCode = null) {
    if (!imgElement) return;
    
    const iconInfo = getCurrencyIcon(currencyCode, countryCode);
    
    imgElement.src = iconInfo.path;
    imgElement.alt = iconInfo.alt;
    imgElement.className = imgElement.className.replace(/(crypto|flag)-icon/g, '') + ` ${iconInfo.type}-icon`;
    
    // Fallback handling
    imgElement.onerror = () => {
        if (iconInfo.type === 'crypto') {
            imgElement.src = getCryptoIconPath('generic');
        } else {
            imgElement.src = getFlagSvgPath('UN');
        }
    };
}

/**
 * Preload crypto icons for better performance
 * @param {string[]} cryptoSymbols - Array of crypto symbols to preload
 */
export function preloadCryptoIcons(cryptoSymbols) {
    cryptoSymbols.forEach(symbol => {
        const link = document.createElement('link');
        link.rel = 'preload';
        link.as = 'image';
        link.href = getCryptoIconPath(symbol);
        document.head.appendChild(link);
    });
}

/**
 * Major cryptocurrencies for preloading
 */
export const MAJOR_CRYPTOCURRENCIES = [
    'BTC', 'ETH', 'ADA', 'XRP', 'LTC', 'BCH', 'DOT', 'LINK', 'BNB', 'SOL',
    'MATIC', 'AVAX', 'UNI', 'ATOM', 'DOGE', 'SHIB'
];
