/**
 * UTC Time Utilities
 * Provides consistent UTC time handling across the application
 */

/**
 * Get current UTC timestamp
 * @returns {number} UTC timestamp in milliseconds
 */
export function getUTCTimestamp() {
    return Date.now();
}

/**
 * Get current UTC Date object
 * @returns {Date} UTC Date object
 */
export function getUTCDate() {
    const now = new Date();
    return new Date(now.getTime() + (now.getTimezoneOffset() * 60000));
}

/**
 * Format UTC time for display
 * @param {Date} date - Date object to format
 * @param {Object} options - Intl.DateTimeFormat options
 * @returns {string} Formatted time string
 */
export function formatUTCTime(date = null, options = {}) {
    const utcDate = date ? getUTCDate() : new Date();
    const defaultOptions = {
        hour: '2-digit',
        minute: '2-digit',
        hour12: false,
        timeZone: 'UTC'
    };
    
    return utcDate.toLocaleTimeString('en-US', { ...defaultOptions, ...options });
}

/**
 * Format UTC date for display
 * @param {Date} date - Date object to format
 * @param {Object} options - Intl.DateTimeFormat options
 * @returns {string} Formatted date string
 */
export function formatUTCDate(date = null, options = {}) {
    const utcDate = date ? getUTCDate() : new Date();
    const defaultOptions = {
        timeZone: 'UTC'
    };
    
    return utcDate.toLocaleDateString('en-US', { ...defaultOptions, ...options });
}

/**
 * Get UTC date with offset
 * @param {number} days - Number of days to offset (negative for past)
 * @returns {Date} UTC Date object with offset
 */
export function getUTCDateWithOffset(days = 0) {
    const utcDate = getUTCDate();
    utcDate.setUTCDate(utcDate.getUTCDate() + days);
    return utcDate;
}

/**
 * Get UTC date with month offset
 * @param {number} months - Number of months to offset (negative for past)
 * @returns {Date} UTC Date object with offset
 */
export function getUTCDateWithMonthOffset(months = 0) {
    const utcDate = getUTCDate();
    utcDate.setUTCMonth(utcDate.getUTCMonth() + months);
    return utcDate;
}

/**
 * Get ISO string in UTC
 * @param {Date} date - Date object (optional)
 * @returns {string} ISO string in UTC
 */
export function getUTCISOString(date = null) {
    const utcDate = date || getUTCDate();
    return utcDate.toISOString();
}

/**
 * Log with UTC timestamp
 * @param {string} message - Message to log
 * @param {string} level - Log level (info, warn, error)
 */
export function logWithUTCTime(message, level = 'info') {
    const timestamp = formatUTCTime();
    const logMessage = `[${timestamp} UTC] ${message}`;
    
    switch (level) {
        case 'warn':
            console.warn(logMessage);
            break;
        case 'error':
            console.error(logMessage);
            break;
        default:
            console.log(logMessage);
    }
}
