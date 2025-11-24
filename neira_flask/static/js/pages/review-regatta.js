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

const regatta_uid = router.getParam('uid');

async function init() {
  const response = await fetch(router.buildUrl(`api/review-regatta?uid=${regatta_uid}`));
  if (!response.ok) {
    throw new Error(`Failed to load regattas list: ${response.status}`);
  }

  const responseJson = await response.json();

  document.getElementById("row2k-link").href = responseJson["regatta"]["2_cleaned"]["url"];
  console.log(responseJson["regatta"]["2_cleaned"]["url"]);

  document.getElementById("regatta-name").textContent = responseJson["regatta"]["2_cleaned"]["name"];
  document.getElementById("regatta-comment").textContent = responseJson["regatta"]["2_cleaned"]["comment"];

  console.log({responseJson});


  // Add each date section with all its races
  const racesContainer = document.getElementById('races-container');
  for (const heat of responseJson["regatta"]["2_cleaned"]["heats"]) {
    racesContainer.appendChild(createHeat(heat))
  }

  const correctionsContainer = document.getElementById('corrections-container');
  for (const correction of responseJson.corrections.corrections) {
    correctionsContainer.appendChild(createCorrection(correction));
  }
}

/**
 * Create a race date section with results
 */
function createHeat(heat) {
  const template = document.getElementById('heat-template');
  const clone = template.content.cloneNode(true);

  clone.querySelector('.name').textContent = heat["gender"] + " " + heat["varsity_index"];
  
  // Build results table
  const resultsTable = clone.querySelector('.results-table');

  const longestSchoolNameLength = Math.max(...heat.results.map(result => result.school.length));

  for (const result of heat.results) {
    const schoolName = result.school.padEnd(Math.max(15, longestSchoolNameLength + 2), ' ');
    const time = result.raw_time.padEnd(8, ' ');
    // const margin = result.margin > 0 ? `+${result.margin.toFixed(1)}` : '';

    // Create clickable line
    const line = document.createElement('a');
    // line.href = race.url;
    line.className = 'result-row';
    line.textContent = `${schoolName}${time}`; // ${margin}`;
    resultsTable.appendChild(line);
    resultsTable.appendChild(document.createTextNode('\n'));
  }
  // clone.querySelector('.name').href = `/review-regatta.html?uid=${regattas[regattas.length - 1].regatta_uid}`;

  // // Add all race results for this date
  // const racesContainer = clone.querySelector('.races-container');
  // for (const race of races) {
  //   const raceResults = createRaceResults(race);
  //   racesContainer.appendChild(raceResults);
  // }

  return clone;
}

function createCorrection(correction) {
  const pre = document.createElement("pre");
  pre.textContent = JSON.stringify(correction);
  return pre;
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', init);
} else {
  console.log(document.readyState);
  init();
}
