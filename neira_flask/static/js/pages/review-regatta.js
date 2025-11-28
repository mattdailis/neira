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
let currentCorrections = [];

async function init() {
  const response = await fetch(router.buildUrl(`api/review-regatta?uid=${regatta_uid}`));
  if (!response.ok) {
    throw new Error(`Failed to load regattas list: ${response.status}`);
  }

  const responseJson = await response.json();

  document.getElementById("row2k-link").href = responseJson["regatta"]["1_parsed"]["url"];
  console.log(responseJson["regatta"]["1_parsed"]["url"]);

  document.getElementById("regatta-name").textContent = responseJson["regatta"]["1_parsed"]["name"];
  document.getElementById("regatta-comment").textContent = responseJson["regatta"]["1_parsed"]["comment"];

  console.log({responseJson});

  // Add each heat as a table row
  const tableBody = document.getElementById('table-body');
  const parsedHeats = responseJson["regatta"]["1_parsed"]["heats"];
  const cleanedHeats = responseJson["regatta"]["2_cleaned"]?.["heats"] || [];
  const reviewedHeats = responseJson["regatta"]["3_reviewed"]?.["heats"] || [];

  console.log({parsedHeats, cleanedHeats, reviewedHeats});

  for (let i = 0; i < parsedHeats.length; i++) {
    tableBody.appendChild(createHeatRow(
      parsedHeats[i],
      cleanedHeats[i],
      reviewedHeats[i]
    ));
  }

  currentCorrections = responseJson.corrections.corrections;
  renderCorrections();
}

/**
 * Create a table row for a single heat showing parsed, cleaned, and reviewed data
 */
function createHeatRow(parsedHeat, cleanedHeat, reviewedHeat) {
  const template = document.getElementById('heat-row-template');
  const clone = template.content.cloneNode(true);

  // Set heat name
  let heatName = "";
  if (reviewedHeat) {
    heatName = `${reviewedHeat.gender} ${reviewedHeat.class} ${reviewedHeat.varsity_index}`;
  } else if (cleanedHeat) {
    heatName = `${cleanedHeat.gender} ${cleanedHeat.class} ${cleanedHeat.varsity_index}`;
  } else {
    heatName = `${parsedHeat.gender} ${parsedHeat.class} ${parsedHeat.varsity_index}`;
  }
  clone.querySelector('.heat-name-cell').textContent = heatName;

  // Populate parsed column
  const parsedTable = clone.querySelector('.parsed-cell .results-table');
  populateResultsTable(parsedTable, parsedHeat);

  // Populate cleaned column
  const cleanedTable = clone.querySelector('.cleaned-cell .results-table');
  if (cleanedTable) {
    populateResultsTable(cleanedTable, cleanedHeat);
  } else {
    cleanedTable.textContent = '(not present)';
    cleanedTable.style.color = '#999';
  }

  // Populate reviewed column
  const reviewedTable = clone.querySelector('.reviewed-cell .results-table');
  if (reviewedHeat) {
    populateResultsTable(reviewedTable, reviewedHeat);
  } else {
    reviewedTable.textContent = '(not present)';
    reviewedTable.style.color = '#999';
  }

  return clone;
}

/**
 * Populate a results table with heat data
 */
function populateResultsTable(tableElement, heat) {
  if (!heat || !heat.results) {
    tableElement.textContent = '(no data)';
    tableElement.style.color = '#999';
    return;
  }

  const longestSchoolNameLength = Math.max(...heat.results.map(result => result.school.length));

  for (let i = 0; i < heat.results.length; i++) {
    const result = heat.results[i];
    const schoolName = result.school.padEnd(Math.max(15, longestSchoolNameLength + 2), ' ');
    const time = (result.raw_time || '').padEnd(8, ' ');
    const margin = result.margin_from_winner != null && result.margin_from_winner > 0
      ? `+${result.margin_from_winner.toFixed(1)}`
      : '';

    const line = document.createElement('div');
    line.className = 'result-row';
    line.textContent = `${schoolName}${time}`;
    tableElement.appendChild(line);
  }
}

