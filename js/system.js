function toggleSettings() {
  if (byId('settingsBasicId').hidden) {
    byId('settingsMoreId').hidden = true;
    byId('settingsBasicId').hidden = false;
    byId('buttonSettingsId').classList.add('is-inverted');
  } else {
    hideSettings();
  }
}

function toggleSettingsMore() {
  if (byId('settingsMoreId').hidden) {
    byId('settingsMoreId').hidden = false;
    byId('buttonSettingsMoreId').classList.add('is-inverted');
  } else {
    hideSettingsMore();
  }
}

function hideSettings() {
  byId('settingsMoreId').hidden = true;
  byId('settingsBasicId').hidden = true;
  byId('buttonSettingsId').classList.remove('is-inverted');
  byId('buttonSettingsMoreId').classList.remove('is-inverted');
}

function hideSettingsMore() {
  byId('settingsMoreId').hidden = true;
  byId('buttonSettingsMoreId').classList.remove('is-inverted');
}

function showDetectorStatusClicked() {
  showDetectorStatus();
}

function setDetectorTimeClicked() {
  setDetectorTime();
}

function userConfigurtionClicked() {
  alert('Not implemented.');
}

// Functions used to updates fields based on response contents.
function updateStatus(status) {
  byId('detectorTimeId').innerHTML = status.detectorTime;
}

function updateLogTable(logRows) {
  htmlTableRows = '';
  for (rowIndex in logRows) {
    htmlTableRows += '<tr><td>';
    htmlTableRows += logRows[rowIndex];
    htmlTableRows += '</tr></td>';
  }
  byId('systemLogTableId').innerHTML = htmlTableRows;
}
