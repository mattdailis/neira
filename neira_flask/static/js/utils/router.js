/**
 * Simple router utility for handling navigation
 * Uses URLSearchParams for query-based routing
 */

export const router = {
  /**
   * Get a URL parameter value
   * @param {string} name - Parameter name
   * @returns {string|null} Parameter value or null
   */
  getParam(name) {
    const params = new URLSearchParams(window.location.search);
    return params.get(name);
  },

  /**
   * Set a URL parameter and update browser history
   * @param {string} name - Parameter name
   * @param {string} value - Parameter value
   */
  setParam(name, value) {
    const params = new URLSearchParams(window.location.search);
    params.set(name, value);
    const newUrl = `${window.location.pathname}?${params.toString()}`;
    window.history.pushState({}, '', newUrl);
  },

  /**
   * Navigate to a new URL
   * @param {string} url - URL to navigate to
   */
  navigate(url) {
    window.location.href = url;
  },

  /**
   * Get the base path for the application
   * In development: '/'
   * In production (GitHub Pages): '/neira/'
   * @returns {string} Base path
   */
  getBasePath() {
    // Check if we're on GitHub Pages
    if (window.location.hostname.includes('github.io')) {
      return '/neira/';
    }
    return '/';
  },

  /**
   * Build a URL with the correct base path
   * @param {string} path - Relative path (e.g., 'dot/girls1fours.html')
   * @returns {string} Full URL with base path
   */
  buildUrl(path) {
    const base = this.getBasePath();
    // Remove leading slash from path if present
    const cleanPath = path.startsWith('/') ? path.slice(1) : path;
    return `${base}${cleanPath}`;
  }
};
