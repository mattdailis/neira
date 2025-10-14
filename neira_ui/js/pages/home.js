/**
 * Home page initialization
 * Currently just imports utilities for future use
 */

import { router } from '../utils/router.js';

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

generateCategoryLinks('fours', 'girls', 'girls-fours-links');
generateCategoryLinks('fours', 'boys', 'boys-fours-links');