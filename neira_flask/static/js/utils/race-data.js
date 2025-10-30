/**
 * Race data loading utilities
 * Fetches and parses race manifest data
 */

import { router } from './router.js';

let cachedManifest = null;

/**
 * Load the race manifest from the server
 * @returns {Promise<Object>} Race manifest data
 */
export async function loadRaceManifest(year) {
  if (cachedManifest) {
    return cachedManifest;
  }

  try {
    const response = await fetch(router.buildUrl(`api/races?year=${year}`));
    if (!response.ok) {
      throw new Error(`Failed to load race manifest: ${response.status}`);
    }
    cachedManifest = await response.json();
    return cachedManifest;
  } catch (error) {
    console.error('Error loading race manifest:', error);
    return null;
  }
}

/**
 * Get races for a specific category
 * @param {string} class_ - "fours" or "eights"
 * @param {string} gender - "girls" or "boys"
 * @param {string} varsity - "1", "2", "3", or "4"
 * @returns {Promise<Array>} Array of race objects
 */
export async function getRacesForCategory(year, class_, gender, varsity) {
  varsity = varsityNums[varsity];
  // const manifest = await loadRaceManifest(year);
  const response = await fetch(router.buildUrl(`api/heats?year=${year}&class=${class_}&gender=${gender}&varsity_index=${varsity}`));
  if (!response.ok) {
    throw new Error(`Failed to load race manifest: ${response.status}`);
  }

  const responseJson = await response.json();

  console.log({responseJson});

  return responseJson.map(heat => ({
    date: heat.date,
    displayDate: heat.date,
    raceId: heat.regatta_uid,
    regattaName: heat.regatta_name,
    url: `https://www.row2k.com/results/resultspage.cfm?UID=${heat.regatta_uid}&cat=5`,
    distance: heat.distance,
    results: heat.results.map(result => ({
      school: result.school,
      time: result.raw_time,
      margin: result.margin_from_winner,
    }))
  }));

  if (!manifest || !manifest.categories) {
    return [];
  }

  try {
    return manifest.categories[class_][gender][varsity] || [];
  } catch (error) {
    console.error(`No data found for ${class_}/${gender}/${varsity}`);
    return [];
  }
}

/**
 * Get a specific race by ID
 * @param {string} raceId - Race identifier (e.g., "ABCD1234")
 * @returns {Promise<Object>} Race data from data/2_reviewed/{raceId}.json
 */
export async function getRaceDetail(raceId) {
  try {
    const response = await fetch(router.buildUrl(`static/data/2_reviewed/${raceId}.json`));
    if (!response.ok) {
      throw new Error(`Failed to load race ${raceId}: ${response.status}`);
    }
    return await response.json();
  } catch (error) {
    console.error('Error loading race detail:', error);
    return null;
  }
}

/**
 * Format a category name for display
 * @param {string} class_ - "fours" or "eights"
 * @param {string} gender - "girls" or "boys"
 * @param {string} varsity - "1", "2", "3", or "4"
 * @returns {string} Formatted name (e.g., "Girls Fours: 1V")
 */
export function formatCategoryName(class_, gender, varsity) {
  const genderCap = gender.charAt(0).toUpperCase() + gender.slice(1);
  const classCap = class_.charAt(0).toUpperCase() + class_.slice(1);
  const varsityCap = varsity.charAt(0).toUpperCase() + varsity.slice(1);
  const varsityNum = varsityNums[varsity];
  return `${genderCap} ${varsityCap} Varsity ${classCap} (${varsityNum}V)`;
}

/**
 * Get the ordinal suffix for a number (1st, 2nd, 3rd, etc.)
 * @param {number} n - Number
 * @returns {string} Number with ordinal suffix
 */
export function ordinal(n) {
  const s = ["th", "st", "nd", "rd"];
  const v = n % 100;
  return n + (s[(v - 20) % 10] || s[v] || s[0]);
}

export const varsityNums = {"first": 1, "second": 2, "third": 3, "fourth": 4, "fifth": 5, "sixth": 6};
export const varsityNames = {1: "first", 2: "second", 3: "third", 4: "fourth", 5: "fifth", 6: "sixth"};