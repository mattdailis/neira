import {router} from '../utils/router.js';

/**
 * Convert EPSG:3857 (Web Mercator) coordinates to WGS84 lat/lng
 * @param {number} x - X coordinate in meters
 * @param {number} y - Y coordinate in meters
 * @returns {Array} [lat, lng] in WGS84
 */
function convertWebMercatorToLatLng(x, y) {
  const lng = (x / 20037508.34) * 180;
  const lat = (Math.atan(Math.exp((y / 20037508.34) * Math.PI)) * 360 / Math.PI) - 90;
  return [lat, lng];
}

/**
 * Create popup content using template cloning pattern
 * @param {Object} regatta - Regatta data object
 * @returns {HTMLElement} Popup content
 */
function createPopup(regatta) {
  const template = document.getElementById('popup-template');
  const clone = template.content.cloneNode(true);
  clone.querySelector('.regatta-name').textContent = regatta.name;
  clone.querySelector('.regatta-date').textContent = regatta.date;
  return clone;
}

/**
 * Initialize the map and add regatta markers
 */
async function initMap() {
  try {
    // Fetch regatta data from API
    const response = await fetch(router.buildUrl('api/map-data'));
    if (!response.ok) {
      throw new Error(`Failed to fetch map data: ${response.status}`);
    }
    const data = await response.json();

    // Initialize map centered on New England
    // Default center: roughly central Massachusetts
    const map = L.map('map').setView([42.3, -71.8], 8);

    // Add OpenStreetMap tile layer
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
      maxZoom: 19
    }).addTo(map);

    // Add markers for each regatta
    const markers = [];
    data.regattas.forEach(regatta => {
      const [x, y] = regatta.coordinates;
      const latlng = [x, y]//convertWebMercatorToLatLng(x, y);

      // Create popup content
      const popupContent = createPopup(regatta);

      // Create a temporary div to convert DocumentFragment to HTML string
      const tempDiv = document.createElement('div');
      tempDiv.appendChild(popupContent);

      // Add marker to map
      const marker = L.marker(latlng)
        .bindPopup(tempDiv.innerHTML)
        .addTo(map);

      markers.push(marker);
    });

    // If we have markers, fit the map to show all of them
    if (markers.length > 0) {
      const group = new L.featureGroup(markers);
      map.fitBounds(group.getBounds().pad(0.1));
    }

  } catch (error) {
    console.error('Error initializing map:', error);
    const mapDiv = document.getElementById('map');
    mapDiv.innerHTML = '<p style="padding: 2rem; text-align: center; color: #666;">Failed to load map data. Please try again later.</p>';
  }
}

// Initialize map when DOM is ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initMap);
} else {
  initMap();
}
