import {router} from '../utils/router.js';

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

    // Create custom red icon for schools
    const redIcon = L.icon({
      iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-red.png',
      shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png',
      iconSize: [25, 41],
      iconAnchor: [12, 41],
      popupAnchor: [1, -34],
      shadowSize: [41, 41]
    });

    // Group regattas by coordinates
    const regattasByLocation = new Map();
    data.regattas.forEach(regatta => {
      const [x, y] = regatta.coordinates;
      const coordKey = `${x},${y}`;

      if (!regattasByLocation.has(coordKey)) {
        regattasByLocation.set(coordKey, []);
      }
      regattasByLocation.get(coordKey).push(regatta);
    });

    // Add markers for each unique location
    const markers = [];
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

    // Add markers for each school (in red)
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