function createCorrection(correction, index) {
  const div = document.createElement('div');
  div.className = 'correction-item';

  const header = document.createElement('div');
  header.className = 'correction-header';

  const typeLabel = document.createElement('span');
  typeLabel.className = 'correction-type';
  typeLabel.textContent = formatCorrectionType(correction.type);

  const actions = document.createElement('div');
  actions.className = 'correction-actions';

  const editBtn = document.createElement('button');
  editBtn.textContent = 'Edit';
  editBtn.className = 'btn-small';
  editBtn.onclick = () => editCorrection(index, correction);

  const deleteBtn = document.createElement('button');
  deleteBtn.textContent = 'Delete';
  deleteBtn.className = 'btn-small btn-danger';
  deleteBtn.onclick = () => deleteCorrection(index);

  actions.appendChild(editBtn);
  actions.appendChild(deleteBtn);

  header.appendChild(typeLabel);
  header.appendChild(actions);

  const details = document.createElement('div');
  details.className = 'correction-details';
  details.appendChild(formatCorrectionDetails(correction));

  div.appendChild(header);
  div.appendChild(details);

  return div;
}

function formatCorrectionDetails(correction) {
  const container = document.createElement('div');

  switch(correction.type) {
    case 'comment':
      const comment = document.createElement('p');
      comment.textContent = correction.comment;
      comment.className = 'correction-comment';
      container.appendChild(comment);
      break;

    case 'set_class_all_heats':
      const classText = document.createElement('p');
      classText.textContent = `Set all heats to: ${correction.class}`;
      container.appendChild(classText);
      break;

    case 'set_gender_all_heats':
      const genderText = document.createElement('p');
      genderText.textContent = `Set all heats to: ${correction.gender}`;
      container.appendChild(genderText);
      break;

    case 'ignore_heats':
      const ignoreText = document.createElement('p');
      ignoreText.textContent = 'Ignore heats:';
      const heatList = document.createElement('ul');
      correction.heats.forEach(heat => {
        const li = document.createElement('li');
        li.textContent = heat;
        heatList.appendChild(li);
      });
      container.appendChild(ignoreText);
      container.appendChild(heatList);
      break;

    case 'exclude_schools_from_heat':
      const excludeText = document.createElement('p');
      excludeText.textContent = `Exclude from heat "${correction.heat}":`;
      const schoolList = document.createElement('ul');
      correction.schools.forEach(school => {
        const li = document.createElement('li');
        li.textContent = school;
        schoolList.appendChild(li);
      });
      container.appendChild(excludeText);
      container.appendChild(schoolList);
      break;

    case 'set_margins':
      const marginText = document.createElement('p');
      marginText.textContent = `Set margins for heat "${correction.heat}":`;
      const marginList = document.createElement('ul');
      correction.margins.forEach(margin => {
        const li = document.createElement('li');
        li.textContent = `${margin.school}: ${margin.margin_from_winner}s`;
        marginList.appendChild(li);
      });
      container.appendChild(marginText);
      container.appendChild(marginList);
      break;

    case 'manual_override':
      const overrideText = document.createElement('p');
      overrideText.textContent = 'Manual override of entire race data';
      overrideText.className = 'warning-text';
      container.appendChild(overrideText);
      break;

    default:
      const unknownText = document.createElement('pre');
      unknownText.textContent = JSON.stringify(correction, null, 2);
      container.appendChild(unknownText);
  }

  return container;
}

