/**
 * Category page - shows all races for a specific boat category
 * URL: /category.html?class=fours&gender=girls&varsity=1
 *
 * Uses HTML <template> elements for rendering (no string concatenation)
 */

import { router } from '../utils/router.js';
import { getRacesForCategory, formatCategoryName, varsityNums } from '../utils/race-data.js';
import { checkForUpdates } from '../utils/version.js';

// Check for updates on page load
checkForUpdates();

// Get URL parameters
const year = router.getParam('year') || '2025';
// const class_ = router.getParam('class') || 'fours';
// const gender = router.getParam('gender') || 'girls';
// const varsity = router.getParam('varsity') || '1';
const slug = router.getParam('category') || '';
const [class_, gender, varsity] = slug.split('-');

// Load and display data
async function init() {
  const container = document.getElementById('category-content');
  container.innerHTML = ''; // Clear loading message

  // Show category title
  const title = formatCategoryName(class_, gender, varsity);
  document.title = `NEIRA - ${title}`;

  // Add header
  const header = createHeader(title, class_, gender, varsity);
  container.appendChild(header);

  // Load race data
  const races = await getRacesForCategory(year, class_, gender, varsity);

  if (!races || races.length === 0) {
    const noResults = createNoResults();
    container.appendChild(noResults);
    return;
  }

  // Group races by date
  const racesByDate = {};
  for (const race of races) {
    if (!racesByDate[race.date]) {
      racesByDate[race.date] = [];
    }
    racesByDate[race.date].push(race);
  }

  // Sort dates in reverse chronological order (newest first)
  const sortedDates = Object.keys(racesByDate).sort().reverse();

  // Add each date section with all its races
  for (const date of sortedDates) {
    const racesForDate = racesByDate[date];
    const raceSection = createRaceSection(racesForDate);
    container.appendChild(raceSection);
  }
}

/**
 * Create header section from template
 */
function createHeader(title, class_, gender, varsity) {
  const template = document.getElementById('category-header-template');
  const clone = template.content.cloneNode(true);

  // Fill in data
  clone.getElementById('title').textContent = title;

  const graphLink = clone.getElementById('graph-link');
  graphLink.href = router.buildUrl(`static/dot/${gender}${varsityNums[varsity]}${class_}.html`);

  return clone;
}

/**
 * Create a race date section with results
 */
function createRaceSection(races) {
  const template = document.getElementById('race-date-template');
  const clone = template.content.cloneNode(true);

  // Set date (all races have same date)
  clone.querySelector('.date').textContent = races[0].displayDate;

  // Add all race results for this date
  const racesContainer = clone.querySelector('.races-container');
  for (const race of races) {
    const raceResults = createRaceResults(race);
    racesContainer.appendChild(raceResults);
  }

  return clone;
}

/**
 * Create race results box from template
 */
function createRaceResults(race) {
  const template = document.getElementById('race-results-template');
  const clone = template.content.cloneNode(true);

  // Set regatta info
  clone.querySelector('.regatta-name').textContent = race.regattaName;

  const distanceSpan = clone.querySelector('.distance');
  if (race.distance) {
    distanceSpan.textContent = ` - ${race.distance}m`;
  }

  const row2kLink = clone.querySelector('.row2k-link');
  row2kLink.href = race.url;

  // Build results table
  const resultsTable = clone.querySelector('.results-table');

  const longestSchoolNameLength = Math.max(...race.results.map(result => result.school.length));

  for (const result of race.results) {
    const schoolName = result.school.padEnd(Math.max(15, longestSchoolNameLength + 2), ' ');
    const time = result.time.padEnd(8, ' ');
    // const margin = result.margin > 0 ? `+${result.margin.toFixed(1)}` : '';

    // Create clickable line
    const line = document.createElement('a');
    line.href = race.url;
    line.className = 'result-row';
    line.textContent = `${schoolName}${time}`; // ${margin}`;
    resultsTable.appendChild(line);
    resultsTable.appendChild(document.createTextNode('\n'));
  }

  return clone;
}

/**
 * Create no results message from template
 */
function createNoResults() {
  const template = document.getElementById('no-results-template');
  return template.content.cloneNode(true);
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', init);
} else {
  init();
}
