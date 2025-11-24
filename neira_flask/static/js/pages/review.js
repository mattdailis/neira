/**
 * Home page initialization
 * Currently just imports utilities for future use
 */

import { router } from '../utils/router.js';

import { login, logout, foo } from '../utils/auth.js';
// document.getElementById('login-button').addEventListener('click', login);
// document.getElementById('logout-button').addEventListener('click', logout);
// document.getElementById('api-test').addEventListener('click', foo);

// Home page is mostly static, but we import router for future dynamic features
console.log('Home page loaded');

const year = router.getParam('year') || '2025';

// Set the season header
const seasonHeader = document.getElementById('season-header');
if (seasonHeader) {
  seasonHeader.textContent = `${year} Season`;
}

// Generate category links
const varsityLevels = ['first', 'second', 'third', 'fourth', 'fifth', 'sixth'];
const varsityNumbers = { first: 1, second: 2, third: 3, fourth: 4, fifth: 5, sixth: 6 };

function generateCategoryLinks(class_, gender, containerId) {
  const container = document.getElementById(containerId);
  if (!container) return;

  varsityLevels.forEach(varsity => {
    const categorySlug = `${class_}-${gender}-${varsity}`;
    const varsityNum = varsityNumbers[varsity];
    const graphUrl = `static/dot/${gender}${varsityNum}${class_}.html`;

    // Create category link
    const categoryLink = document.createElement('a');
    categoryLink.href = `category.html?year=${year}&category=${categorySlug}`;
    categoryLink.textContent = `${varsity.charAt(0).toUpperCase() + varsity.slice(1)} Boat`;

    // Create graph link
    const graphLink = document.createElement('a');
    graphLink.href = graphUrl;
    graphLink.textContent = 'graph';

    // Add to container
    container.appendChild(categoryLink);
    container.appendChild(document.createTextNode(' ('));
    container.appendChild(graphLink);
    container.appendChild(document.createTextNode(')'));
    container.appendChild(document.createElement('br'));
  });
}

async function init() {
  const response = await fetch(router.buildUrl(`api/regattas?year=${year}`));
  if (!response.ok) {
    throw new Error(`Failed to load regattas list: ${response.status}`);
  }

  const responseJson = await response.json();

  console.log({responseJson});

  // Add each date section with all its races
  const racesContainer = document.getElementById('races-container');
  for (const regattas of responseJson) {
    racesContainer.appendChild(createRegattaRow(regattas))
  }
}

/**
 * Create a race date section with results
 */
function createRegattaRow(regattas) {
  const template = document.getElementById('regatta-template');
  const clone = template.content.cloneNode(true);

  // console.log(regattas);

  regattas.sort((a, b) => a.date.localeCompare(b.date));
  regattas.sort((a, b) => a.status.localeCompare(b.status));

  clone.querySelector('.name').innerHTML = regattas[regattas.length - 1].date + " " + regattas[regattas.length - 1].name + " (" + regattas.map(x => (x.status != '2_cleaned' || x.correction_id == null) ? x.status : `<b>${x.status}</b>`).join(", ") + ")";
  clone.querySelector('.name').href = `/review-regatta.html?uid=${regattas[regattas.length - 1].regatta_uid}`;

  // // Add all race results for this date
  // const racesContainer = clone.querySelector('.races-container');
  // for (const race of races) {
  //   const raceResults = createRaceResults(race);
  //   racesContainer.appendChild(raceResults);
  // }

  return clone;
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', init);
} else {
  console.log(document.readyState);
  init();
}