function formatCorrectionType(type) {
  return type
    .split('_')
    .map(word => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ');
}

function renderCorrections() {
  const correctionsContainer = document.getElementById('corrections-container');
  correctionsContainer.innerHTML = '';

  currentCorrections.forEach((correction, index) => {
    correctionsContainer.appendChild(createCorrection(correction, index));
  });

  // Add "Add Correction" button
  const addButton = document.createElement('button');
  addButton.textContent = '+ Add Correction';
  addButton.className = 'btn-primary';
  addButton.onclick = () => openCorrectionModal();
  correctionsContainer.appendChild(addButton);

  // Add "Apply Corrections" button
  const applyButton = document.createElement('button');
  applyButton.textContent = 'Apply Corrections';
  applyButton.className = 'btn-primary';
  applyButton.onclick = () => alert("Apply Corrections");
  correctionsContainer.appendChild(applyButton);
}

function editCorrection(index, correction) {
  openCorrectionModal(index, correction);
}

function deleteCorrection(index) {
  if (confirm('Are you sure you want to delete this correction?')) {
    currentCorrections.splice(index, 1);
    renderCorrections();
    // TODO: Save to backend
    console.log('Correction deleted (not yet saved to backend)');
  }
}

function addNewCorrection() {
  openCorrectionModal();
}

function openCorrectionModal(index = null, correction = null) {
  const isEdit = index !== null;
  const modal = document.createElement('div');
  modal.className = 'modal-overlay';
  modal.onclick = (e) => {
    if (e.target === modal) closeModal();
  };

  const modalContent = document.createElement('div');
  modalContent.className = 'modal-content';

  const header = document.createElement('h3');
  header.textContent = isEdit ? 'Edit Correction' : 'Add Correction';
  modalContent.appendChild(header);

  const form = document.createElement('form');
  form.onsubmit = (e) => {
    e.preventDefault();
    saveCorrectionFromForm(form, index);
  };

  // Correction type selector
  const typeGroup = document.createElement('div');
  typeGroup.className = 'form-group';
  const typeLabel = document.createElement('label');
  typeLabel.textContent = 'Correction Type:';
  const typeSelect = document.createElement('select');
  typeSelect.name = 'type';
  typeSelect.required = true;

  const types = [
    'comment',
    'set_class_all_heats',
    'set_gender_all_heats',
    'ignore_heats',
    'exclude_schools_from_heat',
    'set_margins',
    'manual_override'
  ];

  types.forEach(type => {
    const option = document.createElement('option');
    option.value = type;
    option.textContent = formatCorrectionType(type);
    if (correction && correction.type === type) {
      option.selected = true;
    }
    typeSelect.appendChild(option);
  });

  typeSelect.onchange = () => {
    updateFormFields(form, typeSelect.value, correction);
  };

  typeGroup.appendChild(typeLabel);
  typeGroup.appendChild(typeSelect);
  form.appendChild(typeGroup);

  // Dynamic fields container
  const fieldsContainer = document.createElement('div');
  fieldsContainer.id = 'dynamic-fields';
  form.appendChild(fieldsContainer);

  // Buttons
  const buttonGroup = document.createElement('div');
  buttonGroup.className = 'modal-buttons';

  const saveBtn = document.createElement('button');
  saveBtn.type = 'submit';
  saveBtn.textContent = 'Save';
  saveBtn.className = 'btn-primary';

  const cancelBtn = document.createElement('button');
  cancelBtn.type = 'button';
  cancelBtn.textContent = 'Cancel';
  cancelBtn.className = 'btn-small';
  cancelBtn.onclick = closeModal;

  buttonGroup.appendChild(saveBtn);
  buttonGroup.appendChild(cancelBtn);
  form.appendChild(buttonGroup);

  modalContent.appendChild(form);
  modal.appendChild(modalContent);
  document.body.appendChild(modal);

  // Initialize form fields
  updateFormFields(form, correction ? correction.type : types[0], correction);
}

function updateFormFields(form, type, correction) {
  const container = form.querySelector('#dynamic-fields');
  container.innerHTML = '';

  switch(type) {
    case 'comment':
      const commentGroup = createFormGroup('Comment:', 'textarea', 'comment', correction?.comment || '');
      container.appendChild(commentGroup);
      break;

    case 'set_class_all_heats':
      const classGroup = createFormGroup('Class:', 'select', 'class', correction?.class || 'eights', ['eights', 'fours']);
      container.appendChild(classGroup);
      break;

    case 'set_gender_all_heats':
      const genderGroup = createFormGroup('Gender:', 'select', 'gender', correction?.gender || 'boys', ['boys', 'girls']);
      container.appendChild(genderGroup);
      break;

    case 'ignore_heats':
      const heatsGroup = createFormGroup('Heats (one per line, e.g., "boys 1"):', 'textarea', 'heats',
        correction?.heats ? correction.heats.join('\n') : '');
      container.appendChild(heatsGroup);
      break;

    case 'exclude_schools_from_heat':
      const heatGroup = createFormGroup('Heat (e.g., "boys 1"):', 'text', 'heat', correction?.heat || '');
      const schoolsGroup = createFormGroup('Schools (one per line):', 'textarea', 'schools',
        correction?.schools ? correction.schools.join('\n') : '');
      container.appendChild(heatGroup);
      container.appendChild(schoolsGroup);
      break;

    case 'set_margins':
      const setMarginHeatGroup = createFormGroup('Heat (e.g., "boys 1"):', 'text', 'heat', correction?.heat || '');
      const marginsGroup = createFormGroup('Margins (JSON format):', 'textarea', 'margins',
        correction?.margins ? JSON.stringify(correction.margins, null, 2) : '[]');
      container.appendChild(setMarginHeatGroup);
      container.appendChild(marginsGroup);
      break;

    case 'manual_override':
      const overrideGroup = createFormGroup('New Contents (JSON format):', 'textarea', 'new_contents',
        correction?.new_contents ? JSON.stringify(correction.new_contents, null, 2) : '{}');
      container.appendChild(overrideGroup);
      break;
  }
}

function createFormGroup(labelText, inputType, name, value = '', options = null) {
  const group = document.createElement('div');
  group.className = 'form-group';

  const label = document.createElement('label');
  label.textContent = labelText;
  group.appendChild(label);

  let input;
  if (inputType === 'select') {
    input = document.createElement('select');
    input.name = name;
    input.required = true;
    options.forEach(opt => {
      const option = document.createElement('option');
      option.value = opt;
      option.textContent = opt;
      if (opt === value) option.selected = true;
      input.appendChild(option);
    });
  } else if (inputType === 'textarea') {
    input = document.createElement('textarea');
    input.name = name;
    input.value = value;
    input.rows = 4;
  } else {
    input = document.createElement('input');
    input.type = inputType;
    input.name = name;
    input.value = value;
  }

  group.appendChild(input);
  return group;
}

function saveCorrectionFromForm(form, index) {
  const formData = new FormData(form);
  const type = formData.get('type');

  const correction = { type };

  switch(type) {
    case 'comment':
      correction.comment = formData.get('comment');
      break;

    case 'set_class_all_heats':
      correction.class = formData.get('class');
      break;

    case 'set_gender_all_heats':
      correction.gender = formData.get('gender');
      break;

    case 'ignore_heats':
      correction.heats = formData.get('heats').split('\n').map(s => s.trim()).filter(s => s);
      break;

    case 'exclude_schools_from_heat':
      correction.heat = formData.get('heat');
      correction.schools = formData.get('schools').split('\n').map(s => s.trim()).filter(s => s);
      break;

    case 'set_margins':
      correction.heat = formData.get('heat');
      try {
        correction.margins = JSON.parse(formData.get('margins'));
      } catch (e) {
        alert('Invalid JSON for margins');
        return;
      }
      break;

    case 'manual_override':
      try {
        correction.new_contents = JSON.parse(formData.get('new_contents'));
      } catch (e) {
        alert('Invalid JSON for new contents');
        return;
      }
      break;
  }

  if (index !== null) {
    currentCorrections[index] = correction;
  } else {
    currentCorrections.push(correction);
  }

  renderCorrections();
  closeModal();

  // TODO: Save to backend
  console.log('Correction saved (not yet saved to backend):', correction);
}

function closeModal() {
  const modal = document.querySelector('.modal-overlay');
  if (modal) {
    modal.remove();
  }
}

document.addEventListener('DOMContentLoaded', init);
// Initialize when DOM is ready
// if (document.readyState === 'loading') {
//   document.addEventListener('DOMContentLoaded', init);
// } else {
//   console.log(document.readyState);
//   init();
// }
