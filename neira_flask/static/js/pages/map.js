import {router} from '../utils/router.js';

// Global variables to store map and data for filtering
let mapInstance = null;
let mapData = null;
let allMarkers = [];

/**
 * Get current filter state from URL parameters
 * @returns {Object} Filter state with keys: boys, girls, fours, eights
 */
function getFilterState() {
  return {
    boys: router.getParam('boys') !== 'false',
    girls: router.getParam('girls') !== 'false',
    fours: router.getParam('fours') !== 'false',
    eights: router.getParam('eights') !== 'false'
  };
}

/**
 * Check if regatta matches current filters
 * @param {Object} regatta - Regatta data object
 * @param {Object} filters - Filter state object
 * @returns {boolean} True if regatta should be shown
 */
function regattaMatchesFilters(regatta, filters) {
  // Always show regattas without categories (e.g., Founder's Day)
  if (!regatta.categories || regatta.categories.length === 0) {
    return true;
  }

  // Show if ANY category tuple matches selected filters
  return regatta.categories.some(([boatClass, gender]) =>
    filters[gender] && filters[boatClass]
  );
}

/**
 * Create popup content for single or multiple regattas
 * @param {Array} regattas - Array of regatta data objects at the same location
 * @returns {HTMLElement} Popup content
 */
function createPopup(regattas) {
  const div = document.createElement('div');
  div.className = 'regatta-popup';

  const title = document.createElement('strong');
  title.textContent = regattas[0].location;
  div.appendChild(title);

  const list = document.createElement('ul');
  list.style.margin = '8px 0';
  list.style.paddingLeft = '20px';

  var options = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric', timeZone: 'UTC' };

  regattas.forEach(regatta => {
    const item = document.createElement('li');
    const anchor = document.createElement('a');
    anchor.href = regatta.url;
    const displayDate = new Date(regatta.date).toLocaleDateString("en-US", options);
    anchor.textContent = `${displayDate} (${regatta.name})`;
    item.appendChild(anchor);
    list.appendChild(item);
  });

  div.appendChild(list);
  return div;
}

/**
 * Create markers based on filtered data
 * @param {Object} map - Leaflet map instance
 * @param {Object} data - Map data (regattas and schools)
 * @param {Object} filters - Filter state
 * @returns {Array} Array of created markers
 */
function createMarkers(map, data, filters) {
  const markers = [];

  // Create custom red icon for schools
  const redIcon = L.icon({
    iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-red.png',
    shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png',
    iconSize: [25, 41],
    iconAnchor: [12, 41],
    popupAnchor: [1, -34],
    shadowSize: [41, 41]
  });

  // Group regattas by coordinates (with filtering)
  const regattasByLocation = new Map();
  data.regattas.forEach(regatta => {
    // Skip regattas that don't match filters
    if (!regattaMatchesFilters(regatta, filters)) {
      return;
    }

    const [x, y] = regatta.coordinates;
    const coordKey = `${x},${y}`;

    if (!regattasByLocation.has(coordKey)) {
      regattasByLocation.set(coordKey, []);
    }
    regattasByLocation.get(coordKey).push(regatta);
  });

  // Add markers for each unique location
  regattasByLocation.forEach((regattas, coordKey) => {
    const [x, y] = coordKey.split(',').map(Number);
    const latlng = [x, y];

    // Create popup content (handles both single and multiple regattas)
    const popupContent = createPopup(regattas);

    // Create a temporary div to convert to HTML string
    const tempDiv = document.createElement('div');
    tempDiv.appendChild(popupContent);

    // Add marker to map
    const marker = L.marker(latlng)
      .bindPopup(tempDiv.innerHTML)
      .addTo(map);

    markers.push(marker);
  });

  // Add markers for each school (in red) - always shown, not filtered
  data.schools.forEach(school => {
    const [x, y] = school.coordinates;
    const latlng = [x, y];

    // Create popup content for school
    const popupHtml = `<div class="school-popup">
      <strong>${school.name}</strong>
    </div>`;

    // Add red marker to map
    const marker = L.marker(latlng, { icon: redIcon })
      .bindPopup(popupHtml)
      .addTo(map);

    markers.push(marker);
  });

  return markers;
}

/**
 * Setup filter change listeners
 */
function setupFilterListeners() {
  const checkboxes = document.querySelectorAll('#filter-container input[type="checkbox"]');

  checkboxes.forEach(checkbox => {
    checkbox.addEventListener('change', () => {
      // Get current filter state from checkboxes
      const filters = {};
      checkboxes.forEach(cb => {
        filters[cb.value] = cb.checked;
      });

      // Update URL parameters
      Object.entries(filters).forEach(([key, value]) => {
        router.setParam(key, value.toString());
      });

      // Redraw markers
      redrawMarkers();
    });
  });
}

/**
 * Redraw map markers based on current filter state
 */
function redrawMarkers() {
  if (!mapInstance || !mapData) {
    return;
  }

  // Remove existing markers
  allMarkers.forEach(marker => {
    mapInstance.removeLayer(marker);
  });

  // Get current filter state
  const filters = getFilterState();

  // Create new filtered markers
  allMarkers = createMarkers(mapInstance, mapData, filters);

  // Fit bounds if we have markers
  if (allMarkers.length > 0) {
    const group = new L.featureGroup(allMarkers);
    mapInstance.fitBounds(group.getBounds().pad(0.1));
  }
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

    // Store data globally for filtering
    mapData = data;

    // Initialize map centered on New England
    // Default center: roughly central Massachusetts
    const map = L.map('map').setView([42.3, -71.8], 8);
    mapInstance = map;

    // Add OpenStreetMap tile layer
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
      maxZoom: 19
    }).addTo(map);

    // Get current filter state from URL
    const filters = getFilterState();

    // Initialize checkboxes to match URL state
    const checkboxes = document.querySelectorAll('#filter-container input[type="checkbox"]');
    checkboxes.forEach(checkbox => {
      checkbox.checked = filters[checkbox.value];
    });

    // Create markers with current filters
    allMarkers = createMarkers(map, data, filters);

    // If we have markers, fit the map to show all of them
    if (allMarkers.length > 0) {
      const group = new L.featureGroup(allMarkers);
      map.fitBounds(group.getBounds().pad(0.1));
    }

    // Setup filter change listeners
    setupFilterListeners();

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
