/**
 * Version management for cache busting
 * Update VERSION on each deployment
 */

export const VERSION = '2025.10.14.2';

/**
 * Check if a newer version is available
 * Fetches version.json from server and compares
 */
export async function checkForUpdates() {
  try {
    const response = await fetch('version.json?_=' + Date.now());
    const data = await response.json();

    if (data.version !== VERSION) {
      console.log(`New version available: ${data.version} (current: ${VERSION})`);

      // Optionally notify user
      // if (confirm('A new version is available. Reload to update?')) {
      window.location.reload(true); // Hard reload
      // }
    }
  } catch (error) {
    // Silently fail if version.json doesn't exist
    console.debug('Version check failed:', error);
  }
}

/**
 * Add version parameter to a URL for cache busting
 */
export function versionUrl(url) {
  const separator = url.includes('?') ? '&' : '?';
  return `${url}${separator}v=${VERSION}`;
}
